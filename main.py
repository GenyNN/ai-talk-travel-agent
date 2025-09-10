import json
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import litellm
from litellm import completion
from dotenv import load_dotenv
from simple_travel_agent import run_simple_travel_agent
from travel_agent import run_travel_agent_with_input
#import pydevd_pycharm

# Load environment variables
#pydevd_pycharm.settrace('localhost', port=12388, stdoutToServer=True, stderrToServer=True)
load_dotenv()
litellm.set_verbose=True
#litellm.turn_on_debug()


# Configure litellm for OpenRouter function calling
# Note: add_function_to_prompt can cause issues with newer litellm versions
# litellm.add_function_to_prompt = True

app = FastAPI(title="AI Talk Travel Agent", description="A FastAPI application that forwards messages to neural networks using litellm")

class MessageRequest(BaseModel):
    message: str
    model: str = "openrouter/google/gemini-2.0-flash-exp:free"
    max_tokens: int = 1024

class MessageResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int = None

class TravelAgentRequest(BaseModel):
    message: str

class TravelAgentResponse(BaseModel):
    memory: list
    status: str

def generate_ai_response(message: str, model: str = "openrouter/google/gemini-2.0-flash-exp:free", max_tokens: int = 1024) -> Dict[str, Any]:
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
            "/travel-agent": "POST - Run travel agent with trip purpose interview",
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

@app.post("/travel-agent", response_model=TravelAgentResponse)
async def travel_agent(request: TravelAgentRequest):
    """
    Run the travel agent to interview user about trip purpose
    """
    try:
        from travel_agent import process_user_response, agent_state, reset_agent_state
        
        # Check if this is a new conversation request (keywords that indicate starting fresh)
        new_conversation_keywords = ["travel", "поездка", "путешествие", "тур", "начать", "новый", "снова"]
        is_new_conversation = any(keyword in request.message.lower() for keyword in new_conversation_keywords)
        
        # Reset state if previous conversation was completed OR if this is a new conversation request
        if (agent_state.get("goal_completed", False) or 
            not agent_state.get("conversation_active", True) or 
            is_new_conversation):
            reset_agent_state()
        
        # Check if this is a continuation of an existing conversation
        if agent_state["current_goal"] > 1 or (agent_state["current_goal"] == 1 and agent_state.get("has_asked_goal_1", False)):
            # Process user response and advance to next goal
            final_memory = process_user_response(request.message)
        else:
            # Start new conversation
            final_memory = run_travel_agent_with_input(request.message)

        # Convert memory to list format for JSON response
        memory_list = []
        for item in final_memory.get_memories():
            memory_list.append({
                "type": item["type"],
                "content": item["content"]
            })

        # Determine status based on current goal
        if agent_state["current_goal"] > 8 or agent_state.get("goal_completed", False):
            status = "completed"
        else:
            status = "in_progress"

        return TravelAgentResponse(
            memory=memory_list,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running travel agent: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-talk-travel-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
