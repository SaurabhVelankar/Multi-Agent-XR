from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.language_agent import LanguageAgent

app = FastAPI(title="VR Multi-Agent Spatial System")