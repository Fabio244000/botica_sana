from __future__ import annotations

from pydantic import SecretStr

from core.models.rol import Rol
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

    # ------------------------------------------------------------------
    # 1️⃣  Crear usuario
    # ------------------------------------------------------------------
    def create_user(
        self,
        *,
        username: str,
        password: str,
        email: str,
        celular: str,
        direccion: str,
        nombre_completo: str,
        dni: str,
        rol: Rol = Rol.CAJERO,
        activo: bool = True,
    ) -> Usuario:
        """
        Crea un nuevo usuario.

        - Valida complejidad de contraseña vía modelo `Usuario`.
        - Valida nombre completo y DNI vía modelo `Usuario`.
        - Almacena la contraseña hasheada.
        - Inicializa el campo `activo`.
        """
        # Construye y valida todos los campos
        usuario = Usuario(
            username=username,
            password=SecretStr(password),
            email=email,
            celular=celular,
            direccion=direccion,
            nombre_completo=nombre_completo,
            dni=dni,
            rol=rol,
            activo=activo,
        )

        # Hashea la contraseña antes de persistir
        hashed = self._hash.hash(password)
        usuario.password = SecretStr(hashed)

        return self._repo.add(usuario)

    # ------------------------------------------------------------------
    # 2️⃣  Login
    # ------------------------------------------------------------------
    def login(self, username: str, password: str) -> bool:
        """
        Autentica credenciales y setea el contexto de usuario.
        """
        user = next((u for u in self._repo.list() if u.username == username), None)

        ok = (
            user is not None
            and user.activo
            and self._hash.verify(password, user.password.get_secret_value())
        )

        set_current_user(user if ok else None)
        return ok

    # ------------------------------------------------------------------
    # 3️⃣  Cambiar contraseña
    # ------------------------------------------------------------------
    def change_password(self, user_id: int, new_plain: str) -> Usuario:
        """
        Cambia la contraseña de un usuario, validando complejidad.
        """
        user = self._repo.get(user_id)
        if user is None:
            raise ValueError("Usuario no existe")

        # Validación de complejidad: recreamos un Usuario temporal
        Usuario(
            username=user.username,
            password=SecretStr(new_plain),
            email=user.email,
            celular=user.celular,
            direccion=user.direccion,
            nombre_completo=user.nombre_completo,
            dni=user.dni,
            rol=user.rol,
            activo=user.activo,
        )

        # Si pasó validación, actualizamos hash
        user.password = SecretStr(self._hash.hash(new_plain))
        return self._repo.add(user)

    # ------------------------------------------------------------------
    # 4️⃣  Listar usuarios
    # ------------------------------------------------------------------
    def list_users(self) -> list[Usuario]:
        return list(self._repo.list())

    # ------------------------------------------------------------------
    # 5️⃣  Activar / desactivar
    # ------------------------------------------------------------------
    def set_active(self, user_id: int, activo: bool) -> Usuario:
        user = self._repo.get(user_id)
        if user is None:
            raise ValueError("Usuario no existe")
        user.activo = activo
        return self._repo.add(user)

    # ------------------------------------------------------------------
    # 6️⃣  Eliminar
    # ------------------------------------------------------------------
    def delete_user(self, user_id: int) -> None:
        self._repo.delete(user_id)
