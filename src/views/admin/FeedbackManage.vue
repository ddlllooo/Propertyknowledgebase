<template>
  <div class="feedback-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Feedback Loop</el-tag>
        <h1>反馈处理</h1>
        <p>收集用户对回答质量的评价，将未命中或低质量回答转化为知识库优化任务。</p>
      </div>
      <div class="loop-line">
        <span>用户反馈</span>
        <el-icon><ArrowRight /></el-icon>
        <span>管理员处理</span>
        <el-icon><ArrowRight /></el-icon>
        <span>补充知识库</span>
      </div>
    </section>

    <section class="stat-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <div class="stat-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="filter-card">
      <el-select v-model="filters.status" placeholder="状态筛选">
        <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="filters.type" placeholder="反馈类型">
        <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-input v-model="filters.keyword" clearable placeholder="搜索问题、回答或建议" :prefix-icon="Search" />
    </section>

    <section v-loading="loading" class="feedback-list">
      <article v-for="item in filteredFeedback" :key="item.id" class="feedback-card">
        <div class="card-main">
          <div class="question-block">
            <div class="card-head">
              <h2>{{ item.userQuestion }}</h2>
              <div class="tag-row">
                <el-tag :type="typeTagMap[item.feedbackType]" round>{{ item.feedbackType }}</el-tag>
                <el-tag :type="statusTypeMap[item.status]" round>{{ item.status }}</el-tag>
              </div>
            </div>
            <p class="answer">AI 回答：{{ item.aiAnswer }}</p>
            <p class="suggestion">用户建议：{{ item.suggestion }}</p>
            <div class="meta-row">
              <span>{{ item.category }}</span>
              <span>相似度 {{ Math.round(item.similarity * 100) }}%</span>
              <span>{{ item.createdAt }}</span>
            </div>
          </div>
          <div class="action-column">
            <el-button type="primary" text @click="openDetail(item)">查看详情</el-button>
            <el-button type="success" text @click="openKnowledgeDialog(item)">加入知识库</el-button>
            <el-button type="warning" text @click="openProcessDialog(item)">标记已处理</el-button>
            <el-button type="info" text @click="ignoreFeedback(item)">忽略</el-button>
            <el-button type="danger" text @click="handleDeleteFeedback(item)">删除</el-button>
          </div>
        </div>
      </article>
    </section>

    <el-empty v-if="filteredFeedback.length === 0" description="暂无匹配反馈" />

    <el-dialog v-model="detailVisible" title="反馈详情" :width="detailDialogWidth">
      <template v-if="activeFeedback">
        <div class="detail-grid">
          <div class="detail-item wide">
            <span>用户问题</span>
            <p>{{ activeFeedback.userQuestion }}</p>
          </div>
          <div class="detail-item wide">
            <span>AI 回答</span>
            <p>{{ activeFeedback.aiAnswer }}</p>
          </div>
          <div class="detail-item">
            <span>命中分类</span>
            <el-tag round>{{ activeFeedback.category }}</el-tag>
          </div>
          <div class="detail-item">
            <span>相似度</span>
            <strong>{{ Math.round(activeFeedback.similarity * 100) }}%</strong>
          </div>
          <div class="detail-item">
            <span>反馈类型</span>
            <el-tag :type="typeTagMap[activeFeedback.feedbackType]" round>
              {{ activeFeedback.feedbackType }}
            </el-tag>
          </div>
          <div class="detail-item wide">
            <span>用户建议</span>
            <p>{{ activeFeedback.suggestion }}</p>
          </div>
          <div class="detail-item wide">
            <span>管理员处理说明</span>
            <el-input
              v-model="processRemark"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="请输入处理说明，例如已补充知识、转人工核实、无需调整等"
            />
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="markProcessedFromDetail">保存并标记已处理</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="processVisible" title="标记已处理" :width="processDialogWidth">
      <el-form label-position="top">
        <el-form-item label="管理员处理说明">
          <el-input
            v-model="processRemark"
            type="textarea"
            :rows="5"
            resize="none"
            placeholder="请填写本次反馈的处理说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processVisible = false">取消</el-button>
        <el-button type="primary" @click="markProcessed">确认处理</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="knowledgeVisible" title="加入知识库" :width="knowledgeDialogWidth">
      <el-form ref="knowledgeFormRef" :model="knowledgeForm" :rules="knowledgeRules" label-position="top">
        <el-form-item label="标准问题" prop="question">
          <el-input v-model="knowledgeForm.question" />
        </el-form-item>
        <el-form-item label="标准答案" prop="answer">
          <el-input v-model="knowledgeForm.answer" type="textarea" :rows="5" resize="none" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="分类" prop="category">
            <el-select v-model="knowledgeForm.category">
              <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据来源" prop="source">
            <el-input v-model="knowledgeForm.source" />
          </el-form-item>
        </div>
        <el-form-item label="关键词" prop="keywords">
          <el-select
            v-model="knowledgeForm.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后回车添加"
          >
            <el-option v-for="item in keywordOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="knowledgeVisible = false">取消</el-button>
        <el-button type="primary" @click="saveToKnowledgeBase">保存到知识库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, Search } from '@element-plus/icons-vue'
