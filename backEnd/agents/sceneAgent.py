import google.generativeai as genai
import json
import os

class SceneAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
