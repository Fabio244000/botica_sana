# conftest.py ─ garantiza que la raíz del repo esté en sys.path
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:  # evita duplicados
    sys.path.insert(0, str(ROOT))
