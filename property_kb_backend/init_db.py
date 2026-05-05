from app import app
from extensions.db import db
from models.category import Category
from models.chat_log import ChatLog
from models.feedback import Feedback
from models.qa import QaKnowledge
from models.user import User


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("数据库表创建完成")
