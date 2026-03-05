from datetime import date, datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Asistencia, Usuario

api_bp = Blueprint("api", __name__)


@api_bp.get("/")
def root():
    return jsonify({"status": "ok", "message": "API NFC activa"})


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.get("/asistencia")
def registrar_asistencia():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return (
            jsonify({"status": "error", "message": "Parámetro user_id requerido"}),
            400,
        )

    usuario = db.session.get(Usuario, user_id)
    if usuario is None:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    hoy = date.today()
    asistencia_existente = Asistencia.query.filter_by(user_id=user_id, fecha=hoy).first()
    if asistencia_existente:
        return (
            jsonify({"status": "error", "message": "Asistencia ya registrada hoy"}),
            409,
        )

    nueva_asistencia = Asistencia(user_id=user_id, fecha=hoy, hora=datetime.utcnow())
    db.session.add(nueva_asistencia)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify({"status": "error", "message": "Asistencia ya registrada hoy"}),
            409,
        )

    return jsonify({"status": "ok", "message": "Asistencia registrada"}), 200


@api_bp.get("/usuarios")
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.id.asc()).all()
    return jsonify({"status": "ok", "data": [usuario.to_dict() for usuario in usuarios]})


@api_bp.post("/usuarios")
def crear_usuario():
    payload = request.get_json(silent=True) or {}
    nombre = str(payload.get("nombre", "")).strip()

    if not nombre:
        return jsonify({"status": "error", "message": "El campo nombre es requerido"}), 400

    usuario = Usuario(nombre=nombre)
    db.session.add(usuario)
    db.session.commit()

    return jsonify({"status": "ok", "data": usuario.to_dict()}), 201


@api_bp.get("/asistencias")
def listar_asistencias():
    asistencias = Asistencia.query.order_by(Asistencia.hora.desc()).all()
    return jsonify(
        {"status": "ok", "data": [asistencia.to_dict() for asistencia in asistencias]}
    )
