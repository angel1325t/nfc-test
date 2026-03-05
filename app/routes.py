from datetime import date, datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Asistencia, Usuario

api_bp = Blueprint("api", __name__)


def _resolver_usuario_para_asistencia():
    user_id = request.args.get("user_id", type=int)
    tarjeta_uid = str(request.args.get("tarjeta_uid", "")).strip()

    if user_id and tarjeta_uid:
        return None, (
            jsonify(
                {
                    "status": "error",
                    "message": "Usa solo uno de estos parámetros: user_id o tarjeta_uid",
                }
            ),
            400,
        )

    if user_id:
        usuario = db.session.get(Usuario, user_id)
        if usuario is None:
            return (
                None,
                (jsonify({"status": "error", "message": "Usuario no encontrado"}), 404),
            )
        return usuario, None

    if tarjeta_uid:
        usuario = Usuario.query.filter_by(tarjeta_uid=tarjeta_uid).first()
        if usuario is None:
            return (
                None,
                (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Tarjeta no asociada a un usuario",
                        }
                    ),
                    404,
                ),
            )
        return usuario, None

    return None, (
        jsonify(
            {
                "status": "error",
                "message": "Parámetro user_id o tarjeta_uid requerido",
            }
        ),
        400,
    )


@api_bp.get("/")
def root():
    return jsonify({"status": "ok", "message": "API NFC activa"})


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.get("/asistencia")
def registrar_asistencia():
    usuario, error_response = _resolver_usuario_para_asistencia()
    if error_response:
        return error_response

    hoy = date.today()
    asistencia_existente = Asistencia.query.filter_by(user_id=usuario.id, fecha=hoy).first()
    if asistencia_existente:
        return (
            jsonify({"status": "error", "message": "Asistencia ya registrada hoy"}),
            409,
        )

    nueva_asistencia = Asistencia(user_id=usuario.id, fecha=hoy, hora=datetime.utcnow())
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
    tarjeta_uid = str(payload.get("tarjeta_uid", "")).strip() or None

    if not nombre:
        return jsonify({"status": "error", "message": "El campo nombre es requerido"}), 400

    if tarjeta_uid:
        existente = Usuario.query.filter_by(tarjeta_uid=tarjeta_uid).first()
        if existente:
            return (
                jsonify({"status": "error", "message": "La tarjeta ya está asignada"}),
                409,
            )

    usuario = Usuario(nombre=nombre, tarjeta_uid=tarjeta_uid)
    db.session.add(usuario)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "La tarjeta ya está asignada"}), 409

    return jsonify({"status": "ok", "data": usuario.to_dict()}), 201


@api_bp.get("/registro-usuario")
def crear_usuario_por_tarjeta():
    tarjeta_uid = str(request.args.get("tarjeta_uid", "")).strip()
    nombre = str(request.args.get("nombre", "")).strip()

    if not tarjeta_uid:
        return (
            jsonify({"status": "error", "message": "Parámetro tarjeta_uid requerido"}),
            400,
        )
    if not nombre:
        return (
            jsonify({"status": "error", "message": "Parámetro nombre requerido"}),
            400,
        )

    existente = Usuario.query.filter_by(tarjeta_uid=tarjeta_uid).first()
    if existente:
        return (
            jsonify({"status": "error", "message": "La tarjeta ya está asignada"}),
            409,
        )

    usuario = Usuario(nombre=nombre, tarjeta_uid=tarjeta_uid)
    db.session.add(usuario)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "La tarjeta ya está asignada"}), 409

    return (
        jsonify(
            {
                "status": "ok",
                "message": "Usuario creado mediante tarjeta",
                "data": usuario.to_dict(),
            }
        ),
        201,
    )


@api_bp.get("/asistencias")
def listar_asistencias():
    asistencias = Asistencia.query.order_by(Asistencia.hora.desc()).all()
    return jsonify(
        {"status": "ok", "data": [asistencia.to_dict() for asistencia in asistencias]}
    )
