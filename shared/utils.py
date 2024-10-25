import time
import json

def chat(client, thread, assistant, functions):
    while True:
        try:
            user_message = input("You: ")
            if not user_message.strip():
                print("No input detected. Please type a message.")
                continue

            # Adding user message to thread
            client.beta.threads.messages.create(thread.id, role="user", content=user_message)

            # Initiating assistant response
            run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

            # Polling for run completion
            while run.status not in ["completed", "failed"]:
                print("Waiting for run to complete...", flush=True)
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status == "failed":
                print(f"Run failed with error: {run.error}")
                break

            if run.status == "completed":
                # Handling tool outputs if required
                if run.requires_action and run.required_action.type == 'submit_tool_outputs':
                    submit_tool_outputs(run, client, thread, functions)

                # Displaying assistant response
                assistant_response = get_latest_message(client, thread)
                print(f"\n\nBot: {assistant_response}\n\n", flush=True)
                input("Press enter to continue chatting, or ctrl+c to stop chat\n")

        except KeyboardInterrupt:
            print("Chat stopped by user.\n" + 90 * "-" + "\n\n")
            break

def submit_tool_outputs(run, client, thread, functions):
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []
    for tc in tool_calls:
        function_to_call = functions.get(tc.function.name)
        if function_to_call:
            function_args = json.loads(tc.function.arguments)
            function_response = function_to_call(**function_args)
            tool_outputs.append({
                "tool_call_id": tc.id,
                "output": json.dumps(function_response),
            })
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )
    print("Tool outputs submitted.", flush=True)

def get_latest_message(client, thread):
    thread_messages = client.beta.threads.messages.list(thread.id, limit=1, order='desc')
    return thread_messages.data[0].content[0].text.value
