import google.generativeai as genai
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database import Database

class AssetAgent:
    """
    Asset Agent handles:
    - Creating new objects in the scene
    - Removing existing objects from the scene
    - Selecting appropriate assets from available library
    - Managing object lifecycle (creation/deletion)
    """

    def __init__(self):
        """
        Description: 
            The Asset agent is used to handle the insertion and the deleltion of 
            the items within in the scene according to human prompt.
        """
        genai.configure(api_key='API Key')
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')