from datetime import date, datetime

from .extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    tarjeta_uid = db.Column(db.String(120), nullable=True, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    asistencias = db.relationship(
        "Asistencia",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tarjeta_uid": self.tarjeta_uid,
            "created_at": self.created_at.isoformat(),
        }


class Asistencia(db.Model):
    __tablename__ = "asistencias"
    __table_args__ = (
        db.UniqueConstraint("user_id", "fecha", name="uq_asistencia_user_fecha"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha = db.Column(db.Date, nullable=False, default=date.today, index=True)
    hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="asistencias", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fecha": self.fecha.isoformat(),
            "hora": self.hora.isoformat(),
        }
