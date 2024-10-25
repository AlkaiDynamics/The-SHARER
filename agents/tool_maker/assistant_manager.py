import json
import logging
from pathlib import Path

from agents.agent_builder.create import AgentBuilder

class AssistantManager:
    def __init__(self, client):
        self.client = client
        self.assistant = None
        self.agent_builder = AgentBuilder(client=client)
        self.base_path = Path(__file__).resolve().parent
        self.tools_path = self.base_path / "tool_creator_metadata.json"
        self.load_metadata()

    def load_metadata(self):
        """Load assistant metadata from a JSON file."""
        try:
            with open(self.tools_path, "r") as file:
                self.assistant_package = json.load(file)
        except FileNotFoundError as err:
            logging.error(f"{self.tools_path} not found in the expected directory.")
            raise FileNotFoundError(f"{self.tools_path} not found in the expected directory.") from err

    def get_assistant(self, assistant_type="creator"):
        """Retrieve or create an assistant based on the specified type."""
        name = self.assistant_package.get(assistant_type, {}).get("name")
        if not name:
            raise ValueError(
                f"No name found for assistant type '{assistant_type}' in the metadata."
            )
        self.agent_builder.create_assistant(name)
        assistant = self.client.beta.assistants.retrieve(assistant_id=self.get_assistant_id(name))
        return assistant

    def get_assistant_id(self, name):
        """Helper method to get assistant ID by name."""
        assistants = self.client.beta.assistants.list()
        for assistant in assistants:
            if assistant.name == name:
                return assistant.id
        raise ValueError(f"Assistant with name '{name}' does not exist.")

if __name__ == "__main__":
    from shared.openai_config import get_openai_client

    logging.basicConfig(level=logging.INFO)
    client = get_openai_client()
    assistant_manager = AssistantManager(client=client)
    assistant = assistant_manager.get_assistant()
    print(assistant)