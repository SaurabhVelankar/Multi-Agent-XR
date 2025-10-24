'''
    Database module for BackEnd Agents.
    Loads data from the sceneData.json in the WebXR folder.
    This module contains two different functionalities:
    1. Grab data from the .json file in the WebXR frontEnd;
    2. Update change made by the MAS backEnd to the .json file.
'''

import json
from typing import Dict, List, Optional, Tuple

class Database:
    """
        Python interface to scene data (loads from JSON)
        Agents use this to query and modify scene state
    """

    def __init__(self, json_path='../webXR/sceneData.json'):
        """
        Initialize data exchange 
        Args:
            json_path: Path to sceneData.json file
        """

        self.json_path = json_path
        self.load()


