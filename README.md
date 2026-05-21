# 智慧物业知识库咨询平台

面向物业服务场景的 Web 系统，集成 RAG 向量检索与大模型问答能力。业主可通过在线知识库和智能问答快速获取缴费、报修、停车、装修等常见问题答案；管理员可维护标准问答、处理反馈、分析咨询数据，持续优化系统回答质量。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Vite |
| 后端 | Flask + Flask-JWT-Extended + Flask-SQLAlchemy |
| 数据库 | MySQL 8 |
| 向量检索 | FAISS + HuggingFace (embedding-3) |
| 大模型 | 智谱AI GLM-4.5-Air |

## 功能概览

### 用户端

- **首页** — 统计概览、高频问题推荐、快捷入口
- **在线知识库** — 关键词搜索、分类筛选、查看详情、复制答案
- **智能问答** — 自然语言提问，RAG 检索 + 大模型生成回答，支持游客免登录体验（每日 10 次限制）
- **咨询记录** — 查看历史提问、命中状态、相似度
- **反馈管理** — 对回答提交有帮助/没帮助/需要人工反馈

### 管理端

- **工作台** — 核心指标概览、快捷操作、最近反馈与未命中问题
- **知识库维护** — CRUD 问答、CSV 批量导入、发布/停用
- **分类管理** — 维护知识分类结构
- **反馈处理** — 查看反馈、标记处理、加入知识库
- **咨询日志** — 筛选未命中问题、沉淀到知识库
- **数据看板** — 咨询趋势、命中率、分类分布
- **用户管理** — CRUD 用户、启用/停用、重置密码
- **密码重置管理** — 处理用户发起的密码重置请求，生成临时密码
- **向量库维护** — 查看状态、重建 FAISS 索引

### 账号体系

- **用户注册** — 姓名 + 邮箱 + 验证码注册，密码需包含字母和数字
- **游客模式** — 无需登录即可体验智能问答，每日 10 次限制
- **记住我** — 勾选后 Token 有效期延长至 30 天
- **密码重置** — 用户提交重置请求，管理员生成临时密码，用户首次登录后强制修改
- **登录保护** — 注册/登录接口限流，图形验证码防刷

## 环境要求

