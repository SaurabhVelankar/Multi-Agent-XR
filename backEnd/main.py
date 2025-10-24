from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from orchestrator import Orchestrator
from __init__ import LanguageAgent, SceneAgent, AssetAgent, CodeAgent, VerificationAgent
from database import Database

'''Server side code'''
app = FastAPI(title="VR Multi-Agent Spatial System")

# Initialize specialized agents
language_agent = LanguageAgent()
scene_agent = SceneAgent()
asset_agent = AssetAgent()
code_agent = CodeAgent()
verification_agent = VerificationAgent()

# Initialize orchestration agent
orchestration_agent = Orchestrator()

# Initialize scene database
scene_database = Database()
