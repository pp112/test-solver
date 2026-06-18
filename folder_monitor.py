import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileHandler(FileSystemEventHandler):
    def __init__(self, rename_callback):
        self.rename_callback = rename_callback

    def on_created(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        self.rename_callback(path)
        

class FolderMonitor:
    """
    Мониторит папку и переименовывает новые файлы в порядковые номера
    после того, как файл полностью загружен.
    """

    def __init__(self, folder: str, file_callback=None):
        self.folder = Path(folder)
        self.file_callback = file_callback
        self.counter = 1
        self._observer = Observer()
        self._observer.daemon = True

    def start(self):
        self.folder.mkdir(parents=True, exist_ok=True)

        event_handler = FileHandler(self._handle_file)

        self._observer.schedule(event_handler, str(self.folder))

        self._observer.start()
        print("FolderMonitor запущен.")

        while True:
            time.sleep(1)

    def _handle_file(self, path: Path):
        if not path.exists():
            return
        
        self._wait_until_ready(path)
        new_path = self._rename(path)

        if self.file_callback:
            self.file_callback(new_path)
    
    def _wait_until_ready(self, path: Path):
        """
        Ждём пока файл перестанет изменяться (докачка/дозапись).
        """
        last_size = -1
        stable_count = 0
        checks = 3
        delay = 0.5

        while stable_count < checks:
            try:
                size = path.stat().st_size
            except FileNotFoundError:
                return
            
            if size == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = size

            time.sleep(delay)

    def _rename(self, path: Path):
        ext = path.suffix
        new_name = f"{self.counter}{ext}"
        new_path = self.folder / new_name

        while new_path.exists():
            self.counter += 1
            new_name = f"{self.counter}{ext}"
            new_path = self.folder / new_name

        path.rename(new_path)

        print(f"Переименован: {path.name} → {new_name}")
        self.counter += 1

        return new_path