import { useDialogWidth } from '../../composables/useDialogWidth'
import { getCategoryList } from '../../api/adminCategory'
import { deleteFeedback, feedbackToKnowledge, getFeedbackList, updateFeedbackStatus } from '../../api/adminFeedback'
import { getAdminQaList } from '../../api/adminQa'

const detailDialogWidth = useDialogWidth(720)
const processDialogWidth = useDialogWidth(520)
const knowledgeDialogWidth = useDialogWidth(680)

const statusOptions = ['全部', '待处理', '处理中', '已处理', '已忽略']
const typeOptions = ['全部', '有帮助', '没帮助', '需要人工']
const categoryOptions = ref([])

const feedbackRecords = ref([])
const qaRecords = ref([])
const detailVisible = ref(false)
const processVisible = ref(false)
const knowledgeVisible = ref(false)
const activeFeedback = ref(null)
const processRemark = ref('')
const knowledgeFormRef = ref()
const loading = ref(false)

const filters = reactive({
  status: '全部',
  type: '全部',
  keyword: ''
})

const knowledgeForm = reactive({
  question: '',
  answer: '',
  category: '',
  keywords: [],
  source: '用户反馈'
})

const knowledgeRules = {
  question: [{ required: true, message: '请输入标准问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  keywords: [{ required: true, type: 'array', min: 1, message: '请至少填写一个关键词', trigger: 'change' }],
  source: [{ required: true, message: '请输入数据来源', trigger: 'blur' }]
}

const statusTypeMap = {
  待处理: 'warning',
  处理中: 'primary',
  已处理: 'success',
  已忽略: 'info'
}

const typeTagMap = {
  有帮助: 'success',
  没帮助: 'danger',
  需要人工: 'warning'
}

const stats = computed(() => [
  {
    label: '总反馈数',
    value: feedbackRecords.value.length,
    icon: 'MessageBox',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '待处理',
    value: feedbackRecords.value.filter((item) => item.status === '待处理').length,
    icon: 'Clock',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  },
  {
    label: '已处理',
    value: feedbackRecords.value.filter((item) => item.status === '已处理').length,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '没帮助反馈',
    value: feedbackRecords.value.filter((item) => item.feedbackType === '没帮助').length,
    icon: 'Warning',
    color: 'linear-gradient(135deg, #ff6b6b, #ff9b8a)'
  }
])

const keywordOptions = computed(() => [...new Set(qaRecords.value.flatMap((item) => item.keywords || []))])

const filteredFeedback = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase()

  return feedbackRecords.value.filter((item) => {
    const statusMatched = filters.status === '全部' || item.status === filters.status
    const typeMatched = filters.type === '全部' || item.feedbackType === filters.type
    const text = [item.userQuestion, item.aiAnswer, item.suggestion, item.category].join(' ').toLowerCase()
    const keywordMatched = !keyword || text.includes(keyword)
    return statusMatched && typeMatched && keywordMatched
  })
})

const setActive = (item) => {
  activeFeedback.value = item
  processRemark.value = item.adminReply === '暂无回复' ? '' : item.adminReply
}

const openDetail = (item) => {
  setActive(item)
  detailVisible.value = true
}

const openProcessDialog = (item) => {
  setActive(item)
  processVisible.value = true
}

const refreshFeedback = async () => {
  loading.value = true
  try {
    const response = await getFeedbackList({ page: 1, pageSize: 200 })
    feedbackRecords.value = response.data?.list || []
  } finally {
    loading.value = false
  }
}

const markProcessed = async () => {
  if (!activeFeedback.value) return
  await updateFeedbackStatus(activeFeedback.value.id, {
    status: '已处理',
    adminReply: processRemark.value || '管理员已处理该反馈。'
  })
  await refreshFeedback()
  processVisible.value = false
  ElMessage.success('已标记为已处理')
}

const markProcessedFromDetail = async () => {
  if (!activeFeedback.value) return
  await updateFeedbackStatus(activeFeedback.value.id, {
    status: '已处理',
    adminReply: processRemark.value || '管理员已处理该反馈。'
  })
  await refreshFeedback()
  detailVisible.value = false
  ElMessage.success('处理说明已保存')
}

