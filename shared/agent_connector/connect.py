import yaml
import os
import queue as queueModule
import threading
import time
from shared.openai_config import get_openai_client

agents_path = 'agents'
client = get_openai_client()

# Get the directory name of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the agents.yaml file
yaml_file_path = os.path.join(script_dir, 'agents.yaml')

with open(yaml_file_path, 'r') as stream:
    agents = yaml.safe_load(stream)

def handle_agent_thread(agent, queues):
    """
    Handles messages for a single agent within a thread.
    Manages sending and receiving messages via OpenAI's API.
    """
    print(f"[{agent['name']}] Initialized with ID: {agent['id']}")

    thread = client.beta.threads.create()
    agent_queue = queues[agent['name']]
    sent_messages = set()

    while True:
        message = agent_queue.get(block=True)
        if message is not None:
            sent_messages.add(message)
            client.beta.threads.messages.create(thread_id=thread.id, content=message, role='user')
            run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=agent['id'])

        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == 'completed':
            process_completed_thread(run, agent, queues, sent_messages)

        time.sleep(1)

def process_completed_thread(run, agent, queues, sent_messages):
    """
    Processes messages from a completed thread, broadcasting to other agents if necessary.
    """
    message_list = client.beta.threads.messages.list(thread_id=run.thread_id)
    for datum in message_list.data:
        for content in datum.content:
            message_text = content.text.value
            if message_text not in sent_messages:
                sent_messages.add(message_text)
                print(f"[{agent['name']}] Message: {message_text}")
                if 'talksTo' in agent:
                    for downstream_agent in agent['talksTo']:
                        queues[downstream_agent].put(message_text)

def initialize_agent_threads(agents):
    """
    Initializes threads for all agents and returns the queues used for communication.
    """
    queues = {agent['name']: queueModule.Queue() for agent in agents}
    for agent in agents:
        threading.Thread(target=handle_agent_thread, args=(agent, queues)).start()
    return queues

# Main execution block
if __name__ == "__main__":
    agent_queues = initialize_agent_threads(agents)
    agent_queues['Uppercase'].put("Hello from the main thread!")
