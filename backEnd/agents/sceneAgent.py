import google.generativeai as genai
import json
import os
import math

class SceneAgent:
    def __init__(self, database):
        self.db = database
