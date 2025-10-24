from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions():
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": "[{\"id\": \"1\", \"url\": \"https://example.com/1\", \"snippet\": \"This is the first mock snippet.\", \"title\": \"Mock Title 1\", \"score\": 0.9}, {\"id\": \"2\", \"url\": \"https://example.com/2\", \"snippet\": \"This is the second mock snippet.\", \"title\": \"Mock Title 2\", \"score\": 0.8}]",
                    "role": "assistant",
                },
            }
        ],
        "created": 1677664795,
        "id": "chatcmpl-7QyqztwVhC6n3Kmyb328a42n5k3i",
        "model": "deepseek-coder",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": 17,
            "prompt_tokens": 57,
            "total_tokens": 74,
        },
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
