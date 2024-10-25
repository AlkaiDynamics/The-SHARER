import yaml
import os
import threading
import dotenv
import argparse
import sys
import pathlib
from openai import OpenAI

from context import Context
from agent import Agent
from agentProcessor import AgentProcessor
from function_manager import FunctionManager
from template_manager import TemplateManager
from OAIWrapper import OAIWrapper
import agentEnvHandler
# Assuming network is defined in a module named network_module
from network_module import network

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise EnvironmentError('The OPENAI_API_KEY environment variable is not set.')

client = OpenAI(api_key=api_key)

# Setup argument parser
parser = argparse.ArgumentParser(description='Load agents configuration from its configuration folder.')
parser.add_argument('--agents-definition-folder', dest='agentsDefinitionFolder', required=True,
                    help='Path to the agents definition folder. Should contain an "agents.yaml" file')

args = parser.parse_args()

# Construct the path to the agents.yaml file
workDir = pathlib.Path(__file__).parent.resolve()
agentsDefinitionDir = os.path.join(workDir, args.agentsDefinitionFolder)
agentsYAML = os.path.join(agentsDefinitionDir, "agents.yaml")

# Validate the configuration file's existence
if not os.path.isfile(agentsYAML):
    sys.exit(f"Error: The file {agentsYAML} does not exist.")

# Load agents from configuration
with open(agentsYAML, 'r') as stream:
    agentsProperties = yaml.safe_load(stream)
    agents = [Agent(properties) for properties in agentsProperties]

ctx = Context(client, agents)

# Load or initialize agent IDs
agentsIdsFile = os.path.join(agentsDefinitionDir, "agentsIds.env")
with open(agentsIdsFile, 'a+'):
    pass  # Ensure the file exists

with open(agentsIdsFile, 'r') as stream:
    agentsIds = yaml.safe_load(stream) or {}
    for properties in agentsIds:
        for agent in agents:
            if agent.name == properties['name'] and 'id' not in agent:
                agent.id = properties['id']

print(f"Agents loaded: {[agent.name for agent in agents]}")

function_manager = FunctionManager()
template_manager = TemplateManager([agentsDefinitionDir])
function_manager.load_functions()
template_manager.load_templates()

# Process each agent
for agent in agents:
    oai_wrapper = OAIWrapper(client, agent, function_manager, template_manager)
    agent_update_required = not hasattr(agent, 'id')
    oai_wrapper.createAssistant() if agent_update_required else oai_wrapper.updateAssistant()
    if agent_update_required:
        agentEnvHandler.saveId(agentsIdsFile, agent)

network.build(ctx)

# Start processing threads for each agent
threads = []
for agent in agents:
    processor = AgentProcessor(function_manager)
    thread = threading.Thread(target=processor.processThread, args=(ctx, agent,))
    threads.append(thread)
    thread.start()

# Optionally wait for all threads to complete
for thread in threads:
    thread.join()

print("Initialization complete. All agents are running.")
