from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings class to manage application settings via environment variables.
    It automatically loads the OpenAI API key from a specified .env file.
    """
    OPENAI_API_KEY: str  # Required: OpenAI API key

    class Config:
        env_file = '.env'                # Specify the environment file
        env_file_encoding = 'utf-8'      # Encoding type of the environment file

# Usage example to demonstrate how to access settings
if __name__ == "__main__":
    settings = Settings()
    print("Loaded OpenAI API Key:", settings.OPENAI_API_KEY)
