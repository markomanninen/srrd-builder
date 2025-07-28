import json
from pathlib import Path

def get_installation_status():
    """Reads the installation status from installed_features.json."""
    config_path = Path(__file__).parent / "installed_features.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle malformed JSON
            return {"latex_installed": False, "vector_db_installed": False}
    return {"latex_installed": False, "vector_db_installed": False}

def is_latex_installed():
    """Checks if LaTeX is marked as installed."""
    return get_installation_status().get("latex_installed", False)

def is_vector_db_installed():
    """Checks if the vector database is marked as installed."""
    return get_installation_status().get("vector_db_installed", False)
