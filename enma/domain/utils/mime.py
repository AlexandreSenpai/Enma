from typing import Union
from enma.application.core.utils.logger import logger
from enma.domain.entities.manga import MIME


def get_mime_safelly(mime: str) -> Union[MIME, None]:
    try:
        return MIME[mime]
    except ValueError:
        logger.error(f'Invalid MIME type: {mime}')
        return None