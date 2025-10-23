# llm-service (Ollama + Express proxy)

This microservice provides a small Express API that will act as a layer that is part of our analysis process. 

**Why separate this from our Djago app you might be thinking?** Because we can deploy this microservice completely independently, scale it separately. If we need to rotate cloud providers, it is extremely easy to do so with this architecture. We can simply use our cloud computing trials and clone this microservice to the new environment without touching our main application.

**Why use an express.js layer and not the API that comes with Olamma?**
The Express.js API forwards requests to a locally running Ollama instance, which hosts the LLM models. This allows us to handle authentication, logging, rate limiting, and much more when we need to in the future.

For development and testing purposes, it is advised that you run a small model on Olamma locally (e.g., `mistral` or `llama3`), which can be pulled from Ollama's model repository. **NOTE:** we will use much powerful models in production.

Quick Rundown:
- Ollama handles model hosting and the model API at port 11434 by default.
- The Express server exposes a simple HTTP API (JSON) which forwards requests to Ollama (so your frontend/backend can call a single service).

## Prerequisites

- Node.js (v16+ recommended)
- npm (or yarn)
- Ollama installed on the host machine. See https://ollama.com/ for installation instructions.

## Install

From the `src/llm-service` folder:

```powershell
npm install
```

## Run an Ollama instance (local model server)

1. Install Ollama following the official instructions: https://ollama.com/
2. Pull or install the model you want to use using cmd. Example using the `mistral` model (replace with the model you prefer):

```bash
ollama pull mistral
```

3. Start the Ollama server (it will listen on 127.0.0.1:11434 by default):

```bash
ollama serve
```

Notes
- By default Ollama listens on port 11434 and exposes a REST-like endpoint `/api/generate`.
- The reason we use an Express proxy is to add flexibility (authentication, logging, rate limiting, payload normalization) and to avoid CORS issues when calling from a browser.

## Start the Express server (this microservice)

This Express app is a thin API that forwards requests to the Ollama server. By default it listens on port 3000.

From `src/llm-service`:

```powershell
node index.js
```

On bash / macOS / Linux:

```bash
PORT=3000 node index.js
```

## API Usage
 
 POST to `http://127.0.0.1:3000/api/query`
 
  Express forwards to Ollama and can add auth, logging, rate limits, or payload normalization.

Both endpoints expect JSON like this (example) **make sure to specify the model type**:

```json
{
	"model": "mistral",
	"prompt": "Answer ONLY in English: Summarize the following text: 'Artificial intelligence is transforming the world.'",
	"stream": false
}
```

### Use Postman (recommended)

Open Postman → New Request → POST

URL:

``` 
http://127.0.0.1:3000/api/generate
```

Headers:

```
Content-Type: application/json
```

Body → raw → JSON:

```json
{
	"model": "mistral",
	"prompt": "Answer ONLY in English: Summarize the following text: 'Artificial intelligence is transforming the world.'",
	"stream": false
}
```

Click Send and you will get a response.