# api/main.py
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
from contextlib import asynccontextmanager
import time
import uuid

from.server import bitnet_inference_server

# --- Менеджер життєвого циклу FastAPI ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Керує запуском та зупинкою сервера BitNet.
    Модель завантажується один раз при старті і вивантажується при зупинці.
    """
    print("Запуск сервера BitNet...")
    try:
        bitnet_inference_server.start_process()
        yield
    finally:
        print("Зупинка сервера BitNet...")
        bitnet_inference_server.stop_process()

app = FastAPI(lifespan=lifespan)

# --- Pydantic моделі для валідації запитів/відповідей (сумісні з OpenAI) ---

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048

class ChatCompletionResponseChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List
    usage: Usage

# --- Ендпоінт API ---

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Обробляє запити на доповнення чату.
    """
    # Знаходимо останнє повідомлення від користувача
    user_message = next((msg.content for msg in reversed(request.messages) if msg.role == 'user'), None)

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found in the request.")

    try:
        # Генеруємо відповідь за допомогою сервера BitNet
        response_text = bitnet_inference_server.generate(user_message)

        # Форматуємо відповідь у сумісному з OpenAI форматі
        assistant_message = ChatMessage(role="assistant", content=response_text)
        choice = ChatCompletionResponseChoice(message=assistant_message)
        
        response = ChatCompletionResponse(
            model=request.model,
            choices=[choice],
            usage=Usage() # Токени не підраховуються в цій реалізації
        )
        return response
    except Exception as e:
        print(f"Помилка під час генерації: {e}")
        raise HTTPException(status_code=500, detail=str(e))
