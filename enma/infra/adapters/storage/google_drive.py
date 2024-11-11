try:
    from googleapiclient.discovery import build, HttpError
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2.service_account import Credentials
except ImportError as e:
    raise ImportError(
        "The dependencies for Google Drive are not installed. "
        "Please install them using 'pip install enma[google_drive]'."
    ) from e

from enma.application.core.interfaces.saver_adapter import File, ISaverAdapter

class GoogleDriveStorage(ISaverAdapter):

    def __init__(
            self, 
            credentials_path: str,
            root_shared_folder: str):
        self.credentials = Credentials.from_service_account_file(credentials_path)
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.root_shared_folder = root_shared_folder

    def save(self, path: str, file: File) -> bool:
        try:
            folder_id = self._get_or_create_folder(path)

            file_metadata = {
                'name': file.name,
                'parents': [folder_id]
            }

            media = MediaIoBaseUpload(file.data, mimetype='application/octet-stream')

            teste = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(teste)
            return True
        except HttpError as e:
            print(f'Erro HTTP ao fazer upload: {e}')
            return False
        except Exception as e:
            print(f'Erro ao fazer upload: {e}')
            return False

    def _get_or_create_folder(self, path: str) -> str:
        folder_names = path.strip('/').split('/')
        parent_id = self.root_shared_folder

        for folder_name in folder_names:
            query = (
                f"name = '{folder_name}' and "
                f"mimeType = 'application/vnd.google-apps.folder' and "
                f"'{parent_id}' in parents and "
                f"trashed = false"
            )

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            items = results.get('files', [])

            if items:
                folder_id = items[0]['id']
            else:
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                folder_id = folder.get('id')

            parent_id = folder_id

        return parent_id