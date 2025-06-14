import bcrypt

from core.ports.hash_port import HashPort


class BcryptHasher(HashPort):
    """Implementación real usando la librería *bcrypt*."""

    def hash(self, plain: str) -> str:
        plain_b = plain.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)  # coste razonable
        return bcrypt.hashpw(plain_b, salt).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
