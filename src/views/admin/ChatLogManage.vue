<template>
  <div class="log-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Consultation Analytics</el-tag>
        <h1>咨询日志</h1>
        <p>记录用户每一次智能问答咨询，帮助分析知识库覆盖情况。</p>
      </div>
      <div class="gap-card">
        <strong>{{ unmatchedCount }}</strong>
        <span>条未命中问题待优化</span>
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
      <el-input v-model="filters.keyword" clearable placeholder="搜索用户问题或回答" :prefix-icon="Search" @input="onKeywordInput" />
      <el-select v-model="filters.category" placeholder="分类筛选">
        <el-option label="全部分类" value="全部" />
        <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="filters.hitStatus" placeholder="命中状态">
        <el-option label="全部状态" value="全部" />
        <el-option label="已命中" value="已命中" />
        <el-option label="未命中" value="未命中" />
      </el-select>
      <el-select v-model="filters.needHuman" placeholder="人工处理">
        <el-option label="全部" value="全部" />
        <el-option label="需要人工" value="true" />
        <el-option label="无需人工" value="false" />
      </el-select>
      <el-date-picker
        v-model="filters.dateRange"
        type="daterange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
      />
      <el-button :type="filters.hitStatus === '未命中' ? 'primary' : 'danger'" plain @click="toggleUnmatchedOnly">
        {{ filters.hitStatus === '未命中' ? '查看全部咨询' : '仅查看未命中问题' }}
      </el-button>
      <el-button type="danger" :disabled="!selectedLogIds.length" @click="batchDeleteLogs">
        批量删除 {{ selectedLogIds.length ? `(${selectedLogIds.length})` : '' }}
      </el-button>
    </section>

    <section v-loading="loading" class="table-card">
      <el-table :data="logRecords" row-key="id" stripe @selection-change="onLogSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="createdAt" label="咨询时间" width="152" />
        <el-table-column prop="username" label="用户账号" width="110" />
        <el-table-column prop="question" label="用户问题" min-width="220">
          <template #default="{ row }">
            <strong class="question-text">{{ row.question }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="answer" label="系统回答摘要" min-width="250">
          <template #default="{ row }">
            <span class="answer-preview">{{ row.answer }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="命中分类" width="120">
          <template #default="{ row }">
            <el-tag round>{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="相似度" width="138">
          <template #default="{ row }">
            <div class="similarity-cell">
              <el-progress
                :percentage="Math.round(row.similarity * 100)"
                :stroke-width="8"
                :color="row.similarity >= 0.8 ? '#13bea7' : row.similarity >= 0.6 ? '#ffb020' : '#ff6b6b'"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="hitStatus" label="命中状态" width="104">
          <template #default="{ row }">
            <el-tag :type="row.hitStatus === '已命中' ? 'success' : 'danger'" round>{{ row.hitStatus }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="是否需要人工" width="116">
          <template #default="{ row }">
            <el-tag :type="row.needHuman ? 'warning' : 'info'" round>
              {{ row.needHuman ? '需要人工' : '无需人工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="响应耗时" width="96">
          <template #default="{ row }">{{ row.responseTime }}s</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link @click="openDetail(row)">详情</el-button>
              <el-button type="success" link @click="openKnowledgeDialog(row)">加入知识库</el-button>
              <el-button type="danger" link @click="handleDeleteLog(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </section>

    <el-dialog v-model="detailVisible" title="咨询详情" width="720px">
      <template v-if="activeLog">
        <div class="detail-grid">
          <div class="detail-item wide">
            <span>完整问题</span>
            <p>{{ activeLog.question }}</p>
          </div>
          <div class="detail-item wide">
            <span>完整回答</span>
            <p>{{ activeLog.answer }}</p>
          </div>
          <div class="detail-item">
            <span>用户账号</span>
            <strong>{{ activeLog.username }}</strong>
          </div>
          <div class="detail-item">
            <span>命中分类</span>
            <el-tag round>{{ activeLog.category }}</el-tag>
          </div>
          <div class="detail-item">
            <span>相似度</span>
            <strong>{{ Math.round(activeLog.similarity * 100) }}%</strong>
          </div>
          <div class="detail-item">
            <span>命中状态</span>
            <el-tag :type="activeLog.hitStatus === '已命中' ? 'success' : 'danger'" round>
              {{ activeLog.hitStatus }}
            </el-tag>
          </div>
          <div class="detail-item">
            <span>人工处理</span>
            <el-tag :type="activeLog.needHuman ? 'warning' : 'info'" round>
              {{ activeLog.needHuman ? '需要人工' : '无需人工' }}
            </el-tag>
          </div>
          <div class="detail-item">
            <span>响应耗时</span>
            <strong>{{ activeLog.responseTime }}s</strong>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="success" @click="openKnowledgeDialog(activeLog)">加入知识库</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="knowledgeVisible" title="加入知识库" width="680px">
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getCategoryList } from '../../api/adminCategory'
import { createQa, getAdminQaList } from '../../api/adminQa'
import { batchDeleteChatLogs, deleteChatLog, getChatLogs, getChatLogStats } from '../../api/adminLog'

const categoryOptions = ref([])
const logRecords = ref([])
const qaRecords = ref([])
const detailVisible = ref(false)
const knowledgeVisible = ref(false)
const activeLog = ref(null)
const knowledgeFormRef = ref()
const loading = ref(false)

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedLogIds = ref([])

const logStats = reactive({
  total: 0,
  todayCount: 0,
  hitCount: 0,
  unmatchedCount: 0,
  avgResponseTime: 0
})

const filters = reactive({
  keyword: '',
  category: '全部',
  hitStatus: '全部',
  needHuman: '全部',
  dateRange: []
})

const knowledgeForm = reactive({
  question: '',
  answer: '',
  category: '',
  keywords: [],
  source: '咨询日志未命中问题'
})

const knowledgeRules = {
  question: [{ required: true, message: '请输入标准问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  keywords: [{ required: true, type: 'array', min: 1, message: '请至少填写一个关键词', trigger: 'change' }],
  source: [{ required: true, message: '请输入数据来源', trigger: 'blur' }]
}

const stats = computed(() => [
  {
    label: '总咨询量',
    value: logStats.total,
    icon: 'ChatLineRound',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '今日咨询量',
    value: logStats.todayCount,
    icon: 'Calendar',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '已命中问题',
    value: logStats.hitCount,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #20b486, #74d3b4)'
  },
  {
    label: '未命中问题',
    value: logStats.unmatchedCount,
    icon: 'Warning',
    color: 'linear-gradient(135deg, #ff6b6b, #ff9b8a)'
  },
  {
    label: '平均响应耗时',
    value: `${logStats.avgResponseTime.toFixed(2)}s`,
    icon: 'Timer',
    color: 'linear-gradient(135deg, #7c6cff, #9f94ff)'
  }
])

const keywordOptions = computed(() => [...new Set(qaRecords.value.flatMap((item) => item.keywords || []))])

let keywordTimer = null
const onKeywordInput = () => {
  clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => {
    currentPage.value = 1
    fetchLogs()
  }, 400)
}

watch(
  () => [filters.category, filters.hitStatus, filters.needHuman, filters.dateRange],
  () => {
    currentPage.value = 1
    fetchLogs()
  }
)

const buildQueryParams = () => {
  const params = {
    page: currentPage.value,
    pageSize: pageSize.value
  }
  if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
  if (filters.category !== '全部') params.category = filters.category
  if (filters.hitStatus !== '全部') params.hitStatus = filters.hitStatus
  if (filters.needHuman !== '全部') params.needHuman = filters.needHuman
  const [startDate, endDate] = filters.dateRange || []
  if (startDate) params.startDate = startDate
  if (endDate) params.endDate = endDate
  return params
}

const toggleUnmatchedOnly = () => {
  filters.hitStatus = filters.hitStatus === '未命中' ? '全部' : '未命中'
}

const onLogSelectionChange = (rows) => {
  selectedLogIds.value = rows.map((r) => r.id)
}

const handleDeleteLog = async (row) => {
  await ElMessageBox.confirm('确认删除这条咨询记录吗？', '删除确认', { type: 'warning' })
  await deleteChatLog(row.id)
  await Promise.all([fetchLogs(), fetchStats()])
  ElMessage.success('已删除')
}

const batchDeleteLogs = async () => {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedLogIds.value.length} 条记录吗？`, '批量删除', { type: 'warning' })
  await batchDeleteChatLogs(selectedLogIds.value)
  await Promise.all([fetchLogs(), fetchStats()])
  ElMessage.success('批量删除成功')
}

const openDetail = (row) => {
  activeLog.value = row
  detailVisible.value = true
}

const openKnowledgeDialog = (row) => {
  if (!row) return
  activeLog.value = row
  Object.assign(knowledgeForm, {
    question: row.question,
    answer: row.hitStatus === '未命中' ? '' : row.answer,
    category: row.category,
    keywords: row.category ? [row.category] : [],
    source: '咨询日志未命中问题'
  })
  knowledgeVisible.value = true
}

const saveToKnowledgeBase = async () => {
  await knowledgeFormRef.value.validate()
  await createQa({
    question: knowledgeForm.question,
    answer: knowledgeForm.answer,
    category: knowledgeForm.category,
    keywords: knowledgeForm.keywords,
    source: knowledgeForm.source,
    status: '已发布',
    chatLogId: activeLog.value?.id
  })
  knowledgeVisible.value = false
  detailVisible.value = false
  await Promise.all([fetchLogs(), fetchStats()])
  ElMessage.success('已加入知识库，后续可用于优化 RAG 命中效果')
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await getChatLogs(buildQueryParams())
    logRecords.value = response.data?.list || []
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await getChatLogStats()
    const data = response.data || {}
    logStats.total = data.total || 0
    logStats.todayCount = data.todayCount || 0
    logStats.hitCount = data.hitCount || 0
    logStats.unmatchedCount = data.unmatchedCount || 0
    logStats.avgResponseTime = data.avgResponseTime || 0
  } catch {
    // stats fetch failure is non-critical
  }
}

const fetchCategories = async () => {
  const response = await getCategoryList()
  categoryOptions.value = (response.data || []).map((item) => item.name)
}

const fetchKeywordOptions = async () => {
  const response = await getAdminQaList({ page: 1, pageSize: 500 })
  qaRecords.value = response.data?.list || []
}

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchLogs(), fetchStats(), fetchKeywordOptions()])
})
</script>

<style scoped>
.log-page {
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
    url("/images/bg-dashboard.jpg")
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
  max-width: 680px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
}

.gap-card {
  min-width: 210px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(14px);
}

.gap-card strong,
.gap-card span {
  display: block;
}

.gap-card strong {
  font-size: 42px;
}

.gap-card span {
  color: rgba(255, 255, 255, 0.82);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.filter-card,
.table-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 116px;
  padding: 20px;
  border-radius: 20px;
}

.stat-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  color: #fff;
  font-size: 22px;
}

.stat-card strong {
  display: block;
  color: #172b4d;
  font-size: 26px;
  line-height: 1.1;
}

.stat-card span {
  display: block;
  margin-top: 7px;
  color: #6b7c93;
  font-size: 13px;
}

.filter-card {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 18px;
  border-radius: 20px;
}

.filter-card .el-input,
.filter-card .el-select,
.filter-card .el-date-picker {
  flex: 0 0 auto;
}

.table-card {
  padding: 16px;
  border-radius: 22px;
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.table-card :deep(.el-table) {
  --el-table-border-color: #e4edf5;
  --el-table-header-bg-color: #f6faff;
  --el-table-row-hover-bg-color: #f1f8ff;
  border-radius: 16px;
}

.table-card :deep(.el-table th.el-table__cell) {
  color: #4c627a;
  font-weight: 700;
}

.question-text {
  color: #172b4d;
  line-height: 1.5;
}

.answer-preview {
  display: -webkit-box;
  color: #5d7188;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.similarity-cell :deep(.el-progress__text) {
  min-width: 34px;
  color: #4e6680;
}

.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
  font-size: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

@media (max-width: 1240px) {
  .stat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .filter-card {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .title-panel {
    align-items: flex-start;
    flex-direction: column;
  }

  .stat-grid,
  .filter-card,
  .form-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
