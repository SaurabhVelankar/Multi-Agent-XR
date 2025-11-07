import google.generativeai as genai
import json
import os
import math

class SceneAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')