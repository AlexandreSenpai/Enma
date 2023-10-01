from abc import ABC, abstractmethod

class IEnma(ABC):
    @abstractmethod
    def get(self, identifier: str):
        ...