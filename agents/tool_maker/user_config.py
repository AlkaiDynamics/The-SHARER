import json
import os
from typing import List, Optional

class AssistantConfig:
    def __init__(self, tools_to_use: Optional[List[str]] = None):
        self.tools_to_use = tools_to_use or []
        self.instructions_for_assistant = 'Use the tools to accomplish the task'
        self.files_for_assistant = []  # Local file paths
        self.assistant_details = self._build_assistant_details()

    def _build_assistant_details(self):
        assistant_details = {
            'build_params': {
                'model': "gpt-4-1106-preview",
                'name': "Tool User",
                'description': "Assistant to use tools made by the tool creator.",
                'instructions': self.instructions_for_assistant,
                'tools': [],
                'file_ids': [],
                'metadata': {},
            },
            'file_paths': self.files_for_assistant,
            'functions': {}
        }

        self._load_tools(assistant_details)
        return assistant_details

    def _load_tools(self, assistant_details: dict):
        # Ensure the tools directory exists
        tools_dir = 'tools'
        os.makedirs(tools_dir, exist_ok=True)

        if not self.tools_to_use:
            self.tools_to_use = [tool.split('.')[0] for tool in os.listdir(tools_dir) if tool.endswith('.json')]

        for tool in self.tools_to_use:
            self._add_tool_details(tool, assistant_details)

    def _add_tool_details(self, tool: str, assistant_details: dict):
        tool_json_path = f'tools/{tool}.json'
        tool_code_path = f'tools/{tool}.py'

        try:
            with open(tool_json_path) as f:
                tool_details = json.load(f)
            with open(tool_code_path) as f:
                tool_code = f.read()
        except FileNotFoundError:
            print(f"Error: File for tool '{tool}' not found.")
            return

        assistant_details['build_params']['tools'].append({
            "type": "function",
            "function": {
                "name": tool_details['name'],
                "description": tool_details['description'],
                "parameters": eval(tool_details['parameters']),  # Using eval here could be risky; consider safer alternatives
            }
        })
        assistant_details['functions'][tool_details['name']] = tool_code

if __name__ == '__main__':
    config = AssistantConfig()
    print(json.dumps(config.assistant_details, indent=2))
