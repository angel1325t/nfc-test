import os
import sys
import time
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

# Asegura imports absolutos como "from app import ..." al ejecutar este script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db


def run_schema_migrations() -> None:
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())
    if "usuarios" not in table_names:
        return

    user_columns = {column["name"] for column in inspector.get_columns("usuarios")}
    if "tarjeta_uid" not in user_columns:
        db.session.execute(text("ALTER TABLE usuarios ADD COLUMN tarjeta_uid VARCHAR(120)"))
        db.session.commit()
        print("Migracion aplicada: columna usuarios.tarjeta_uid.")

    inspector = inspect(db.engine)
    unique_constraints = inspector.get_unique_constraints("usuarios")
    has_tarjeta_unique = any(
        set(constraint.get("column_names") or []) == {"tarjeta_uid"}
        for constraint in unique_constraints
    )
    if not has_tarjeta_unique:
        db.session.execute(
            text("ALTER TABLE usuarios ADD CONSTRAINT uq_usuarios_tarjeta_uid UNIQUE (tarjeta_uid)")
        )
        db.session.commit()
        print("Migracion aplicada: constraint UNIQUE para usuarios.tarjeta_uid.")


def init_db() -> None:
    max_retries = int(os.getenv("DB_INIT_MAX_RETRIES", "20"))
    retry_delay = float(os.getenv("DB_INIT_RETRY_DELAY", "2"))

    app = create_app()
    with app.app_context():
        for attempt in range(1, max_retries + 1):
            try:
                db.create_all()
                run_schema_migrations()
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
