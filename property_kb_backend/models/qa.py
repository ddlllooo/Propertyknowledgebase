from datetime import datetime

from extensions.db import db


class QaKnowledge(db.Model):
    __tablename__ = "qa_knowledge"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False, index=True)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    keywords = db.Column(db.String(255), nullable=True)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    ask_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="已发布", index=True)
    source = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    def to_dict(self):
        keyword_list = []
        if self.keywords:
            keyword_list = [
                item.strip() for item in self.keywords.split(",") if item.strip()
            ]

        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "keywords": keyword_list,
            "viewCount": self.view_count,
            "askCount": self.ask_count,
            "status": self.status,
            "source": self.source,
            "updatedAt": self.updated_at.strftime("%Y-%m-%d")
            if self.updated_at
            else None,
        }

