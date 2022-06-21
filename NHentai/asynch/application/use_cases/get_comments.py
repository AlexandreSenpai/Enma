from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.interfaces.doujin import CommentPage

class GetCommentsUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    async def execute(self, doujin_id: int) -> CommentPage:
        return await self.nhentai_repo.get_comments(doujin_id=doujin_id)