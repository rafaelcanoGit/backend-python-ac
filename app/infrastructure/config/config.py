from dotenv import load_dotenv
import os

load_dotenv()

def get_env(env, default=None):
    """Retrieve an environment variable."""
    return os.getenv(env, default)
