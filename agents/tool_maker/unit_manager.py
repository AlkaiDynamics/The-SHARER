from agents.tool_maker.assistant_manager import AssistantManager
from agents.tool_maker.chat_manager import ChatManager


class Unit:
    """
    Manages two symbiotic `Assistant` instances within a Unit Agent designed as a Minimum Viable Agent (MVA).

    The `Unit` facilitates communication between an interface `Assistant` that handles user interactions
    and a functional `Assistant` responsible for backend operations like writing Python functions during tool submissions.

    Attributes:
        assistant_manager (AssistantManager): Manages creation and retrieval of `Assistant` instances.
        chat_manager (ChatManager): Manages thread operations for chat functionalities.
        interface_assistant (Assistant): Assistant for user interaction via chat.
        functional_assistant (Assistant): Assistant for backend operations and tool submissions.
        interface_thread (Thread): Thread linking the `interface_assistant` with the user chat.
        functional_thread (Thread): Thread linking the `functional_assistant` with backend operations.
    """

    def __init__(self, client):
        """
        Initializes a new Unit instance with necessary assistants and threads.

        Args:
            client (Client): OpenAI client instance to be used by managers.
        """
        self.assistant_manager = AssistantManager(client=client)
        self.chat_manager = ChatManager(client=client)
        self.interface_assistant = self.assistant_manager.get_assistant()
        self.functional_assistant = self.assistant_manager.get_coding_assistant()
        self.interface_thread = self.chat_manager.create_empty_thread()
        self.functional_thread = self.chat_manager.create_empty_thread()

    def chat(self):
        """
        Processes user input to perform operations using the `interface_assistant` within its designated thread.
        The loop facilitates continuous interaction until explicitly terminated.
        """
        try:
            while True:
                self.interface_assistant, self.interface_thread, self.functional_thread = self.chat_manager.run_unit(
                    interface_assistant=self.interface_assistant,
                    interface_thread=self.interface_thread,
                    functional_assistant=self.functional_assistant,
                    functional_thread=self.functional_thread,
                )
        except KeyboardInterrupt:
            print("Chat session ended.")


if __name__ == "__main__":
    from shared.openai_config import get_openai_client
    client = get_openai_client()
    unit = Unit(client=client)
    unit.chat()
