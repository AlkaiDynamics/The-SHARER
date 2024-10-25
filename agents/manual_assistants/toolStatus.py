import json
from pathlib import Path
from shared.openai_config import get_openai_client

class AgentBuilder:
    def __init__(self, client):
        self.client = client
        self.agents_path = "agents"
        self.existing_assistants = self.load_existing_assistants()

    def load_existing_assistants(self):
        """Load existing assistants and cache their details."""
        return {assistant.name: assistant for assistant in self.client.beta.assistants.list(limit=100)}

    def handle_files(self, agent_folder):
        """Handle file operations for an agent's folder."""
        files_folder = Path(agent_folder) / 'files'
        if not files_folder.is_dir():
            raise FileNotFoundError(f"No 'files' directory found in {agent_folder}")
        
        existing_files = {file['name']: file for file in self.client.files.list()}
        new_files = [f for f in files_folder.iterdir() if f.is_file() and f.name not in existing_files]

        uploaded_files = []
        for file_path in new_files:
            with file_path.open('rb') as file_data:
                file_object = self.client.files.create(file=file_data, purpose='assistants')
                uploaded_files.append({"name": file_path.name, "id": file_object.id})
        return uploaded_files

    def update_assistant(self, assistant, updates):
        """Update assistant properties if there are any changes."""
        return self.client.beta.assistants.update(assistant_id=assistant.id, **updates)

    def create_or_update_assistant(self, agent_name):
        """Create or update an assistant based on the provided configuration."""
        agent_folder = Path(self.agents_path) / agent_name
        if not agent_folder.is_dir():
            raise FileNotFoundError(f'{agent_folder} is missing or not a directory.')

        settings_path = agent_folder / 'settings.json'
        with settings_path.open() as f:
            settings = json.load(f)

        instructions_path = agent_folder / "instructions.md"
        if instructions_path.is_file():
            with instructions_path.open() as f:
                instructions = f.read()

        files = self.handle_files(agent_folder)
        assistant = self.existing_assistants.get(agent_name)
        if assistant:
            updates = {}
            if assistant.model != settings["model"]:
                updates["model"] = settings["model"]
            if assistant.description != settings["description"]:
                updates["description"] = settings["description"]
            if 'instructions' in updates or files:
                updates['file_ids'] = [file['id'] for file in files]
                assistant = self.update_assistant(assistant, updates)
            return assistant
        else:
            assistant_data = {
                "name": agent_name,
                "instructions": instructions,
                "description": settings["description"],
                "model": settings["model"],
                "file_ids": [file['id'] for file in files]
            }
            return self.client.beta.assistants.create(**assistant_data)

    def __repr__(self):
        return f"<AgentBuilder client={self.client}>"

if __name__ == "__main__":
    client = get_openai_client()
    agent_builder = AgentBuilder(client=client)
    assistant = agent_builder.create_or_update_assistant('ExampleAssistant')
    print(assistant)
