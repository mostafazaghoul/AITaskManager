# app/main.py
from fastapi import FastAPI
from .database import create_database_tables
from .routes import tasks, ai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create database tables on startup
create_database_tables()

app = FastAPI(
    title="AI-Powered To-Do List API",
    description="A smart, extensible REST API for managing daily tasks with AI assistance.",
    version="1.0.0",
)

# Health check endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI-Powered To-Do List API!"}

# Include routers
app.include_router(tasks.router)
app.include_router(ai.router)

# Basic check for OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable not found.")
    print("AI features will not work.")