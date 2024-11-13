from enma.application.core.interfaces.saver_adapter import File, ISaverAdapter
from enma.application.core.utils.logger import logger

class GoogleDriveStorage(ISaverAdapter):

    def __init__(
            self, 
            credentials_path: str,
            root_shared_folder: str):

        try:
            from googleapiclient.discovery import build, HttpError
            from googleapiclient.http import MediaIoBaseUpload
            from google.oauth2.service_account import Credentials

            self.MediaIoBaseUpload = MediaIoBaseUpload
            self.HttpError = HttpError
            self.build = build
        except ImportError as e:
            raise ImportError(
                "The dependencies for Google Drive are not installed. "
                "Please install them using 'pip install enma[google_drive]'."
            ) from e
            
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

            logger.debug(f'Uploading image to google drive with name: {file.name} and parent folder: {folder_id}')

            media = self.MediaIoBaseUpload(file.data, mimetype='application/octet-stream')

            self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return True
        except self.HttpError as e:
            logger.error(f'A HTTP error ocurred while trying to upload image to google drive: {e}')
            return False
        except Exception as e:
            logger.error(f'An unknown error ocurred while trying to upload image to google drive: {e}')
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

            logger.debug(f'Querying folder with query: {query}')

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

                logger.debug(f'Creating folder with metadata: {folder_metadata}')

                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                folder_id = folder.get('id')

            parent_id = folder_id

        return parent_id