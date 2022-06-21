from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.interfaces import CommentPage

class GetCommentsUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    def execute(self, doujin_id: int) -> CommentPage:
        return self.nhentai_repo.get_comments(doujin_id=doujin_id)