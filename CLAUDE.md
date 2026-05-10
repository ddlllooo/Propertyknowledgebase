# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick commands

```bash
# Frontend
npm install                  # Install frontend dependencies
npm run dev                  # Start Vite dev server on http://localhost:5173

# Backend
cd property_kb_backend
pip install -r requirements.txt       # Install Python dependencies (into .venv if using venv)
python init_db.py                     # Create database tables
python seed_data.py                   # Insert demo data
python app.py                         # Start Flask dev server on http://localhost:5000
```

## Environment variables

All env vars are centralized in `property_kb_backend/.env` (loaded by both `config.py` and `rag/config.py`). Key variables:

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `property-kb-secret-key` | Flask secret key |
| `JWT_SECRET_KEY` | `property-kb-jwt-secret-key` | JWT signing key |
| `DATABASE_URL` | `mysql+pymysql://root:123456@localhost:3306/property_kb?charset=utf8mb4` | MySQL connection |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `BIGMODEL_API_KEY` | — | ZhipuAI API key |
| `BIGMODEL_BASE_URL` | `https://open.bigmodel.cn/api/paas/v4` | LLM API base URL |
| `BIGMODEL_MODEL` | `GLM-4.5-Air` | LLM model name |
| `EMBEDDING_MODEL_NAME` | `BAAI/bge-small-zh-v1.5` | HuggingFace embedding model |
| `HF_CACHE_DIR` | `storage/hf_cache` | HuggingFace model cache path |
| `FAISS_INDEX_DIR` | `storage/faiss_index` | FAISS index storage path |
| `RAG_TOP_K` | `3` | Number of similar docs to retrieve |
| `RAG_MAX_DISTANCE_THRESHOLD` | `1.2` | Max FAISS distance for a hit |
| `RAG_PRELOAD_EMBEDDINGS` | `true` | Preload embedding model at startup |

Frontend env: root `.env` with `VITE_API_BASE_URL=http://localhost:5000/api`.

## Architecture overview

**Stack**: Vue 3 (Composition API, `<script setup>`) + Element Plus + Vite on the frontend / Flask + Flask-SQLAlchemy + Flask-JWT-Extended + FAISS on the backend. MySQL for structured data, FAISS flat index on disk for vector search.

### Frontend (`src/`)

- `src/main.js` — App entry: mounts Vue, installs Element Plus + all icons globally, installs router.
- `src/App.vue` — Just `<router-view />`.
- `src/router/index.js` — Two top-level layouts:
  - `/user/*` → `UserLayout` (sidebar: home, knowledge base, chat, history, feedback)
  - `/admin/*` → `AdminLayout` (sidebar: home, qa, category, feedback, password-reset, users, logs, dashboard, vector)
  - `/login` — public; `/change-password` — forced password change for temp-password users.
  - `/` redirects based on stored token/role.
  - Route guards check `sessionStorage` for token and role; admins can't visit `/user` and vice versa.
- `src/utils/request.js` — Axios instance with base URL from `VITE_API_BASE_URL` env var. Injects Bearer token. Caches GET responses in-memory (Map with 30s TTL in `src/utils/cache.js`) and returns cached data via a custom axios adapter. Mutations (POST/PUT/DELETE) clear related cache entries. 423 redirects to `/change-password`, 401/403 redirects to `/login`. Default 8s timeout.
- `src/api/*.js` — Thin wrappers around `request` for each resource. 11 API modules: `auth`, `qa`, `chat`, `feedback`, `dashboard`, `vector`, `adminQa`, `adminCategory`, `adminFeedback`, `adminUser`, `adminLog`, `adminPasswordReset`.
- `src/layouts/` — `UserLayout.vue` (5 menu items) and `AdminLayout.vue` (9 menu items) each have a sticky sidebar, top bar with user info, and `<router-view>` for page content.
- `src/views/` — Page components organized by `user/` (5 views) and `admin/` (9 views). Each page fetches its own data in `onMounted` and manages local `ref` state — no shared store.

### Backend (`property_kb_backend/`)

