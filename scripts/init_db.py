import os
import sys
import time
from pathlib import Path

from sqlalchemy.exc import OperationalError

# Asegura imports absolutos como "from app import ..." al ejecutar este script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db


def init_db() -> None:
    max_retries = int(os.getenv("DB_INIT_MAX_RETRIES", "20"))
    retry_delay = float(os.getenv("DB_INIT_RETRY_DELAY", "2"))

    app = create_app()
    with app.app_context():
        for attempt in range(1, max_retries + 1):
            try:
                db.create_all()
                print("Base de datos inicializada.")
                return
            except OperationalError as exc:
                if attempt == max_retries:
                    raise RuntimeError("No se pudo conectar a la base de datos.") from exc
                print(
                    "Intento de conexion a DB fallido "
                    f"({attempt}/{max_retries}). Reintentando en {retry_delay}s..."
                )
                time.sleep(retry_delay)


if __name__ == "__main__":
    init_db()
