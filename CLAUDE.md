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

The backend `.env` file lives at `property_kb_backend/.env`. Set `DEEPSEEK_API_KEY`, `DATABASE_URL`, and optionally `CORS_ORIGINS`, `SECRET_KEY`, `JWT_SECRET_KEY` there.

## Architecture overview

**Stack**: Vue 3 (Composition API, `<script setup>`) + Element Plus + Vite on the frontend / Flask + Flask-SQLAlchemy + Flask-JWT-Extended + FAISS on the backend. MySQL for structured data, FAISS flat index on disk for vector search.

### Frontend (`src/`)

- `src/main.js` — App entry: mounts Vue, installs Element Plus + all icons globally, installs router.
- `src/App.vue` — Just `<router-view />`.
- `src/router/index.js` — Two top-level layouts:
  - `/user/*` → `UserLayout` (sidebar: home, knowledge base, chat, history, feedback)
  - `/admin/*` → `AdminLayout` (sidebar: dashboard, qa, category, feedback, logs, vector)
  - `/login` — public; `/` redirects based on stored token/role.
  - Route guards check `sessionStorage` for token and role; admins can't visit `/user` and vice versa.
- `src/utils/request.js` — Axios instance with base URL from `VITE_API_BASE_URL` env var. Injects Bearer token. Caches GET responses in-memory (Map with 30s TTL in `src/utils/cache.js`) and returns cached data via a custom axios adapter. Mutations (POST/PUT/DELETE) clear related cache entries. `result.code !== 200` or 401/403 triggers ElMessage and redirects to login.
- `src/api/*.js` — Thin wrappers around `request` for each resource (qa, auth, chat, feedback, dashboard, vector, admin*). Frontend calls these directly; there is no store/vuex/pinia.
- `src/layouts/` — `UserLayout.vue` and `AdminLayout.vue` each have a sticky sidebar, top bar with user info, and `<router-view>` for page content.
- `src/views/` — Page components organized by `user/` and `admin/`. Each page fetches its own data in `onMounted` and manages local `ref` state — no shared store.

### Backend (`property_kb_backend/`)

- `app.py` — `create_app()` factory wires up Flask, CORS, JWT, SQLAlchemy, and registers 9 blueprints under `/api/*`. Calls `warm_up_embeddings()` and `preload_faiss_index()` on startup to pre-cache models. Module-level `app` at import time.
- `config.py` — `Config` class read by Flask. All values from env vars with defaults.
- `extensions/db.py` — Single `SQLAlchemy()` instance imported by models and routes.
- `utils/auth.py` — Two decorators:
  - `@login_required_user` — JWT required + user must exist and be "启用"
  - `@admin_required` — same + role must be "admin"
- `utils/response.py` — `success(data, message)` and `fail(message, code)` helpers, both return `{ code, message, data }` JSON.

**Route blueprints (all use `/api` prefix)**:

| Blueprint | Prefix | Decorator | Purpose |
|---|---|---|---|
| `auth_bp` | `/api/auth` | public | login, register |
| `qa_bp` | `/api/qa` | `@login_required_user` | list, detail, categories |
| `chat_bp` | `/api/chat` | `@login_required_user` | RAG question answering |
| `feedback_bp` | `/api/feedback` | `@login_required_user` | submit feedback, user's feedback list |
| `admin_qa_bp` | `/api/admin/qa` | `@admin_required` | CRUD + batch-create QA |
| `admin_category_bp` | `/api/admin/category` | `@admin_required` | CRUD categories |
| `admin_feedback_bp` | `/api/admin/feedback` | `@admin_required` | list/update feedback, feedback-to-knowledge |
| `admin_chat_logs_bp` | `/api/admin` | `@admin_required` | list chat logs |
| `admin_dashboard_bp` | `/api/admin/dashboard` | `@admin_required` | overview, trends, hot questions, stats |
| `vector_bp` | `/api/admin/vector` | `@admin_required` | rebuild/check FAISS index |

**Models** — SQLAlchemy ORM models in `models/`, all use `to_dict()` for camelCase JSON serialization:

- `User` (`users`) — username, email, password_hash, role (user/admin), nickname, status
- `QaKnowledge` (`qa_knowledge`) — question, answer, category, keywords (comma-separated string), view_count, ask_count, status (已发布/草稿/待审核/已停用), source
- `Category` (`categories`) — name (unique), description, question_count, sort_order, status (启用/停用)
- `ChatLog` (`chat_logs`) — user_id, username, question, answer, category, similarity (0–1), hit_status (已命中/未命中), need_human, response_time
- `Feedback` (`feedback`) — user_id, chat_log_id, qa_id, user_question, ai_answer, feedback_type (有帮助/没帮助/需要人工), suggestion, status (待处理/处理中/已处理/已忽略), admin_reply

