"""
Create an assistant using the tools from tool_creator using the assistant creation API.
"""

import os
import json
import sys
from importlib import util

from shared.utils import chat as chat_loop
from shared.openai_config import get_openai_client

client = get_openai_client()

def create_tool_user(assistant_details):
    """
    Creates an assistant with provided details and saves its configuration to a JSON file.
    """
    tool_user = client.beta.assistants.create(**assistant_details["build_params"])
    print(f"Created assistant {tool_user.id} to use tools\n\n" + 90 * "-" + "\n\n", flush=True)

    info_to_export = {
        "assistant_id": tool_user.id,
        "assistant_details": assistant_details,
    }
    os.makedirs('assistants', exist_ok=True)
    with open('assistants/tool_user.json', 'w') as f:
        json.dump(info_to_export, f, indent=4)
    return tool_user

def load_or_create_assistant(assistant_details):
    """
    Loads an assistant from a JSON file if available, otherwise creates a new one.
    """
    try:
        os.makedirs('assistants', exist_ok=True)
        with open('assistants/tool_user.json', 'r') as f:
            assistant_from_json = json.load(f)
            print("Loaded assistant details from tool_user.json\n" + "-" * 90 + "\n", flush=True)
            return assistant_from_json  # Return the loaded assistant details
    except (FileNotFoundError, KeyError):
        print("No existing assistant found or error in JSON. Creating new assistant.")
        return create_tool_user(assistant_details)

def load_functions(function_paths):
    """
    Dynamically loads and returns functions defined in external Python files using importlib.
    """
    loaded_functions = {}
    os.makedirs('tools', exist_ok=True)
    for func_name, path in function_paths.items():
        try:
            spec = util.spec_from_file_location(func_name, path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded_functions[func_name] = getattr(module, func_name)
        except Exception as e:
            print(f"Failed to load function {func_name} from {path}: {e}", flush=True)
    return loaded_functions

def talk_to_tool_user(assistant_details):
    """
    Interacts with the tool user assistant using the loaded or created assistant and tools.
    """
    tool_user = load_or_create_assistant(assistant_details)
    function_paths = {func: f"tools/{func}.py" for func in assistant_details["functions"].keys()}
    functions = load_functions(function_paths)

    # Create thread
    thread = client.beta.threads.create()

    # Chat with the assistant
    chat_loop(client, thread, tool_user, functions)

if __name__ == "__main__":
    assistant_details = {"build_params": {...}}  # Load or define your assistant details here
    try:
        talk_to_tool_user(assistant_details)
    except KeyboardInterrupt:
        print("Session interrupted by user.")
        sys.exit(1)
