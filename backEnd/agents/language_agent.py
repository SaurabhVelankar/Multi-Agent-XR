import google.generativeai as genai
import json

class LanguageAgents:
    def __init__(self):
        self.client = genai()
        # AIzaSyCPHwWiX1fwWkn6-ffrFEdQE-qP6KvxE_8 is mine
        genai.configure(api_key= 'try-with-your-own-ones')
        