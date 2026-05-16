# 智慧物业知识库咨询平台

面向物业服务场景的 Web 系统，集成 RAG 向量检索与大模型问答能力。业主可通过在线知识库和智能问答快速获取缴费、报修、停车、装修等常见问题答案；管理员可维护标准问答、处理反馈、分析咨询数据，持续优化系统回答质量。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Vite |
| 后端 | Flask + Flask-JWT-Extended + Flask-SQLAlchemy |
| 数据库 | MySQL 8 |
| 向量检索 | FAISS + HuggingFace (BAAI/bge-small-zh-v1.5) |
| 大模型 | 智谱AI GLM-4.5-Air |

## 功能概览

### 用户端

- **在线知识库** — 关键词搜索、分类筛选、查看详情、复制答案
- **智能问答** — 自然语言提问，RAG 检索 + 大模型生成回答
- **咨询记录** — 查看历史提问、命中状态、相似度
- **反馈管理** — 对回答提交有帮助/没帮助/需要人工反馈

### 管理端

- **知识库维护** — CRUD 问答、CSV 批量导入、发布/停用
- **分类管理** — 维护知识分类结构
- **反馈处理** — 查看反馈、标记处理、加入知识库
- **咨询日志** — 筛选未命中问题、沉淀到知识库
- **数据看板** — 咨询趋势、命中率、分类分布
- **向量库维护** — 查看状态、重建 FAISS 索引

## 环境要求

- Node.js 18+
- Python 3.10+
- MySQL 8+
- 智谱AI API Key（[申请地址](https://open.bigmodel.cn/)）

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

# 智谱AI
BIGMODEL_API_KEY=your-api-key
BIGMODEL_BASE_URL=https://open.bigmodel.cn/api/paas/v4
BIGMODEL_MODEL=GLM-4.5-Air

# RAG
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
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
│   ├── api/                      # API 请求模块
│   ├── layouts/                  # 布局组件（用户端/管理端）
│   ├── router/                   # 路由配置
│   ├── utils/                    # 工具函数（axios 封装、缓存）
│   └── views/                    # 页面组件
│       ├── user/                 # 用户端页面
│       └── admin/                # 管理端页面
├── property_kb_backend/          # 后端源码
│   ├── models/                   # SQLAlchemy 数据模型
│   ├── routes/                   # API 路由蓝图
│   ├── services/                 # 业务逻辑层
│   ├── rag/                      # RAG 问答管道
│   │   ├── document_builder.py   # 文档构建
│   │   ├── embeddings.py         # Embedding 模型
│   │   ├── faiss_store.py        # FAISS 向量库
│   │   ├── llm_client.py         # 大模型客户端
│   │   └── rag_service.py        # RAG 编排服务
│   ├── storage/                  # 本地存储（FAISS 索引、模型缓存）
│   ├── app.py                    # Flask 应用工厂
│   ├── config.py                 # 配置加载
│   └── .env                      # 环境变量（不提交到 Git）
└── .env                          # 前端环境变量
```

## RAG 问答流程

```
用户提问 → FAISS 向量检索 → 相似度阈值判断
  ├─ 命中 → 构建 Prompt → 调用智谱AI → 返回回答
  └─ 未命中 → 返回知识库标准答案或"联系人工客服"
```

- Embedding 模型：`BAAI/bge-small-zh-v1.5`（中文语义向量）
- 向量库：FAISS flat 索引，存储于 `storage/faiss_index/`
- 仅"已发布"状态的知识参与检索

## 常见问题

**Q: 首次提问响应慢？**
A: 首次需加载 Embedding 模型，保持 `RAG_PRELOAD_EMBEDDINGS=true` 可在启动时预热。

**Q: 新增知识后未命中？**
A: 确认问答状态为"已发布"，并执行"重建向量库"。

**Q: 向量库重建失败？**
A: 检查是否有已发布知识、MySQL 连接是否正常、`storage/` 目录是否有写入权限。

## License

MIT
