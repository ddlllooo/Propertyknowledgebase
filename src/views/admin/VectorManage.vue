<template>
  <div class="vector-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>RAG Vector Store</el-tag>
        <h1>向量库维护</h1>
        <p>将标准问答内容向量化，为 RAG 智能问答提供检索能力。</p>
      </div>
      <el-button type="primary" :icon="Refresh" :loading="rebuildLoading" @click="handleRebuild">
        重建向量库
      </el-button>
    </section>

    <section class="status-grid">
      <article v-for="item in statusCards" :key="item.label" class="status-card">
        <div class="status-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </article>
    </section>

    <section class="flow-card">
      <div class="section-head">
        <div>
          <h2>向量库构建流程</h2>
          <span>从业务知识到可检索向量索引的完整链路</span>
        </div>
        <el-tag type="success" round>{{ ragStatus }}</el-tag>
      </div>

      <el-steps :active="5" align-center finish-status="success">
        <el-step v-for="step in buildSteps" :key="step.title" :title="step.title" :description="step.desc" />
      </el-steps>

      <div class="tech-strip">
        <div>
          <span>切片数量</span>
          <strong>{{ vectorInfo.ragStatus.chunkCount }}</strong>
        </div>
        <div>
          <span>平均相似度</span>
          <strong>{{ Math.round(vectorInfo.ragStatus.avgSimilarity * 100) }}%</strong>
        </div>
        <div>
          <span>同步结果</span>
          <strong>{{ vectorInfo.ragStatus.lastSyncResult }}</strong>
        </div>
        <div>
          <span>待同步知识</span>
          <strong>{{ vectorInfo.ragStatus.pendingSyncCount }}</strong>
        </div>
      </div>
    </section>

    <section class="bottom-grid">
      <article class="rebuild-card">
        <div class="section-head">
          <div>
            <h2>手动重建</h2>
            <span>知识库新增或修改后，可手动更新检索索引</span>
          </div>
        </div>
        <div class="rebuild-visual">
          <div class="pulse-ring">
            <el-icon><Connection /></el-icon>
          </div>
          <div>
            <strong>{{ rebuildLoading ? '正在重建向量库' : '向量库状态正常' }}</strong>
            <p>{{ rebuildLoading ? '正在执行文本切分、Embedding 和 FAISS 写入。' : '当前 RAG 检索服务可正常调用。' }}</p>
          </div>
        </div>
        <el-button type="primary" :icon="Refresh" :loading="rebuildLoading" @click="handleRebuild">
          重建向量库
        </el-button>
      </article>

      <article class="notice-card">
        <div class="section-head">
          <div>
            <h2>注意事项</h2>
            <span>演示环境与后续扩展方向</span>
          </div>
        </div>
        <ul>
          <li v-for="item in notices" :key="item">
            <el-icon><CircleCheck /></el-icon>
            <span>{{ item }}</span>
          </li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, Connection, Refresh } from '@element-plus/icons-vue'
import { vectorStatus } from '../../mock/mockData'

const rebuildLoading = ref(false)

const vectorInfo = reactive({
  ...vectorStatus,
  status: '正常',
  knowledgeCount: 60,
  lastBuildTime: '2026-04-29 10:30:00',
  vectorStore: 'FAISS',
  embeddingModel: 'bge-small-zh',
  ragStatus: {
    ...vectorStatus.ragStatus,
    serviceStatus: '运行中'
  }
})

const ragStatus = computed(() => vectorInfo.ragStatus.serviceStatus || '运行中')

const statusCards = computed(() => [
  {
    label: '向量库状态',
    value: vectorInfo.status,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '当前知识条数',
    value: vectorInfo.knowledgeCount,
    icon: 'Collection',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '最后重建时间',
    value: vectorInfo.lastBuildTime,
    icon: 'Timer',
    color: 'linear-gradient(135deg, #7c6cff, #9f94ff)'
  },
  {
    label: '使用向量库',
    value: vectorInfo.vectorStore,
    icon: 'Cpu',
    color: 'linear-gradient(135deg, #20b486, #74d3b4)'
  },
  {
    label: 'Embedding 模型',
    value: vectorInfo.embeddingModel,
    icon: 'Connection',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  },
  {
    label: 'RAG 服务状态',
    value: ragStatus.value,
    icon: 'Monitor',
    color: 'linear-gradient(135deg, #0f8bd9, #13bea7)'
  }
])

