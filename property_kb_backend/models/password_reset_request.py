from datetime import datetime

from extensions.db import db


class PasswordResetRequest(db.Model):
    __tablename__ = "password_reset_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    username = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="待处理", index=True)
    temp_password_plain = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    handled_by = db.Column(db.Integer, nullable=True)
    handled_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "username": self.username,
            "email": self.email,
            "status": self.status,
            "tempPassword": self.temp_password_plain,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None,
            "handledAt": self.handled_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.handled_at
            else None,
        }
