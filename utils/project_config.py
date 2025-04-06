import json
import os
from pathlib import Path

def load_project_config(project_name):
    """載入專案配置"""
    config_path = Path(f"data/{project_name}/config.json")
    if not config_path.exists():
        return None
    
    with open(config_path) as f:
        return json.load(f)

DEFAULT_CONFIG = {
    "metrics": {
        "Pass_Rate(%)": {"threshold": 90, "higher_better": True},
        "Open_Bugs": {"threshold": 10, "higher_better": False},
        "Critical_Bugs": {"threshold": 2, "higher_better": False},
        "Code_Coverage": {"threshold": 80, "higher_better": True}
    },
    "weights": {
        "Pass_Rate(%)": 0.3,
        "Open_Bugs": 0.2, 
        "Critical_Bugs": 0.3,
        "Code_Coverage": 0.2
    },
    "description": ""
}

def init_project_config(project_name):
    """初始化專案配置"""
    config_path = Path(f"data/{project_name}/config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
