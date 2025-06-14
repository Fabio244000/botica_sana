from abc import ABC, abstractmethod


class HashPort(ABC):
    """Puerta de hash (BCrypt, Argon2, etc.)."""

    @abstractmethod
    def hash(self, plain: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...