const handleDeleteFeedback = async (item) => {
  await ElMessageBox.confirm(`确认删除这条反馈吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteFeedback(item.id)
  await refreshFeedback()
  ElMessage.success('反馈已删除')
}

const ignoreFeedback = async (item) => {
  await ElMessageBox.confirm(`确认忽略“${item.userQuestion}”这条反馈吗？`, '忽略确认', {
    type: 'warning',
    confirmButtonText: '忽略',
    cancelButtonText: '取消'
  })
  await updateFeedbackStatus(item.id, {
    status: '已忽略',
    adminReply: '该反馈已忽略，暂不调整知识库。'
  })
  await refreshFeedback()
  ElMessage.success('已忽略该反馈')
}

const openKnowledgeDialog = (item) => {
  setActive(item)
  Object.assign(knowledgeForm, {
    question: item.userQuestion,
    answer: item.aiAnswer,
    category: item.category,
    keywords: extractKeywords(item.userQuestion),
    source: '用户反馈'
  })
  knowledgeVisible.value = true
}

const extractKeywords = (text) => {
  const matched = categoryOptions.value.filter((item) => text.includes(item.slice(0, 2)))
  if (matched.length) return matched
  return activeFeedback.value?.category ? [activeFeedback.value.category] : []
}

const saveToKnowledgeBase = async () => {
  await knowledgeFormRef.value.validate()
  if (activeFeedback.value) {
    await feedbackToKnowledge(activeFeedback.value.id, {
      question: knowledgeForm.question,
      answer: knowledgeForm.answer,
      category: knowledgeForm.category,
      keywords: knowledgeForm.keywords
    })
    await refreshFeedback()
  }
  knowledgeVisible.value = false
  ElMessage.success('已加入知识库并标记反馈为已处理')
}

onMounted(async () => {
  loading.value = true
  try {
    const [categoryResponse, qaResponse] = await Promise.all([
      getCategoryList(),
      getAdminQaList({ page: 1, pageSize: 200 })
    ])
    categoryOptions.value = (categoryResponse.data || []).map((item) => item.name)
    qaRecords.value = qaResponse.data?.list || []
    await refreshFeedback()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.feedback-page {
  display: grid;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
}

.title-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 32px;
  border-radius: 26px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(17, 120, 255, 0.96), rgba(19, 190, 167, 0.86)),
    url("/images/bg-feedback-1400.jpg")
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
  max-width: 730px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
}

.loop-line {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  min-width: 360px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(14px);
}

.loop-line span {
  font-weight: 700;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.filter-card,
.feedback-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 116px;
  padding: 22px;
  border-radius: 20px;
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 50px;
  height: 50px;
  border-radius: 16px;
  color: #fff;
  font-size: 22px;
}

.stat-card strong {
  display: block;
  color: #172b4d;
  font-size: 30px;
  line-height: 1.1;
}

.stat-card span {
  display: block;
  margin-top: 7px;
  color: #6b7c93;
}

.filter-card {
  display: grid;
  grid-template-columns: 180px 180px minmax(280px, 1fr);
  gap: 12px;
  padding: 18px;
  border-radius: 20px;
}

.feedback-list {
  display: grid;
  gap: 16px;
}

.feedback-card {
  padding: 20px;
  border-radius: 22px;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.feedback-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 22px 46px rgba(21, 56, 98, 0.12);
}

.card-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 128px;
  gap: 18px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.card-head h2 {
  margin: 0;
  color: #172b4d;
  font-size: 19px;
  line-height: 1.45;
}

.tag-row,
.record-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.answer,
.suggestion {
  margin: 12px 0 0;
  color: #5d7188;
  line-height: 1.75;
}

.suggestion {
  color: #38536d;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.meta-row span {
  padding: 6px 10px;
  border-radius: 999px;
  color: #5d7188;
  background: #f1f7fc;
  font-size: 12px;
}

.action-column {
  display: grid;
  align-content: center;
  gap: 6px;
  justify-items: end;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.detail-item {
  padding: 15px;
  border-radius: 16px;
  background: #f6faff;
}

.detail-item.wide {
  grid-column: 1 / -1;
}

.detail-item span {
  display: block;
  margin-bottom: 8px;
  color: #7890a8;
  font-size: 13px;
}

.detail-item p {
  margin: 0;
  color: #354b63;
  line-height: 1.75;
}

.detail-item strong {
  color: #1178ff;
  font-size: 22px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

@media (max-width: 980px) {
  .title-panel {
    align-items: flex-start;
    flex-direction: column;
  }

  .loop-line {
    min-width: 0;
  }

  .stat-grid,
  .filter-card,
  .card-main,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .action-column {
    justify-items: start;
  }
}

@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .filter-card .filter-row {
    grid-template-columns: 1fr;
  }

  .card-main {
    flex-direction: column;
  }

  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