**Services** — Business logic layer in `services/`:

- `category_service.py` — `ensure_category(name, description)` creates or updates categories. `refresh_category_question_count()` syncs counts.
- `dashboard_service.py` — Aggregation queries using SQLAlchemy `func` with GROUP BY. `get_daily_trend()`, `get_hit_rate_trend()`, `get_hot_questions()`, `get_category_ratio()`, `get_feedback_status()`, `get_unmatched_questions()`.
- `feedback_metrics.py` — `get_helpful_rate_summary()` computes helpful rate stats.

### RAG pipeline (`property_kb_backend/rag/`)

1. `document_builder.py` — Reads `qa_knowledge` rows with `status='已发布'`, builds LangChain `Document` objects with structured `page_content` (分类/问题/关键词/答案) and metadata.
2. `embeddings.py` — Thread-safe singleton wrapping `HuggingFaceEmbeddings` with `BAAI/bge-small-zh-v1.5`. Model cached to `HF_CACHE_DIR` (default `storage/hf_cache`). `preload_embedding_model()` for warmup.
3. `faiss_store.py` — Thread-safe singleton for FAISS vector store. `build_faiss_index()` loads published docs, builds index, saves to `FAISS_INDEX_DIR` (default `storage/faiss_index/`), caches in memory. `load_faiss_index()` loads from disk into memory cache. `search_similar_docs()` returns `[(doc, distance), ...]`. `preload_faiss_index()` for startup warmup.
4. `llm_client.py` — Singleton OpenAI-compatible client targeting DeepSeek API. `call_deepseek(prompt)` sends system+user messages, returns content. API key is stripped from error messages.
5. `rag_service.py` — Orchestrator: `rag_answer(question, user)` calls FAISS search → checks distance threshold → builds prompt → calls DeepSeek → saves ChatLog → returns result with hit status and trace info. Handles empty index, no results, low similarity, and LLM failures (falls back to knowledge base answer or `FALLBACK_ANSWER`).
6. `prompt.py` — `build_prompt(context, question)` constructs the system prompt with knowledge context. `FALLBACK_ANSWER` is the "contact human support" message.
7. `config.py` — Loads `.env` from backend dir or repo root. All RAG settings via env vars: `RAG_TOP_K` (3), `RAG_MAX_DISTANCE_THRESHOLD` (1.2), `RAG_PRELOAD_EMBEDDINGS`, `HF_CACHE_DIR`, `EMBEDDING_MODEL_NAME`.

### Data flow for a user question

```
User types question in ChatAgent.vue
  → POST /api/chat/ask { question }
  → chat_bp → rag_service.rag_answer(question, user)
    → search_similar_docs(question)  # FAISS similarity_search_with_score
    → if hit: build_prompt → call_deepseek → save ChatLog
    → if miss: save ChatLog with FALLBACK_ANSWER
  → response with { answer, category, similarity, hitStatus, needHuman, ... }
  → ChatAgent.vue renders answer + shows feedback buttons
```

### CSV batch import

`QaManage.vue` supports CSV import with inline parsing (character-by-character, handles quoted fields). The template header uses `englishName（中文注释）` format. The parser strips Chinese annotations via regex `replace(/（[^）]*）/, '')` before matching English field names. Import sends a single `POST /api/admin/qa/batch-create` with `{ items: [...] }`.

### Database migrations

There is no Alembic/Flyway. Use `init_db.py` for initial table creation. For incremental changes (e.g., adding indexes), run ALTER TABLE statements directly in MySQL. The models in `models/` are the schema source of truth.

### Key design patterns
- **No Pinia/Vuex** — components manage their own state with `ref()`/`reactive()`. Data is fetched per-page in `onMounted`.
- **Decorator-based auth** — `@login_required_user` and `@admin_required` wrap Flask routes. No middleware-style auth.
- **Thread-safe singletons** — Embedding model and FAISS store use `RLock` + double-check pattern to avoid reloading.
- **Soft deletes** — QA "delete" sets status to "已停用" rather than removing rows.
- **API response convention** — All endpoints return `{ code: 200, message: "...", data: ... }`. The axios interceptor checks `code !== 200` as an error.
- **SessionStorage for auth** — Token, role, and username stored in sessionStorage. No refresh token mechanism.
