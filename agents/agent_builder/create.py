import os
import json
from pathlib import Path
from shared.openai_config import get_openai_client

class AgentBuilder:

    def __init__(self, client):
        self.client = client
        self.existing_assistants = {}
        self.agents_path = "agents"
    def get_existing_assistants(self):
        if not self.existing_assistants:
            for assistant in self.client.beta.assistants.list(limit=100):
                self.existing_assistants[assistant.name] = assistant

    def handle_files(self, agent_folder, existing_files):
        files_folder = os.path.join(agent_folder, 'files')
        if not os.path.isdir(files_folder):
            raise FileNotFoundError(f"No 'files' directory found in {agent_folder}")
        requested_files = {filename for filename in os.listdir(files_folder) if os.path.isfile(os.path.join(files_folder, filename))}
        new_files = requested_files - existing_files.keys()
        uploaded_files = []
        for filename in new_files:
            file_path = os.path.join(files_folder, filename)
            with open(file_path, 'rb') as file_data:
                file_object = self.client.files.create(file=file_data, purpose='assistants')
                uploaded_files.append({"name": filename, "id": file_object.id})
        return uploaded_files

    def check_for_updates(self, existing_agent, settings, instructions, uploaded_files):
        update_params = {}
        if existing_agent.model != settings["model"]:
            update_params["model"] = settings["model"]
        if existing_agent.description != settings["description"]:
            update_params["description"] = settings["description"]
        if existing_agent.instructions != instructions:
            update_params["instructions"] = instructions
        if uploaded_files:
            update_params['file_ids'] = [file['id'] for file in uploaded_files]
        return update_params

    def create_assistant(self, agent_name):
        current_file_path = Path(__file__).absolute().parent
        agent_folder = os.path.join(current_file_path, self.agents_path, agent_name)

        if not os.path.exists(agent_folder) or not os.path.isdir(agent_folder):
            raise FileNotFoundError(f'{agent_folder} is missing or not a directory.')

        print(agent_folder)
        existing_files = {}
        existing_agent = {}
        self.get_existing_assistants()
        if agent_name in self.existing_assistants:
            existing_agent = self.existing_assistants[agent_name]
            for file_id in existing_agent.file_ids:
                existing_file = self.client.files.retrieve(file_id=file_id)
                existing_files[existing_file.filename] = existing_file

        instructions = ""
        instructions_file_path = os.path.join(agent_folder, "instructions.md")
        if os.path.isfile(instructions_file_path):
            with open(instructions_file_path, 'r') as f:
                instructions = f.read()

        settings = {}
        settings_file_path = os.path.join(agent_folder, 'settings.json')
        if os.path.isfile(settings_file_path):
            with open(settings_file_path, 'r') as f:
                settings = json.load(f)

        uploaded_files = self.handle_files(agent_folder, existing_files)

        print(agent_name)
        print("")
        print(instructions)
        if uploaded_files:
            print("")
            print(f"Files: {list(map(lambda x: x['name'], uploaded_files))}")

        if existing_agent:
            print(f"{agent_name} already exists... validating properties")
            update_params = self.check_for_updates(existing_agent, settings, instructions, uploaded_files)
            if update_params:
                print(f"Updating {agent_name}'s { ','.join(update_params.keys()) }")
                update_params['assistant_id'] = existing_agent.id
                assistant = self.client.beta.assistants.update(**update_params)
            else:
                print(f"{agent_name} is up to date")
        else:
            create_params = {
                "name": agent_name,
                "instructions": instructions,
                "description": settings["description"],
                "model": settings["model"],
                "tools": settings["tools"]
            }
            if uploaded_files:
                create_params['file_ids'] = [file['id'] for file in uploaded_files]
        assistant = self.client.beta.assistants.create(**create_params)
        print(f"Created assistant: {assistant.name}, ID: {assistant.id}")
        print("***********************************************")

    def create_assistants(self):
        agents_path = os.path.join(
            Path(__file__).absolute().parent, self.agents_path
        )

        if not os.path.exists(agents_path) or not os.path.isdir(agents_path):
            raise FileNotFoundError(f'The "{self.agents_path}" folder is missing or not a directory.')

        self.get_existing_assistants()

        for agent_name in os.listdir(agents_path):
            self.create_assistant(agent_name)

if __name__ == '__main__':
    client = get_openai_client()
    agent_builder = AgentBuilder(client=client)
    agent_builder.create_assistants()
