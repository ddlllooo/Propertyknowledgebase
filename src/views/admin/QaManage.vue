<template>
  <div class="qa-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Knowledge Maintenance</el-tag>
        <h1>知识库维护</h1>
        <p>维护物业高频问答、标准答案、分类与关键词，支持后续 RAG 智能问答调用。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增问答</el-button>
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

    <section class="toolbar-card">
      <div class="filter-row">
        <el-input
          v-model="filters.keyword"
          clearable
          placeholder="搜索标准问题、答案、关键词"
          :prefix-icon="Search"
        />
        <el-select v-model="filters.category" placeholder="分类筛选">
          <el-option label="全部分类" value="全部" />
          <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态筛选">
          <el-option label="全部状态" value="全部" />
          <el-option label="启用" value="启用" />
          <el-option label="停用" value="停用" />
        </el-select>
      </div>

      <div class="action-row">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增问答</el-button>
        <el-button :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button type="success" :icon="Refresh" :loading="rebuildLoading" @click="handleRebuildVector">
          重建向量库
        </el-button>
      </div>
    </section>

    <section class="table-card">
      <el-table :data="filteredQaList" row-key="id" stripe>
        <el-table-column prop="id" label="编号" width="82" />
        <el-table-column prop="question" label="标准问题" min-width="240">
          <template #default="{ row }">
            <div class="question-cell">
              <strong>{{ row.question }}</strong>
              <span>{{ row.source }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag round>{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关键词" min-width="190">
          <template #default="{ row }">
            <div class="keyword-tags">
              <el-tag v-for="tag in row.keywords" :key="tag" size="small" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="viewCount" label="查看次数" width="104" />
        <el-table-column prop="askCount" label="咨询命中次数" width="126" />
        <el-table-column prop="status" label="状态" width="96">
          <template #default="{ row }">
            <el-tag :type="row.status === '启用' ? 'success' : 'info'" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="120" />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" :type="row.status === '启用' ? 'warning' : 'success'" link @click="toggleStatus(row)">
                {{ row.status === '启用' ? '停用' : '启用' }}
              </el-button>
              <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增问答' : '编辑问答'" width="680px">
      <el-form ref="qaFormRef" :model="qaForm" :rules="rules" label-position="top">
        <el-form-item label="标准问题" prop="question">
          <el-input v-model="qaForm.question" placeholder="请输入标准问题" />
        </el-form-item>
        <el-form-item label="标准答案" prop="answer">
          <el-input
            v-model="qaForm.answer"
            type="textarea"
            :rows="5"
            resize="none"
            placeholder="请输入面向用户展示的标准答案"
          />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="分类" prop="category">
            <el-select v-model="qaForm.category" placeholder="请选择分类">
              <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="qaForm.status">
              <el-radio-button label="启用" />
              <el-radio-button label="停用" />
            </el-radio-group>
          </el-form-item>
        </div>
        <el-form-item label="关键词" prop="keywords">
          <el-select
            v-model="qaForm.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后回车添加"
          >
            <el-option v-for="item in keywordOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据来源" prop="source">
          <el-input v-model="qaForm.source" placeholder="例如：物业服务合同、工程报修服务规范" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQaForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Upload } from '@element-plus/icons-vue'
import { categoryList, qaList } from '../../mock/mockData'

const today = '2026-04-29'
const categoryOptions = categoryList.map((item) => item.name)
const rebuildLoading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create')
const qaFormRef = ref()

const qaRecords = ref(
  qaList.map((item) => ({
    ...item,
    status: item.status === '已发布' ? '启用' : '停用'
  }))
)

const filters = reactive({
  keyword: '',
  category: '全部',
  status: '全部'
})

const createEmptyForm = () => ({
  id: null,
  question: '',
  answer: '',
  category: '',
  keywords: [],
  viewCount: 0,
  askCount: 0,
  status: '启用',
  source: '',
  updatedAt: today
})

const qaForm = reactive(createEmptyForm())

const rules = {
  question: [{ required: true, message: '请输入标准问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  keywords: [{ required: true, type: 'array', min: 1, message: '请至少填写一个关键词', trigger: 'change' }],
  source: [{ required: true, message: '请输入数据来源', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const stats = computed(() => [
  {
    label: '总问答数',
    value: qaRecords.value.length,
    icon: 'Collection',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '启用问答',
    value: qaRecords.value.filter((item) => item.status === '启用').length,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '停用问答',
    value: qaRecords.value.filter((item) => item.status === '停用').length,
    icon: 'CircleClose',
    color: 'linear-gradient(135deg, #7c8da5, #a5b5c6)'
  },
  {
    label: '今日更新',
    value: qaRecords.value.filter((item) => item.updatedAt === today).length,
    icon: 'Refresh',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  }
])

const keywordOptions = computed(() => {
  return [...new Set(qaRecords.value.flatMap((item) => item.keywords))]
})

const filteredQaList = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase()

  return qaRecords.value.filter((item) => {
    const text = [item.question, item.answer, item.category, item.source, ...item.keywords].join(' ').toLowerCase()
    const keywordMatched = !keyword || text.includes(keyword)
    const categoryMatched = filters.category === '全部' || item.category === filters.category
    const statusMatched = filters.status === '全部' || item.status === filters.status
    return keywordMatched && categoryMatched && statusMatched
  })
})

const assignForm = (data) => {
  Object.assign(qaForm, {
    ...createEmptyForm(),
    ...data,
    keywords: [...(data.keywords || [])]
  })
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  assignForm(createEmptyForm())
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogMode.value = 'edit'
  assignForm(row)
  dialogVisible.value = true
}

const submitQaForm = async () => {
  await qaFormRef.value.validate()

  const payload = {
    ...qaForm,
    keywords: [...qaForm.keywords],
    updatedAt: today
  }

  if (dialogMode.value === 'create') {
    qaRecords.value.unshift({
      ...payload,
      id: Math.max(...qaRecords.value.map((item) => item.id), 0) + 1
    })
    ElMessage.success('新增问答成功')
  } else {
    const index = qaRecords.value.findIndex((item) => item.id === payload.id)
    if (index !== -1) {
      qaRecords.value[index] = payload
    }
    ElMessage.success('编辑问答成功')
  }

  dialogVisible.value = false
}

const toggleStatus = (row) => {
  row.status = row.status === '启用' ? '停用' : '启用'
  row.updatedAt = today
  ElMessage.success(`已${row.status}该问答`)
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确认删除“${row.question}”吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  qaRecords.value = qaRecords.value.filter((item) => item.id !== row.id)
  ElMessage.success('删除成功')
}

const handleImport = () => {
  ElMessage.info('已预留批量导入入口，当前演示使用 mock 数据。')
}

const handleRebuildVector = async () => {
  await ElMessageBox.confirm('确认基于当前知识库数据重建向量库吗？', '重建向量库', {
    type: 'info',
    confirmButtonText: '开始重建',
    cancelButtonText: '取消'
  })
  rebuildLoading.value = true
  setTimeout(() => {
    rebuildLoading.value = false
    ElMessage.success('向量库重建成功')
  }, 2000)
}
</script>

<style scoped>
.qa-page {
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
    url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1400&q=80")
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
  max-width: 720px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
}

.title-panel .el-button {
  margin-top: 4px;
  border: 0;
  color: #1178ff;
  background: #fff;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.toolbar-card,
.table-card {
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

.toolbar-card {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 18px;
  border-radius: 20px;
}

.filter-row {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) 160px 140px;
  gap: 12px;
  flex: 1;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.table-card {
  padding: 16px;
  border-radius: 22px;
  overflow: hidden;
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

.table-card :deep(.el-table .cell) {
  line-height: 1.55;
}

.question-cell strong,
.question-cell span {
  display: block;
}

.question-cell strong {
  color: #172b4d;
  font-size: 14px;
}

.question-cell span {
  margin-top: 5px;
  color: #8a9db1;
  font-size: 12px;
}

.keyword-tags,
.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.table-actions {
  gap: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 16px;
}

@media (max-width: 1180px) {
  .toolbar-card {
    align-items: stretch;
    flex-direction: column;
  }

  .action-row {
    justify-content: flex-start;
  }
}

@media (max-width: 860px) {
  .title-panel {
    flex-direction: column;
  }

  .stat-grid,
  .filter-row,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
