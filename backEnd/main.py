from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from backEnd.agents.languageAgent import LanguageAgent

app = FastAPI(title="VR Multi-Agent Spatial System")

# Initialize agents
language_agent = LanguageAgent()