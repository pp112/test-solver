from pathlib import Path
from folder_monitor import FolderMonitor
from ollama_client import OllamaClient


class App:
    def __init__(self, folder: str):
        self.ollama = OllamaClient()
        self.monitor = FolderMonitor(folder=folder, file_callback=self.on_new_file)

    def run(self):
        self.monitor.start()

    def on_new_file(self, path: Path):
        answer = self.ollama.ask_with_image(path)
        print(answer)
