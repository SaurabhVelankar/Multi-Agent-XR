from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from backEnd.agents.languageAgent import LanguageAgent
from backEnd.agents.sceneAgent import SceneAgent
from backEnd.agents.assetAgent import AssetAgent
from backEnd.agents.codeAgent import CodeAgent
from backEnd.agents.verificationAgent import VerificationAgent

'''Server side code'''
app = FastAPI(title="VR Multi-Agent Spatial System")

# Initialize specialized agents
language_agent = LanguageAgent()
scene_agent = SceneAgent()
asset_agent = AssetAgent()
code_agent = CodeAgent()
verification_agent = VerificationAgent()

