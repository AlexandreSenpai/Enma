import os
from enma.application.core.interfaces.saver_adapter import File, ISaverAdapter


class LocalStorage(ISaverAdapter):
    def save(self, path: str, file: File) -> bool:
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, f'{file.name}'), 'wb') as f:
            f.write(file.data.getbuffer())
            f.close()

        return True
