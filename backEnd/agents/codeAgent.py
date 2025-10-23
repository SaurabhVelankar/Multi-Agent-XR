import google.generativeai as genai
import json
import os

class CodeAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')