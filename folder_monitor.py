from pathlib import Path


class FolderMonitor:
    """
    Мониторит папку и переименовывает новые файлы в порядковые номера
    после того, как файл полностью загружен.
    """

    def __init__(self, folder: str):
        self.folder = Path(folder)
        self.counter = 1
        