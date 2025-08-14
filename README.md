# AI Talk Travel Agent

A FastAPI application that accepts console messages and forwards them to neural networks using the [litellm](https://github.com/BerriAI/litellm) library, following the pattern from the [coursera-aiagent-developer](https://github.com/GenyNN/coursera-aiagent-developer/blob/main/shared/game/core.py) reference implementation.

## Features

- 🚀 FastAPI-based REST API
- 🤖 Integration with multiple AI models via litellm
- 💬 Simple console interface for message exchange
- 🔧 Easy configuration and deployment
- 📊 Token usage tracking
- 🏥 Health check endpoints

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-talk-travel-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env and add your API keys
```

## Configuration

Create a `.env` file with your API keys:

```bash
# Required for OpenAI models
OPENAI_API_KEY=your_openai_api_key_here

# Optional for other models
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

### Starting the Server

Run the FastAPI server:

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Using the Console Interface

Start the console client:

```bash
python console_client.py
```

This provides an interactive chat interface where you can:
- Type messages and get AI responses
- See which model was used
- View token usage statistics
- Type 'quit' or 'exit' to stop

### API Endpoints

- `GET /` - API information
- `POST /chat` - Send message to AI
- `GET /health` - Health check

#### Example API Usage

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "model": "openai/gpt-4o",
       "max_tokens": 1024
     }'
```

## Architecture

The application follows the pattern from the reference implementation:

1. **Message Processing**: Accepts user messages via FastAPI endpoints
2. **litellm Integration**: Uses litellm's `completion()` function to forward messages to AI models
3. **Response Handling**: Processes and returns AI responses with metadata
4. **Console Interface**: Provides a user-friendly way to interact with the API

## Supported Models

The application supports any model that litellm supports, including:

- OpenAI: `openai/gpt-4o`, `openai/gpt-3.5-turbo`
- Anthropic: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- Google: `gemini/gemini-pro`
- And many more...

## Development

### Project Structure

```
ai-talk-travel-agent/
├── main.py              # FastAPI application
├── console_client.py    # Console interface client
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── start.sh            # Startup script
├── test_setup.py       # Setup verification script
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # This file
```

### Running Tests

```bash
# Start the server
python main.py

# In another terminal, test the API
curl http://localhost:8000/health
```

### Docker Deployment

You can also run the application using Docker:

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run manually
docker build -t ai-talk-agent .
docker run -p 8000:8000 --env-file .env ai-talk-agent
```

## Testing Setup

Run the test script to verify your installation:

```bash
python test_setup.py
```

## License

This project is open source and available under the MIT License.
