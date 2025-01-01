# app/services/base_service.py

from abc import ABC, abstractmethod

class BaseService(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass