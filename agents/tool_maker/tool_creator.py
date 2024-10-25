"""
Create a tool-creator assistant using the assistant creation API.
"""

import json
import os

from shared.utils import chat as chat_loop
from shared.openai_config import get_openai_client

client = get_openai_client()

def create_tool_creator(assistant_details):
    """
    Creates an assistant using provided details and saves its configuration.
    """
    tool_creator = client.beta.assistants.create(**assistant_details["build_params"])
    print(f"Created assistant to create tools: {tool_creator.id}\n\n" + 90 * "-" + "\n\n")

    info_to_export = {
        "assistant_id": tool_creator.id,
        "assistant_details": assistant_details,
    }
    os.makedirs('assistants', exist_ok=True)
    with open('assistants/tool_creator.json', 'w') as f:
        json.dump(info_to_export, f, indent=4)

    return tool_creator

def talk_to_tool_creator(assistant_details):
    """
    Initiates a conversation with the assistant to manage tool creation, checking for
    existing configurations and offering to create new if required.
    """
    try:
        os.makedirs('assistants', exist_ok=True)
        with open('assistants/tool_creator.json', 'r') as f:
            create_new = input('Assistant details found in tool_creator.json. Create a new assistant? [y/N] ')
            if create_new.lower() == 'y':
                raise Exception("User wants a new assistant")
            assistant_from_json = json.load(f)
            tool_creator = client.beta.assistants.retrieve(assistant_from_json['assistant_id'])
            print(r"Loaded assistant details from tool_creator.json\n\n" + 90 * "-" + "\n\n")
            print(f'Assistant {tool_creator.id}:\n')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        tool_creator = create_tool_creator(assistant_details)

    functions = assistant_details["functions"]

    thread = client.beta.threads.create()
    chat_loop(client, thread.id, tool_creator, functions)

if __name__ == "__main__":
    from creator_config import AssistantConfig

    assistant_config = AssistantConfig()
    talk_to_tool_creator(assistant_config.assistant_details)