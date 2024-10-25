import importlib
import json
import os
from pathlib import Path
from openai import OpenAI
from path.to.tool_manager import ToolManager  # Assuming ToolManager is defined in 'path.to.tool_manager'

# Define custom types for better code readability.
Assistant = type(OpenAI().beta.assistants.list().data[0])
Thread = type(OpenAI().beta.threads.create())


class ChatManager:
    def __init__(self, client: OpenAI):
        self.client = client
        self.functions_path = Path(__file__).absolute().parent / "python_functions"
        print(f"Functions path: {self.functions_path}")

    def create_thread_from_user_input(self):
        user_input = input("Begin:\n")
        return self.client.beta.threads.create(messages=[{"role": "user", "content": user_input}])

    def create_empty_thread(self):
        return self.client.beta.threads.create()

    def run_python_from_function_name(self, call):
        print("CALLING FUNCTION")
        base = ".".join(__name__.split(".")[:-1])
        module_path = f"{base}.python_functions.{call.function.name}"
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            function = getattr(module, call.function.name)
            print(function)
            arguments = json.loads(call.function.arguments)
            result = function(**arguments)
            response = {"tool_call_id": call.id, "output": f"result: {result}"}
        except Exception as error:
            response = {"tool_call_id": call.id, "output": f"{{Exception: {error}}}"}
        print(response)
        return response

    def get_existing_functions(self):
        print("Retrieving Built Functions")
        results = []
        if os.path.exists(self.functions_path):
            for filename in os.listdir(self.functions_path):
                if filename.endswith(".json"):
                    with open(self.functions_path / filename, "r") as file:
                        results.append(json.load(file))
        return results

    def handle_function_request(self, call, interface_assistant: Assistant, interface_thread: Thread,
                                functional_assistant: Assistant, functional_thread: Thread):
        try:
            schema = ToolManager.schema_from_response(call.function.arguments)
            tool = ToolManager.tool_from_function_schema(schema)
            existing_tools = filter(lambda x: x.type == "function", interface_assistant.tools)
            if tool["function"]["name"] not in [t.function.name for t in existing_tools]:
                updated_tools = [*interface_assistant.tools, tool]
                interface_assistant = self.client.beta.assistants.update(
                    assistant_id=interface_assistant.id, tools=updated_tools)

            self.client.beta.threads.messages.create(thread_id=functional_thread.id, content=str(tool), role="user")
            functional_run = self.client.beta.threads.runs.create(
                thread_id=functional_thread.id, assistant_id=functional_assistant.id)
            functional_response = self.simple_run(run=functional_run, thread=functional_thread)

            function_lines = functional_response.split("```python")[1].split("```")[0]
            file_path = self.functions_path / f"{tool['function']['name']}.py"
            with open(file_path, "w") as file:
                file.write(function_lines)

            response = {"tool_call_id": call.id, "output": "success"}

        except Exception as error:
            response = {"tool_call_id": call.id, "output": f"{{Exception: {error}}}"}

        return interface_assistant, response

    def simple_run(self, run, thread):
        """Execute a function call and handle the response."""
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
            if run.status == "requires_action":
                responses = [self.process_call(call) for call in run.required_action.submit_tool_outputs.tool_calls]
                run = self.client.beta.threads.runs.submit_tool_outputs(run_id=run.id, thread_id=thread.id, tool_outputs=responses)

        response = next((msg.content for msg in self.client.beta.threads.messages.list(thread_id=thread.id).data if msg.role == "system"), "")
        return response

    def process_call(self, call):
        """Process individual function calls during execution."""
        if call.function.name == "get_existing_functions":
            available_functions = self.get_existing_functions()
            return {"tool_call_id": call.id, "output": f"result: {available_functions}"}
        return {"tool_call_id": call.id, "output": "result: None"}

    def run_unit(self, interface_assistant: Assistant, interface_thread: Thread,
                 functional_assistant: Assistant, functional_thread: Thread):
        user_input = input("Type command: ")
        self.client.beta.threads.messages.create(thread_id=interface_thread.id, content=user_input, role="user")
        interface_run = self.client.beta.threads.runs.create(
            thread_id=interface_thread.id, assistant_id=interface_assistant.id,
            instructions="Please minimize output text tokens for cost efficiency.")
        interface_assistant, response = self.begin_run(
            run=interface_run, interface_assistant=interface_assistant,
            interface_thread=interface_thread, functional_assistant=functional_assistant,
            functional_thread=functional_thread)
        print(response)
