# Politics RAG (Retrieval Augmented Generation)

[This was made in December 2024]
This project is a **Retrieval-Augmented Generation (RAG)** system designed to answer questions about French politics using an LLM model. The system retrieves relevant articles or chunks of text from a pre-existing index and sends that data to an LLM for generating context-aware responses. Mistral-7B in this project is hosted using local **Ollama**, which runs on a local machine.

## Features

- **Question Answering**: Provides answers to user queries about French politics by retrieving relevant text from a pre-built index.
- **FastAPI Backend**: A simple, fast API that receives user input, processes the query, and returns a model-generated answer.
- **Ollama-powered Mistral**: Uses Ollama to interact with Mistral 7B that can understand and respond to the question.
- **Pre-processing & Retrieval**: The system is capable of retrieving relevant content from indexed articles and passing it to the model for context-based generation.

## How it Works

1. **User sends a request**: The user sends a POST request to the FastAPI backend with their question. For example, a question about French politics.

2. **Preprocessing**: The system retrieves relevant articles or chunks from the indexed documents using the `retrieve` function. These articles serve as context for the model to generate an answer.

3. **Prompt Engineering**: The retrieved content is then formatted into a prompt, which is structured for Mistral to process effectively.

4. **Interaction with Ollama**: The backend sends the formatted prompt to the Ollama server via an HTTP request to generate a response from the model.

5. **Response Handling**: The generated response is received, parsed, and returned to the user as the final answer.

### Example Request (Curl):

To interact with the system, you can send a request via `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "What is the latest in French politics?"
}'
```

### Example Response:

```json
{
  "answer": "The latest news in French politics is the ongoing debate regarding the pension reform..."
}
```

## API Endpoints

### `/ask` (POST)

- **Description**: This endpoint receives the user’s question, processes it, and returns a generated answer based on the content retrieved from the indexed articles.
  
- **Request Body**:
  - `question`: The user’s query, typically related to French politics.

- **Response**:
  - `answer`: The model-generated response to the query.

- **Error Handling**:
  - Returns a `400` error if no question is provided.
  - Returns a `500` error if there is an issue calling the Ollama server.

## Additional Notes

- The current setup uses **Mistral** as the language model. You can switch to other models supported by Ollama by changing the `model` parameter in the payload.
- If using a cloud server, ensure that the instance has sufficient resources (CPU/GPU) to handle the model’s inference.
- Depending on the cloud instance, performance might vary, and you may need to adjust the configuration for optimal performance.
- Disclaimer : Everything used here is ofcourse completly deprecated today. I was and am still learning. 
