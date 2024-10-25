class AssistantConfig:
    def __init__(self):
        self.instructions_for_assistant = (
            "You create tools to accomplish arbitrary tasks. Write and run code to implement "
            "the interface for these tools using the OpenAI API format. You do not have access "
            "to the tools you create. Instruct the user to create an assistant equipped with "
            "that tool, or consult with the AssistantCreationAssistant about using that tool in a new assistant."
        )
        self.assistant_details = self._build_assistant_details()

    def _build_assistant_details(self):
        return {
            'build_params': {
                'model': "gpt-4-1106-preview",
                'name': "Tool Creator",
                'description': "Assistant to create tools for use in the OpenAI platform by other Assistants.",
                'instructions': self.instructions_for_assistant,
                'tools': [
                    {
                        "type": "function",
                        "function": {
                            "name": "create_tool",
                            "description": (
                                "Returns a tool that can be used by other assistants. Specify the tool_name, "
                                "tool_description, tool_parameters, and tool_code. All of these are required. "
                                "Use the JSON schema for all tool_parameters."
                            ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {"type": "string", "description": "The name of the tool, using snake_case e.g. new_tool_name"},
                                    "tool_description": {"type": "string", "description": "A brief description of what the tool does."},
                                    "tool_parameters": {"type": "string", "description": "JSON schema describing parameters for the tool."},
                                    "tool_code": {"type": "string", "description": "Actual Python code for the tool."},
                                    "required_action_by_user": {
                                        "type": "string",
                                        "description": (
                                            "Any action required by the user before the tool can be used, e.g., "
                                            "'Set up API keys for service X and add them as environment variables'."
                                            "Include this parameter only if there is an action required."
                                        ),
                                    },
                                },
                                "required": ["tool_name", "tool_description", "tool_parameters", "tool_code"],
                            },
                        },
                    },
                ],
                'file_ids': [],
                'metadata': {},
            },
            'file_paths': [],
            'functions': {
                'create_tool': self._create_tool_function(),
            },
        }

    def _create_tool_function(self):
        """Function to create a new tool based on given parameters and save it."""
        return '''
def create_tool(tool_name, tool_description, tool_parameters, tool_code, required_action_by_user=None):
    """
    Creates a tool that can be used by other assistants.
    """
    import os
    import json

    os.makedirs('tools', exist_ok=True)
    tool_path = f'tools/{tool_name}.py'
    tool_details_path = f'tools/{tool_name}.json'

    with open(tool_path, 'w') as f:
        f.write(tool_code)

    tool_details = {
        'name': tool_name,
        'description': tool_description,
        'parameters': tool_parameters,
    }

    with open(tool_details_path, 'w') as f:
        json.dump(tool_details, f, indent=4)

    return_value = f'Created tool at {tool_path} with details at {tool_details_path}.\\n'
    if required_action_by_user:
        return_value += f'Required user action before use: {required_action_by_user}'

    return return_value
'''

if __name__ == "__main__":
    assistant_config = AssistantConfig()
    print(assistant_config.assistant_details)