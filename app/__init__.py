from flask import Flask, jsonify

from .config import Config
from .extensions import db
from .routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("La variable de entorno DATABASE_URL es obligatoria.")

    db.init_app(app)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"status": "error", "message": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

    return app
