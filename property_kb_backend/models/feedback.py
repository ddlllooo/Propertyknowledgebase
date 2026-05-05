from datetime import datetime

from extensions.db import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    username = db.Column(db.String(120), nullable=False, index=True)
    chat_log_id = db.Column(db.Integer, nullable=True, index=True)
    qa_id = db.Column(db.Integer, nullable=True, index=True)
    user_question = db.Column(db.String(500), nullable=False)
    ai_answer = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(20), nullable=False, index=True)
    suggestion = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="待处理", index=True)
    category = db.Column(db.String(80), nullable=True, index=True)
    similarity = db.Column(db.Float, nullable=True)
    admin_reply = db.Column(db.Text, nullable=False, default="暂无回复")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    handled_by = db.Column(db.Integer, nullable=True)
    handled_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        created_at = (
            self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None
        )
        admin_reply = self.admin_reply or "暂无回复"

        return {
            "id": self.id,
            "userQuestion": self.user_question,
            "aiAnswer": self.ai_answer,
            "feedbackType": self.feedback_type,
            "suggestion": self.suggestion,
            "status": self.status,
            "category": self.category,
            "similarity": self.similarity,
            "createdAt": created_at,
            "adminReply": admin_reply,
            "time": created_at,
            "question": self.user_question,
            "type": self.feedback_type,
            "reply": admin_reply,
        }

