from infrastructure.db import Base, engine
from infrastructure.models import *

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✓ Base de datos creada")
