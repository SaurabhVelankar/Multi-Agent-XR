import google.generativeai as genai
import json
import os

class Orchestrator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')