import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from extensions.db import db
from utils.response import fail, success


jwt = JWTManager()


def warm_up_embeddings(app):
    from rag.config import RAG_PRELOAD_EMBEDDINGS

    if not RAG_PRELOAD_EMBEDDINGS:
        app.logger.info("RAG embedding preload is disabled")
        return

    try:
        from rag.embeddings import preload_embedding_model

        preload_embedding_model()
        app.logger.info("RAG embedding model warmed up")
    except Exception as exc:
        app.logger.warning("RAG embedding model warm-up failed: %s", exc)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    cors_origins = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
    )

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth import auth_bp
    from routes.qa import qa_bp
    from routes.admin_category import admin_category_bp
    from routes.admin_chat_logs import admin_chat_logs_bp
    from routes.admin_dashboard import admin_dashboard_bp
    from routes.admin_feedback import admin_feedback_bp
    from routes.admin_qa import admin_qa_bp
    from routes.chat import chat_bp
    from routes.feedback import feedback_bp
    from routes.vector import vector_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(qa_bp, url_prefix="/api/qa")
    app.register_blueprint(admin_qa_bp, url_prefix="/api/admin/qa")
    app.register_blueprint(admin_category_bp, url_prefix="/api/admin/category")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(admin_feedback_bp, url_prefix="/api/admin/feedback")
    app.register_blueprint(admin_chat_logs_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_dashboard_bp, url_prefix="/api/admin/dashboard")
    app.register_blueprint(vector_bp, url_prefix="/api/admin/vector")

    @app.get("/api/ping")
    def ping():
        return success(message="后端服务运行正常")

    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return fail("请先登录", 401)

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return fail("无效的登录凭证", 401)

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return fail("登录凭证已过期", 401)

    warm_up_embeddings(app)

    try:
        from rag.faiss_store import preload_faiss_index
        preload_faiss_index()
        app.logger.info("FAISS index preloaded into memory")
    except Exception as exc:
        app.logger.warning("FAISS index preload skipped: %s", exc)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
