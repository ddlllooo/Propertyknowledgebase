from datetime import datetime

from extensions.db import db


class ChatLog(db.Model):
    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    username = db.Column(db.String(120), nullable=False, index=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, default="未分类")
    similarity = db.Column(db.Float, nullable=False, default=0)
    hit_status = db.Column(db.String(20), nullable=False, default="未命中", index=True)
    need_human = db.Column(db.Boolean, nullable=False, default=True, index=True)
    is_guest = db.Column(db.Boolean, nullable=False, default=False, index=True)
    response_time = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "similarity": self.similarity,
            "hitStatus": self.hit_status,
            "needHuman": self.need_human,
            "isGuest": self.is_guest,
            "responseTime": self.response_time,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None,
        }

    def to_history_dict(self):
        return {
            "id": self.id,
            "time": self.created_at.strftime("%Y-%m-%d %H:%M")
            if self.created_at
            else None,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "hit": self.hit_status == "已命中",
            "needManual": self.need_human,
            "isGuest": self.is_guest,
        }