- Node.js 18+
- Python 3.10+
- MySQL 8+
- 智谱AI API Key（[申请地址](https://open.bigmodel.cn/)）
- 操作系统：Windows / macOS / Linux

## 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/ddlllooo/Propertyknowledgebase.git
cd Propertyknowledgebase
```

### 2. 安装前端依赖

```bash
npm install
```

### 3. 安装后端依赖

```bash
cd property_kb_backend
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. 配置环境变量

**后端** `property_kb_backend/.env`：

```env
# Flask
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/property_kb?charset=utf8mb4

# CORS
CORS_ORIGINS=http://localhost:5173

# 智谱AI
BIGMODEL_API_KEY=your-api-key
BIGMODEL_BASE_URL=https://open.bigmodel.cn/api/paas/v4
BIGMODEL_MODEL=GLM-4.5-Air

# Embedding
EMBEDDING_MODEL_NAME=embedding-3
EMBEDDING_DIMENSIONS=1024

# RAG
HF_CACHE_DIR=storage/hf_cache
FAISS_INDEX_DIR=storage/faiss_index
RAG_TOP_K=3
RAG_MAX_DISTANCE_THRESHOLD=1.2
RAG_PRELOAD_EMBEDDINGS=true
```

**前端** 根目录 `.env`：

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### 5. 初始化数据库

```sql
CREATE DATABASE property_kb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
cd property_kb_backend
python init_db.py
python seed_data.py
```

默认账号：

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | 123456 |
| 普通用户 | user | 123456 |

### 6. 启动服务

```bash
# 后端（property_kb_backend/ 目录）
python app.py

# 前端（项目根目录）
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
Propertyknowledgebase/
├── src/                          # 前端源码
│   ├── api/                      # API 请求模块（12 个模块）
│   ├── composables/              # 组合式函数（响应式断点、对话框宽度）
│   ├── layouts/                  # 布局组件（UserLayout / AdminLayout）
│   ├── router/                   # 路由配置（含角色守卫、游客限制）
│   ├── styles/                   # 全局样式
│   ├── utils/                    # 工具函数（axios 封装、内存缓存）
│   └── views/                    # 页面组件
│       ├── user/                 # 用户端（首页、知识库、问答、历史、反馈）
│       └── admin/                # 管理端（工作台、知识库、分类、反馈、看板等）
├── property_kb_backend/          # 后端源码
│   ├── models/                   # SQLAlchemy 数据模型（6 个）
│   ├── routes/                   # API 路由蓝图（12 个）
│   ├── services/                 # 业务逻辑层（分类、看板、反馈指标）
│   ├── rag/                      # RAG 问答管道
│   │   ├── document_builder.py   # 文档构建
│   │   ├── embeddings.py         # Embedding 模型
│   │   ├── faiss_store.py        # FAISS 向量库
│   │   ├── llm_client.py         # 大模型客户端
│   │   └── rag_service.py        # RAG 编排服务
│   ├── extensions/               # Flask 扩展（db、limiter）
│   ├── utils/                    # 工具（鉴权装饰器、响应格式化）
│   ├── storage/                  # 本地存储（FAISS 索引、模型缓存）
│   ├── app.py                    # Flask 应用工厂
│   ├── config.py                 # 配置加载
│   ├── init_db.py                # 建表脚本
│   ├── seed_data.py              # 示例数据填充
│   └── .env                      # 环境变量（不提交到 Git）
├── public/                       # 静态资源（图片）
├── .env                          # 前端环境变量
└── vite.config.js                # Vite 配置
```

## RAG 问答流程

```
用户提问 → FAISS 向量检索 → 相似度阈值判断
  ├─ 命中 → 构建 Prompt → 调用智谱AI → 返回回答
  └─ 未命中 → 返回知识库标准答案或"联系人工客服"
```

- Embedding 模型：`embedding-3`（中文语义向量）
- 向量库：FAISS flat 索引，存储于 `storage/faiss_index/`
- 仅"已发布"状态的知识参与检索

## API 路由一览

| 前缀 | 鉴权 | 用途 |
|------|------|------|
| `/api/auth` | 公开 | 登录、注册、游客登录、验证码、密码重置、修改密码 |
| `/api/qa` | 用户 | 知识库列表、详情、分类、首页摘要 |
| `/api/chat` | 用户 | RAG 问答、我的历史 |
| `/api/feedback` | 用户 | 提交反馈、我的反馈列表 |
| `/api/admin/qa` | 管理员 | 知识库 CRUD + 批量操作 |
| `/api/admin/category` | 管理员 | 分类 CRUD |
| `/api/admin/feedback` | 管理员 | 反馈列表/更新/删除/转入知识库 |
| `/api/admin/password-reset` | 管理员 | 密码重置请求列表/重置/忽略 |
| `/api/admin/user` | 管理员 | 用户 CRUD + 批量操作 |
| `/api/admin` | 管理员 | 咨询日志列表/删除/统计 |
| `/api/admin/dashboard` | 管理员 | 看板数据（概览、趋势、热门问题） |
| `/api/admin/vector` | 管理员 | FAISS 索引状态与重建 |

## 常见问题

**Q: 首次提问响应慢？**
A: 首次需加载 Embedding 模型，保持 `RAG_PRELOAD_EMBEDDINGS=true` 可在启动时预热。

**Q: 新增知识后未命中？**
A: 确认问答状态为"已发布"，并执行"重建向量库"。

**Q: 向量库重建失败？**
A: 检查是否有已发布知识、MySQL 连接是否正常、`storage/` 目录是否有写入权限。

**Q: 游客模式和正式用户有什么区别？**
A: 游客可使用智能问答（每日 10 次），但无法查看知识库详情、提交反馈或查看咨询记录。

**Q: 忘记密码怎么办？**
A: 在登录页点击"忘记密码"提交重置请求，等待管理员生成临时密码。使用临时密码登录后系统会强制要求修改密码。

**Q: 前端请求被缓存导致数据不更新？**
A: 系统对 GET 请求有 30 秒内存缓存。切换路由时自动清除；手动操作后如需立即刷新，可在请求参数中添加 `_noCache: true`。

## License

MIT
