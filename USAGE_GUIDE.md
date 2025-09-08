# Travel Agent Console Client Usage Guide

## Overview
The updated console client now provides three modes of interaction with the advanced travel agent:

1. **Regular Chat** - Direct AI conversation
2. **Interactive Travel Agent** - Step-by-step travel planning
3. **Quick Travel Agent** - One-shot travel planning

## How to Use

### 1. Start the Server
First, make sure the FastAPI server is running:
```bash
python main.py
```
The server will start on `http://localhost:8001`

### 2. Start the Console Client
In a new terminal, run:
```bash
python console_client.py
```

### 3. Choose Your Mode

#### Interactive Travel Agent (Recommended)
Type `travel` to start the interactive mode:
```
💬 You: travel
```

This mode will:
- Guide you through all 6 goals step by step
- Ask about trip type, destination, group size, dates, and departure city
- Handle errors gracefully with retry logic
- Generate a comprehensive summary at the end
- Allow you to exit anytime with 'quit', 'exit', or 'stop'

#### Quick Travel Agent
Type `quick` for one-shot processing:
```
💬 You: quick
```

This mode will:
- Process your travel request in one go
- Show all agent memory and responses
- Good for testing or quick interactions

#### Regular Chat
Just type any message for direct AI conversation:
```
💬 You: Hello, how are you?
```

## Features

### Interactive Mode Features
- **Step-by-step guidance** through all travel planning goals
- **Error handling** with polite retry requests
- **State management** to track progress through goals
- **Flexible input** - accepts various response formats
- **Exit options** - can quit anytime during conversation
- **Progress tracking** - remembers where you are in the process

### Error Handling
- If you give an unclear answer, the agent will politely ask for clarification
- Maximum of 3 errors before graceful termination
- Option to reschedule if you're embarrassed to answer
- Returns to the current goal after successful clarification

### Goal Progression
The agent follows this sequence:
1. **Trip Type** - Independent, Organized (preferred), or Business
2. **Destination** - Country, city, or resort
3. **Group Size** - Number of people traveling
4. **Travel Dates** - When you plan to travel
5. **Departure City** - Where you're starting from
6. **Summary** - Complete overview of your travel plans

## Example Session

```
🤖 AI Talk Travel Agent - Advanced Console Interface
============================================================
✅ Server is running and healthy!

Available modes:
1. Regular chat - just type your message
2. Interactive Travel Agent - type 'travel' for step-by-step trip planning
3. Quick Travel Agent - type 'quick' for one-shot travel planning
Type 'quit' or 'exit' to stop.
------------------------------------------------------------

💬 You: travel

🌍 Starting Interactive Travel Agent
This mode will guide you through a step-by-step travel planning process.
You can type 'quit', 'exit', or 'stop' at any time to end the session.

🤖 Agent: Starting travel planning session...

==================================================
🤖 Travel Agent Response:
==================================================

What type of trip are you planning?

Please choose one of the following options:
1) Independent trip - you organize everything yourself
2) Organized tourism - use the services of a tour operator (recommended)
3) Business trip

Please respond with the number (1, 2, or 3) or the full option name.

==================================================

💬 Your response: 2

🤖 Agent is processing your response...

==================================================
🤖 Travel Agent Response:
==================================================

Which country, city, or resort would you like to visit? Please provide the specific destination.

==================================================

💬 Your response: Paris, France

... (continues through all goals)

==================================================
🤖 Travel Agent Response:
==================================================

Dear tourist, you have entered the following information:

• You have chosen: Organized tourism, using the services of a tour operator
• Destination: Paris, France
• Number of people: 2 people
• Travel dates: June 15-25, 2024
• Departure city: New York

I wish you a good journey!

==================================================

👋 Ending travel planning session. Goodbye!
```

## Troubleshooting

### Server Not Running
If you see "Server is not available", make sure to start the server first:
```bash
python main.py
```

### Connection Errors
If you get connection errors, check that:
- The server is running on port 8001
- No firewall is blocking the connection
- The server started without errors

### Agent Not Responding
If the agent doesn't respond:
- Check that all dependencies are installed
- Verify the .env file has the required API keys
- Check server logs for errors

## Dependencies
Make sure you have all required packages installed:
```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- litellm
- python-dotenv
- pydantic
- requests