const buildSteps = [
  { title: '读取 MySQL 知识库', desc: '读取标准问答、分类与关键词' },
  { title: '文本切分', desc: '生成适合检索的知识片段' },
  { title: 'Embedding 向量化', desc: '调用 bge-small-zh 生成语义向量' },
  { title: '写入 FAISS', desc: '更新本地向量索引' },
  { title: 'RAG 检索调用', desc: '为智能问答提供召回能力' }
]

const notices = [
  '新增或修改知识库后建议重建向量库',
  '重建期间智能问答可能短暂不可用',
  '当前演示阶段使用模拟数据',
  '后续可接入 LangChain + FAISS 实现真实向量库更新'
]

const formatNow = () => {
  const date = new Date()
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(
    date.getMinutes()
  )}:${pad(date.getSeconds())}`
}

const handleRebuild = async () => {
  await ElMessageBox.confirm('确认重新构建向量库索引吗？重建期间智能问答可能短暂不可用。', '重建向量库', {
    type: 'info',
    confirmButtonText: '开始重建',
    cancelButtonText: '取消'
  })

  rebuildLoading.value = true
  setTimeout(() => {
    vectorInfo.lastBuildTime = formatNow()
    vectorInfo.status = '正常'
    vectorInfo.ragStatus.lastSyncResult = '成功'
    vectorInfo.ragStatus.pendingSyncCount = 0
    rebuildLoading.value = false
    ElMessage.success('向量库重建成功')
  }, 2000)
}
</script>

<style scoped>
.vector-page {
  display: grid;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
}

.title-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  padding: 32px;
  border-radius: 26px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(17, 120, 255, 0.96), rgba(19, 190, 167, 0.86)),
    url("https://images.unsplash.com/photo-1518779578993-ec3579fee39f?auto=format&fit=crop&w=1400&q=80")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 22px 52px rgba(16, 108, 191, 0.2);
}

.title-tag {
  border: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
}

.title-panel h1 {
  margin: 22px 0 10px;
  font-size: clamp(30px, 4vw, 46px);
}

.title-panel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
}

.title-panel .el-button {
  border: 0;
  color: #1178ff;
  background: #fff;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.status-card,
.flow-card,
.rebuild-card,
.notice-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 118px;
  padding: 22px;
  border-radius: 20px;
}

.status-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 50px;
  height: 50px;
  border-radius: 16px;
  color: #fff;
  font-size: 22px;
}

.status-card span {
  display: block;
  color: #6b7c93;
  font-size: 13px;
}

.status-card strong {
  display: block;
  margin-top: 7px;
  color: #172b4d;
  font-size: 22px;
  line-height: 1.35;
}

.flow-card,
.rebuild-card,
.notice-card {
  padding: 26px;
  border-radius: 22px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.section-head h2 {
  margin: 0;
  color: #172b4d;
  font-size: 22px;
}

.section-head span {
  display: block;
  margin-top: 6px;
  color: #7b8fa6;
  font-size: 13px;
}

.flow-card :deep(.el-step__title.is-success) {
  color: #172b4d;
  font-weight: 700;
}

.flow-card :deep(.el-step__description.is-success) {
  color: #6b7c93;
}

.tech-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 28px;
}

.tech-strip > div {
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(120deg, #f0f7ff, #effbf8);
}

.tech-strip span,
.tech-strip strong {
  display: block;
}

.tech-strip span {
  color: #6b7c93;
  font-size: 13px;
}

.tech-strip strong {
  margin-top: 8px;
  color: #1178ff;
  font-size: 24px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1.1fr);
  gap: 18px;
}

.rebuild-visual {
  display: flex;
  align-items: center;
  gap: 18px;
  min-height: 150px;
  padding: 20px;
  border-radius: 20px;
  background: linear-gradient(120deg, #eef7ff, #ecfbf8);
}

.pulse-ring {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  color: #fff;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  box-shadow: 0 0 0 14px rgba(17, 120, 255, 0.1);
  font-size: 34px;
}

.rebuild-visual strong {
  color: #172b4d;
  font-size: 22px;
}

.rebuild-visual p {
  margin: 8px 0 0;
  color: #5d7188;
  line-height: 1.75;
}

.rebuild-card > .el-button {
  margin-top: 18px;
}

.notice-card ul {
  display: grid;
  gap: 14px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.notice-card li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 14px;
  color: #465f78;
  background: #f6faff;
}

.notice-card li .el-icon {
  color: #13bea7;
}

@media (max-width: 1020px) {
  .status-grid,
  .tech-strip,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .title-panel {
    flex-direction: column;
  }
}
</style>
