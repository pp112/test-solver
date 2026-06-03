import base64
from pathlib import Path

from ollama import AsyncClient


SYSTEM_PROMPT = """Ты помощник для решения тестов. 
Тебе будут присылаться скриншоты вопросов с вариантами ответов.
Твоя задача — внимательно прочитать вопрос и все варианты ответов, 
затем выбрать правильный вариант или несколько правильных вариантов.
"""


class OllamaClient:
    """Клиент для работы с Ollama API с поддержкой vision и сессии чата."""

    def __init__(self, model: str = "llava:7b"):
        self.model = model
        self.client = AsyncClient()
        self.history: list[dict] = []
        self._initialized = False

    async def ask_with_image(self, image_path: Path, reset_after = False) -> str:
        """Отправить вопрос в виде изображения, получить ответ модели."""
        if not self._initialized:
            await self._initialize()

        image_b64 = self._encode_image(image_path)

        message = {
            "role": "user",
            "content": "Реши этот вопрос теста:",
            "images": [image_b64]
        }
        self.history.append(message)

        response = await self._send_request()
        
        if reset_after:
            self._reset()
        
        return response
    
    async def _initialize(self) -> None:
        """Инициализация сессии: отправка системного промпта."""
        if self._initialized:
            return

        self.history = []
        init_message = {
            "role": "user",
            "content": SYSTEM_PROMPT
        }
        self.history.append(init_message)

        response = await self._send_request()
        self.history.append({"role": "assistant", "content": response})
        self._initialized = True

    async def _send_request(self) -> str:
        """Отправить текущую историю чата в Ollama и получить ответ."""
        response = await self.client.chat(
            model=self.model,
            messages=self.history
        )
        return response["message"]["content"]

    def _encode_image(self, image_path: Path) -> str:
        """Закодировать изображение в base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _reset(self) -> None:
        """Сбросить историю чата."""
        self.history = []
        self._initialized = False
