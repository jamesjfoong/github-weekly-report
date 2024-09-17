import json
import os
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    try:
        config_path = Path(__file__).parent.parent.parent / 'config' / 'config.json'
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Config file not found")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in config file")

def load_env_variables():
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent

    # Construct the path to the .env file
    env_path = project_root / 'config' / '.env'

    # Load the .env file
    load_dotenv(dotenv_path=env_path)

    print(f"Loaded environment variables from {project_root}")

    # Verify that required environment variables are set
    required_vars = ['GITHUB_TOKEN', 'GROQ_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"{var} not found in environment variables")

    # You can return the values if needed, or just verify they exist
    return {
        'github_token': os.getenv('GITHUB_TOKEN'),
        'groq_api_key': os.getenv('GROQ_API_KEY'),
    }