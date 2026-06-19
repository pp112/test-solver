import base64
from pathlib import Path

from ollama import Client


SYSTEM_PROMPT = """Ты помощник для решения тестов. 
Тебе будут присылаться скриншоты вопросов с вариантами ответов.
Твоя задача — внимательно прочитать вопрос и все варианты ответов, 
затем выбрать правильный вариант или несколько правильных вариантов.
Также вопросы могут приходить в текстовом формате или без вариантов ответов. 
Если нет вариантов, то надо дать развернутый ответ.
"""


class OllamaClient:
    """Клиент для работы с Ollama API с поддержкой vision и сессии чата."""

    def __init__(self, model: str = "gemma4:e4b"):
        self.model = model
        self.client = Client()
        self.history: list[dict] = []
        self._initialized = False

    def ask_with_image(self, image_path: Path, reset_after = False) -> str:
        """Отправить вопрос в виде изображения, получить ответ модели."""
        if not self._initialized:
            self._initialize()

        image_b64 = self._encode_image(image_path)

        message = {
            "role": "user",
            "content": "Реши вопрос(ы):",
            "images": [image_b64]
        }
        self.history.append(message)

        response = self._send_request()
        
        if reset_after:
            self._reset()
        
        return response
    
    def _initialize(self) -> None:
        """Инициализация сессии: отправка системного промпта."""
        if self._initialized:
            return

        print(f"Инициализация чата {self.model}")
        self.history = []
        init_message = {
            "role": "user",
            "content": SYSTEM_PROMPT
        }
        self.history.append(init_message)

        response = self._send_request()
        self.history.append({"role": "assistant", "content": response})
        self._initialized = True
        print(self.history)

    def _send_request(self) -> str:
        full_response = ""

        stream = self.client.chat(
            model=self.model,
            messages=self.history,
            stream=True
        )

        for chunk in stream:
            content = chunk["message"]["content"]
            print(content, end="", flush=True)
            full_response += content

        print()
        return full_response

    def _encode_image(self, image_path: Path) -> str:
        """Закодировать изображение в base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _reset(self) -> None:
        """Сбросить историю чата."""
        self.history = []
        self._initialized = False
