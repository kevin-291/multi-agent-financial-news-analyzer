from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

def model():
    """
    Configure the main model for the application.
    This function sets up the OpenAI model with Ollama as the provider.
    """
    return OpenAIModel(
        model_name='gemma3:1b',
        provider=OpenAIProvider(base_url='http://localhost:11434/v1')
    )