# Behavioral Rules
## Setup
The agent must configure the global LLM provider and API keys during setup.

## LLM Provider
The agent must support the following LLM providers:
* Groq
* Anthropic
* OpenAI
* OpenRouter
* Google
* Ollama

## Model ID
The agent must prompt the user for a model ID during setup.

## API Key
The agent must prompt the user for an API key during setup, unless the provider is Ollama.

## Base URL
The agent must prompt the user for a base URL during setup, if the provider is Ollama.

## Config
The agent must update the config with the new provider configuration during setup.

## Invariants
* The agent must always load the environment early during setup.
* The agent must always use the `load_dotenv` function to load the environment.
* The agent must always use the `click` library to prompt the user for input.