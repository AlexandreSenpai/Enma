from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import queue
import threading
from typing import Optional
from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.application.core.interfaces.saver_adapter import File, ISaverAdapter
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.manga import Chapter, Image

@dataclass
class Threaded:
    use_threads: bool
    number_of_threads: int

@dataclass
class DownloadChapterRequestDTO:
    chapter: Chapter
    path: str
    saver_adapter: ISaverAdapter
    downloader: IDownloaderAdapter
    threaded: Optional[Threaded] = field(default_factory=lambda: Threaded(use_threads=False,
                                                                          number_of_threads=0))

@dataclass
class DownloadChapterResponseDTO:
    done: bool
    
class DownloadChapterUseCase(IUseCase[DownloadChapterRequestDTO, DownloadChapterResponseDTO]):

    def __make_download_with_queue(self, page: Image):
        downloaded = self.downloader.download(page=page)
        logger.debug(f'Download completed sending {page.name} to saving queue.')
        self.queue.put(File(name=page.name, data=downloaded))

    def __handle_saving(self, save_queue: queue.Queue[File], path: str, saver: ISaverAdapter) -> None:
        while True:
            try:
                content = save_queue.get(timeout=5)
                logger.debug(f'Saving file to path: {path} with name: {content.name}')
                saved = saver.save(path=path, file=content)
                if saved:
                    save_queue.task_done()
            except queue.Empty:
                return

    def __spawn_workers(self, chapter: Chapter, workers: int) -> None:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.__make_download_with_queue, page): page for page in chapter.pages}
            executor.shutdown()

        for future in as_completed(futures):
            page = futures[future]
            try:
                _ = future.result()
            except Exception as err:
                logger.error(f"Error while downloading {page}: {err}")

    def __make_sync_download(self, chapter: Chapter, downloader: IDownloaderAdapter) -> None:
        for page in chapter.pages:
            self.__make_download_with_queue(page=page)
    
    def __create_queue(self) -> queue.Queue[File]:
        return queue.Queue[File]()

    def execute(self, dto: DTO[DownloadChapterRequestDTO]) -> DownloadChapterResponseDTO:
        try:

            using_threads = dto.data.threaded is not None

            logger.info(f'Downloading chapter with {len(dto.data.chapter.pages)} pages.')
            
            logger.debug(f'Using threads to perform download: {using_threads}.')

            self.queue = self.__create_queue()
            self.downloader = dto.data.downloader

            threads: list[threading.Thread] = []
            queue_threads_num = 1

            logger.debug(f'Spawning {queue_threads_num} threads to handle download queue.')
            for _ in range(queue_threads_num):
                t = threading.Thread(target=self.__handle_saving, args=(self.queue,
                                                                        dto.data.path,
                                                                        dto.data.saver_adapter))
                t.start()
                threads.append(t)

            if dto.data.threaded is not None:
                self.__spawn_workers(chapter=dto.data.chapter, workers=dto.data.threaded.number_of_threads)
            else:
                self.__make_sync_download(chapter=dto.data.chapter, downloader=dto.data.downloader)

            self.queue.join()

            for thread in threads:
                thread.join(timeout=5)

            return DownloadChapterResponseDTO(done=True)
        except Exception as err:
            logger.error(err)
            return DownloadChapterResponseDTO(done=False)
