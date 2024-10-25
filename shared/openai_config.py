from shared.settings import Settings
from openai import OpenAI
import logging

def get_openai_client() -> OpenAI:
    """
    Initializes and returns an OpenAI client using the API key from settings.

    Returns:
        OpenAI: An instance of the OpenAI client configured with the API key.

    Raises:
        ValueError: If the API key is not found or is invalid.
    """
    settings = Settings()
    if not settings.OPENAI_API_KEY:
        logging.error("No OpenAI API key found in settings.")
        raise ValueError("OpenAI API key must be provided in the settings.")

    logging.info("OpenAI client initialized successfully.")
    return OpenAI(api_key=settings.OPENAI_API_KEY)

# Example usage
if __name__ == "__main__":
    try:
        openai_client = get_openai_client()
        # You can now use openai_client to interact with OpenAI services
        print("OpenAI Client is ready to use.")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