- `app.py` — `create_app()` factory wires up Flask, CORS, JWT, SQLAlchemy, and registers 11 blueprints under `/api/*`. Calls `warm_up_embeddings()` and `preload_faiss_index()` on startup to pre-cache models. Module-level `app` at import time.
- `config.py` — `Config` class read by Flask. Loads `property_kb_backend/.env` via `python-dotenv`. Defines SECRET_KEY, JWT_SECRET_KEY, SQLALCHEMY_DATABASE_URI, CORS_ORIGINS, JWT token expiry (12 hours). All env var access centralized here.
- `extensions/db.py` — Single `SQLAlchemy()` instance imported by models and routes.
- `utils/auth.py` — Two decorators:
  - `@login_required_user` — JWT required + user must exist and be "启用". Returns 423 if `must_change_password` is set.
  - `@admin_required` — same + role must be "admin"
- `utils/response.py` — `success(data, message)` and `fail(message, code)` helpers, both return `{ code, message, data }` JSON.

**Route blueprints (all use `/api` prefix)**:

| Blueprint | Prefix | Decorator | Purpose |
|---|---|---|---|
| `auth_bp` | `/api/auth` | public | login, register, profile, password-reset request/status, change-password |
| `qa_bp` | `/api/qa` | `@login_required_user` | list, detail, categories, home-summary |
| `chat_bp` | `/api/chat` | `@login_required_user` | RAG question answering, my-history |
| `feedback_bp` | `/api/feedback` | `@login_required_user` | submit feedback, user's feedback list |
| `admin_qa_bp` | `/api/admin/qa` | `@admin_required` | CRUD + batch-create + batch-delete + batch-status + stats |
| `admin_category_bp` | `/api/admin/category` | `@admin_required` | CRUD categories |
| `admin_feedback_bp` | `/api/admin/feedback` | `@admin_required` | list/update/delete feedback, feedback-to-knowledge, batch-status |
| `admin_password_reset_bp` | `/api/admin/password-reset` | `@admin_required` | list/reset/ignore password reset requests |
| `admin_user_bp` | `/api/admin/user` | `@admin_required` | CRUD users, batch-status |
| `admin_chat_logs_bp` | `/api/admin` | `@admin_required` | list/delete/batch-delete chat logs, stats |
| `admin_dashboard_bp` | `/api/admin/dashboard` | `@admin_required` | overview, trends, hot questions, stats |
| `vector_bp` | `/api/admin/vector` | `@admin_required` | rebuild/check FAISS index |

**Models** — SQLAlchemy ORM models in `models/`, all use `to_dict()` for camelCase JSON serialization:

- `User` (`users`) — username, email, password_hash, role (user/admin), nickname, status, must_change_password
- `QaKnowledge` (`qa_knowledge`) — question, answer, category, keywords (comma-separated string), view_count, ask_count, status (已发布/草稿/待审核/已停用), source, created_by, updated_by
- `Category` (`categories`) — name (unique), description, question_count, sort_order, status (启用/停用)
- `ChatLog` (`chat_logs`) — user_id, username, question, answer, category, similarity (0–1), hit_status (已命中/未命中), need_human, response_time. Has `to_dict()` and `to_history_dict()`.
- `Feedback` (`feedback`) — user_id, chat_log_id, qa_id, user_question, ai_answer, feedback_type (有帮助/没帮助/需要人工), suggestion, status (待处理/处理中/已处理/已忽略), admin_reply, category, similarity
- `PasswordResetRequest` (`password_reset_requests`) — user_id, username, email, status (pending/approved/ignored), temp_password_plain

**Services** — Business logic layer in `services/`:

- `category_service.py` — `ensure_category()`, `refresh_category_question_count()`, `sync_categories_from_qa()`, `count_category_questions()`, `get_next_sort_order()`
- `dashboard_service.py` — `get_overview()`, `get_daily_trend()`, `get_hit_rate_trend()`, `get_hot_questions()`, `get_category_ratio()`, `get_feedback_status()`, `get_unmatched_questions()`
- `feedback_metrics.py` — `get_helpful_rate_summary()` computes helpful rate stats.

