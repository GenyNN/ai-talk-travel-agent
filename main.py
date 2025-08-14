import json
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from litellm import completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Talk Travel Agent", description="A FastAPI application that forwards messages to neural networks using litellm")

class MessageRequest(BaseModel):
    message: str
    model: str = "openai/gpt-4o"
    max_tokens: int = 1024

class MessageResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int = None

def generate_ai_response(message: str, model: str = "openai/gpt-4o", max_tokens: int = 1024) -> Dict[str, Any]:
    """
    Generate response using litellm, following the pattern from the reference implementation
    """
    try:
        # Prepare messages in the format expected by litellm
        messages = [
            {"role": "user", "content": message}
        ]
        
        # Call the LLM using litellm completion function
        response = completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        
        # Extract the response content
        result = response.choices[0].message.content
        
        return {
            "response": result,
            "model_used": model,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "AI Talk Travel Agent API",
        "description": "Send messages to neural networks using litellm",
        "endpoints": {
            "/chat": "POST - Send a message and get AI response",
            "/health": "GET - Check API health"
        }
    }

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """
    Accept a message and forward it to the neural network using litellm
    """
    try:
        result = generate_ai_response(
            message=request.message,
            model=request.model,
            max_tokens=request.max_tokens
        )
        
        return MessageResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-talk-travel-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
