from core.models.usuario import Usuario
from core.ports.hash_port import HashPort
from core.ports.repository_port import RepositoryPort
from infrastructure.auth_context import set_current_user


class AuthService:
    """Registro y autenticación de usuarios."""

    def __init__(
        self,
        user_repo: RepositoryPort[Usuario],
        hasher: HashPort,
    ) -> None:
        self._repo = user_repo
        self._hash = hasher

    # 1️⃣ Crear usuario
    def create_user(self, username: str, password: str, rol: str) -> Usuario:
        hashed = self._hash.hash(password)
        usuario = Usuario(username=username, password_hash=hashed, rol=rol)
        return self._repo.add(usuario)

    # 2️⃣ Login
    def login(self, username: str, password: str) -> bool:
        user = next((u for u in self._repo.list() if u.username == username), None)

        ok = (
            user is not None
            and user.activo
            and self._hash.verify(password, user.password_hash)
        )

        if ok:
            set_current_user(user)  # sesión válida
            return True

        # 🆕 limpia el contexto cuando falla
        set_current_user(None)
        return False

    # 3️⃣ Cambiar password
    def change_password(self, user_id: int, new_plain: str) -> Usuario:
        user = self._repo.get(user_id)
        if user is None:
            raise ValueError("Usuario no existe")
        user.password_hash = self._hash.hash(new_plain)
        return self._repo.add(user)

    # 4️⃣  Listar usuarios
    def list_users(self) -> list[Usuario]:
        return list(self._repo.list())

    # 5️⃣  Desactivar / activar
    def set_active(self, user_id: int, activo: bool) -> Usuario:
        user = self._repo.get(user_id)
        if not user:
            raise ValueError("Usuario no existe")
        user.activo = activo
        return self._repo.add(user)

    # 6️⃣  Eliminar
    def delete_user(self, user_id: int) -> None:
        self._repo.delete(user_id)
