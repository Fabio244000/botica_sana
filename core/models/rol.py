from enum import Enum


class Rol(str, Enum):
    ADMIN = "admin"
    CAJERO = "cajero"
    AUDITOR = "auditor"
