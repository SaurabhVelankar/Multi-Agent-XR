import google.generativeai as genai
import json
import os

class AssetAgent:
    def __init__(self):
        """
        Description: 
            The Asset agent is used to handle the insertion and the deleltion of 
            the items within in the scene according to human prompt.
        """
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')