# MISSION AND INSTRUCTIONS

* You are a boss agent in charge of three worker agents.
* You'll be handed a project to work on and are expected to delegate on the workers.
* Send tasks to the workers one a time. They will collaborate on the tasks you provide and get back to you.
* Wait for a worker response before sending another task.
* Once you're satisfied with the information received from the workers, put it together and send the final result back to the user.
* Complete the task in your mission.
* To talk to other agents call the function 'assign_task'. At the beginning of the message identify yourself.
from agents.tool_maker.tool_manager import ToolManager
import os
import json
from pathlib import Path  # Import Path from pathlib
from agents.agent_builder.create import AgentBuilder

class AssistantManager:
    def __init__(self, client):
        self.client = client
        self.assistant = None
        self.agent_builder = AgentBuilder(client=self.client)
        self.base_path = Path(__file__).absolute().parent
        tools_path = os.path.join(self.base_path, "tool_creator_metadata.json")
        try:
            with open(tools_path, "r") as file:
                self.assistant_package = json.load(file)
        except FileNotFoundError:
            raise Exception("tool_creator_metadata.json not found in the expected directory.")

    def get_assistant(self, assistant_type="creator"):
        """Retrieve or create an assistant based on the specified type."""
        name = self.assistant_package.get(assistant_type, {}).get("name")
        if not name:
            raise ValueError(f"No name found for assistant type '{assistant_type}' in the metadata.")

        self.agent_builder.create_assistant(name)
        assistants = self.client.beta.assistants.list()
        assistant_names = [assistant.name for assistant in assistants]

        if name not in assistant_names:
            raise ValueError(f"{name} needs to be created using create.py in /agents/agent_builder/")

        assistant_dict = {assistant.name: assistant.id for assistant in assistants}
        assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_dict[name])
        self.assistant = assistant
        return assistant

if __name__ == "__main__":
    from shared.openai_config import get_openai_client
    client = get_openai_client()
    assistant_manager = AssistantManager(client=client)
    assistant = assistant_manager.get_assistant()
    print(assistant)
 Agents: { talksTo }

* Agents: { talksTo }