### RAG pipeline (`property_kb_backend/rag/`)

1. `document_builder.py` — Reads `qa_knowledge` rows with `status='已发布'`, builds LangChain `Document` objects with structured `page_content` (分类/问题/关键词/答案) and metadata.
2. `embeddings.py` — Thread-safe singleton wrapping `HuggingFaceEmbeddings` with `BAAI/bge-small-zh-v1.5`. Model cached to `HF_CACHE_DIR`. `preload_embedding_model()` for warmup.
3. `faiss_store.py` — Thread-safe singleton for FAISS vector store. `build_faiss_index()` loads published docs, builds index, saves to `FAISS_INDEX_DIR`, caches in memory. `load_faiss_index()` loads from disk into memory cache. `search_similar_docs()` returns `[(doc, distance), ...]`. `preload_faiss_index()` for startup warmup.
4. `llm_client.py` — Singleton OpenAI-compatible client targeting ZhipuAI (BigModel) API. `call_llm(prompt)` sends system+user messages, returns content. API key is stripped from error messages. `get_llm_health()` returns config status.
5. `rag_service.py` — Orchestrator: `rag_answer(question, user)` calls FAISS search → checks distance threshold → builds prompt → calls LLM → saves ChatLog → returns result with hit status and trace info. Handles empty index, no results, low similarity, and LLM failures (falls back to knowledge base answer or `FALLBACK_ANSWER`).
6. `prompt.py` — `build_prompt(context, question)` constructs the system prompt with knowledge context. `FALLBACK_ANSWER` is the "contact human support" message.
7. `config.py` — Loads `.env` from backend dir and repo root. All RAG settings via env vars (see table above). Sets HuggingFace cache environment variables.

### Data flow for a user question

```
User types question in ChatAgent.vue
  → POST /api/chat { question }
  → chat_bp → rag_service.rag_answer(question, user)
    → search_similar_docs(question)  # FAISS similarity_search_with_score
    → if hit: build_prompt → call_llm → save ChatLog
    → if miss: save ChatLog with FALLBACK_ANSWER
  → response with { answer, category, similarity, hitStatus, needHuman, ... }
  → ChatAgent.vue renders answer + shows feedback buttons
```

### CSV batch import

`QaManage.vue` supports CSV import with inline parsing (character-by-character, handles quoted fields). The template header uses `englishName（中文注释）` format. The parser strips Chinese annotations via regex `replace(/（[^）]*）/, '')` before matching English field names. Import sends a single `POST /api/admin/qa/batch-create` with `{ items: [...] }`. Duplicate detection checks existing questions before inserting.

### Database migrations

There is no Alembic/Flyway. Use `init_db.py` for initial table creation. For incremental changes (e.g., adding indexes), run ALTER TABLE statements directly in MySQL. The models in `models/` are the schema source of truth.

### Key design patterns
- **No Pinia/Vuex** — components manage their own state with `ref()`/`reactive()`. Data is fetched per-page in `onMounted`.
- **Server-side pagination** — admin list endpoints accept `page`/`pageSize` params, return `{ list, total }`. Frontend uses `el-pagination`.
- **Batch operations** — admin QA, feedback, users, and chat logs support batch delete and batch status update.
- **Decorator-based auth** — `@login_required_user` and `@admin_required` wrap Flask routes. No middleware-style auth.
- **Thread-safe singletons** — Embedding model and FAISS store use `RLock` + double-check pattern to avoid reloading.
- **Soft deletes** — QA "delete" sets status to "已停用" rather than removing rows. Hard delete available via `?hard=true`.
- **API response convention** — All endpoints return `{ code: 200, message: "...", data: ... }`. The axios interceptor checks `code !== 200` as an error.
- **SessionStorage for auth** — Token, role, and username stored in sessionStorage. No refresh token mechanism.
- **Forced password change** — Users with `must_change_password=true` get 423 on any authenticated request; frontend redirects to `/change-password`.
