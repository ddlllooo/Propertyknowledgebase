<template>
  <div class="qa-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Knowledge Maintenance</el-tag>
        <h1>知识库维护</h1>
        <p>维护物业高频问答、标准答案、分类与关键词。</p>
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
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
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
        <el-table-column prop="viewCount" label="查看次数" width="104" align="center"/>
        <el-table-column prop="askCount" label="咨询命中次数" width="110" align="center"/>
        <el-table-column prop="status" label="状态" width="90" >
          <template #default="{ row }" >
            <el-tag :type="statusTagType(row.status)" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="120" />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" :type="row.status === '已发布' ? 'warning' : 'success'" link @click="toggleStatus(row)">
                {{ row.status === '已发布' ? '停用' : '发布' }}
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
            <el-select
              v-model="qaForm.category"
              filterable
              allow-create
              default-first-option
              clearable
              placeholder="请选择或输入分类"
            >
              <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="qaForm.status">
              <el-radio-button v-for="item in statusOptions" :key="item" :label="item" />
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

    <el-dialog v-model="importVisible" title="批量导入问答" width="860px">
      <div class="import-tools">
        <el-button :icon="Download" @click="downloadImportTemplate">下载导入模板</el-button>
        <el-button type="primary" :icon="Upload" @click="triggerFileSelect">选择 CSV 文件</el-button>
        <input
          ref="fileInputRef"
          class="hidden-file"
          type="file"
          accept=".csv,text/csv"
          @change="handleImportFile"
        />
      </div>

      <div class="import-note">
        <span>模板需包含：标准问题（question）、标准答案（answer）、分类（category）、关键词（keywords）、来源（source）、状态（status）；新分类可填写分类描述（categoryDescription）。</span>
        <span>关键词可以填写多个，请用中文逗号、英文逗号或分号分隔。</span>
      </div>

      <el-alert
        v-if="importErrors.length"
        class="import-alert"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #title>
          <span>{{ importErrors.slice(0, 3).join('；') }}</span>
        </template>
      </el-alert>

      <el-table v-if="importRows.length" :data="importRows" max-height="360" stripe>
        <el-table-column type="index" label="#" width="56" />
        <el-table-column prop="question" label="标准问题" min-width="180" />
        <el-table-column prop="category" label="分类" width="110" />
        <el-table-column prop="categoryDescription" label="分类描述" min-width="170" />
        <el-table-column label="关键词" min-width="160">
          <template #default="{ row }">{{ row.keywords.join('，') }}</template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="130" />
        <el-table-column prop="status" label="状态" width="96" />
      </el-table>

      <div
        v-else
        class="import-drop-zone"
        @click="triggerFileSelect"
        @dragover.prevent
        @drop.prevent="handleImportDrop"
      >
        <el-icon><Upload /></el-icon>
        <strong>拖拽 CSV 文件到这里</strong>
        <span>也可以点击此区域选择填写后的 CSV 文件</span>
      </div>

      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" :disabled="!importRows.length" @click="submitImportRows">
          导入 {{ importRows.length }} 条
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Plus, Refresh, Search, Upload } from '@element-plus/icons-vue'
import { batchCreateQa, createQa, deleteQa, getAdminQaList, updateQa } from '../../api/adminQa'
import { getCategoryList } from '../../api/adminCategory'
import { rebuildVector } from '../../api/vector'

const categoryRecords = ref([])
const statusOptions = ['已发布', '草稿', '待审核', '已停用']
const rebuildLoading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create')
const qaFormRef = ref()
const importVisible = ref(false)
const importRows = ref([])
const importErrors = ref([])
const importLoading = ref(false)
const fileInputRef = ref()

const qaRecords = ref([])

const categoryOptions = computed(() => {
  const names = [
    ...categoryRecords.value.map((item) => item.name),
    ...qaRecords.value.map((item) => item.category)
  ]
  return [...new Set(names.map((item) => String(item || '').trim()).filter(Boolean))]
})

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
  status: '已发布',
  source: '',
  updatedAt: ''
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
    value: qaRecords.value.filter((item) => item.status === '已发布').length,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '停用问答',
    value: qaRecords.value.filter((item) => item.status === '已停用').length,
    icon: 'CircleClose',
    color: 'linear-gradient(135deg, #7c8da5, #a5b5c6)'
  },
  {
    label: '今日更新',
    value: qaRecords.value.filter((item) => item.updatedAt === new Date().toISOString().slice(0, 10)).length,
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

const statusTagType = (status) => {
  if (status === '已发布') return 'success'
  if (status === '待审核') return 'warning'
  if (status === '草稿') return 'primary'
  return 'info'
}

const fetchCategories = async () => {
  const response = await getCategoryList()
  categoryRecords.value = response.data || []
}

const fetchQaRecords = async () => {
  const response = await getAdminQaList({
    page: 1,
    pageSize: 1000
  })
  qaRecords.value = response.data?.list || []
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
    question: qaForm.question,
    answer: qaForm.answer,
    category: qaForm.category,
    keywords: [...qaForm.keywords],
    source: qaForm.source,
    status: qaForm.status
  }

  if (dialogMode.value === 'create') {
    await createQa(payload)
    ElMessage.success('新增问答成功')
  } else {
    await updateQa(qaForm.id, payload)
    ElMessage.success('编辑问答成功')
  }

  dialogVisible.value = false
  await Promise.all([fetchQaRecords(), fetchCategories()])
}

const toggleStatus = async (row) => {
  const status = row.status === '已发布' ? '已停用' : '已发布'
  await updateQa(row.id, { status })
  row.status = status
  await fetchCategories()
  ElMessage.success(`已${row.status}该问答`)
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确认删除“${row.question}”吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteQa(row.id)
  await Promise.all([fetchQaRecords(), fetchCategories()])
  ElMessage.success('删除成功')
}

const handleImport = () => {
  importVisible.value = true
  importRows.value = []
  importErrors.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const downloadImportTemplate = () => {
  const rows = [
    ['question（标准问题）', 'answer（标准答案）', 'category（分类）', 'categoryDescription（分类描述）', 'keywords（关键词）', 'source（来源）', 'status（状态）'],
    [
      '物业费电子发票在哪里开？',
      '线上缴费完成后，可在社区小程序缴费记录中申请电子发票。',
      '物业缴费',
      '物业费、水电公摊、账单查询、票据开具等缴费相关知识。',
      '物业费，电子发票，票据',
      '管理员导入',
      '已发布'
    ]
  ]
  const csv = rows.map((row) => row.map(escapeCsvCell).join(',')).join('\n')
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'qa_import_template.csv'
  link.click()
  URL.revokeObjectURL(url)
}

const escapeCsvCell = (value) => {
  const text = String(value ?? '')
  return `"${text.replaceAll('"', '""')}"`
}

const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

const handleImportFile = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  await parseImportUpload(file)
  event.target.value = ''
}

const handleImportDrop = async (event) => {
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  await parseImportUpload(file)
}

const parseImportUpload = async (file) => {
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.csv')) {
    ElMessage.warning('请上传 CSV 文件')
    return
  }

  const content = await file.text()
  const parsedRows = parseCsv(content)
  const { rows, errors } = normalizeImportRows(parsedRows)
  importRows.value = rows
  importErrors.value = errors

  if (!rows.length && !errors.length) {
    importErrors.value = ['未读取到可导入数据']
  }
}

const parseCsv = (content) => {
  const text = content.replace(/^\ufeff/, '')
  const rows = []
  let row = []
  let cell = ''
  let inQuotes = false

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    const next = text[index + 1]

    if (char === '"' && inQuotes && next === '"') {
      cell += '"'
      index += 1
      continue
    }

    if (char === '"') {
      inQuotes = !inQuotes
      continue
    }

    if (char === ',' && !inQuotes) {
      row.push(cell)
      cell = ''
      continue
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') index += 1
      row.push(cell)
      if (row.some((item) => item.trim())) rows.push(row)
      row = []
      cell = ''
      continue
    }

    cell += char
  }

  row.push(cell)
  if (row.some((item) => item.trim())) rows.push(row)
  return rows
}

const normalizeImportRows = (csvRows) => {
  const [header = [], ...body] = csvRows
  const headerMap = header.map((item) => item.trim().replace(/（[^）]*）/, '').trim())
  const requiredHeaders = ['question', 'answer', 'category', 'keywords', 'source', 'status']
  const errors = []

  requiredHeaders.forEach((name) => {
    if (!headerMap.includes(name)) {
      errors.push(`缺少模板字段 ${name}`)
    }
  })

  if (errors.length) {
    return { rows: [], errors }
  }

  const rows = []
  body.forEach((line, index) => {
    const record = Object.fromEntries(headerMap.map((name, columnIndex) => [name, (line[columnIndex] || '').trim()]))
    const lineNumber = index + 2

    if (!record.question || !record.answer || !record.category) {
      errors.push(`第 ${lineNumber} 行缺少标准问题、标准答案或分类`)
      return
    }

    rows.push({
      question: record.question,
      answer: record.answer,
      category: record.category,
      categoryDescription: record.categoryDescription || record.category_description || '',
      keywords: splitKeywords(record.keywords),
      source: record.source || '批量导入',
      status: record.status || '已发布'
    })
  })

  return { rows, errors }
}

const splitKeywords = (value) => {
  return String(value || '')
    .split(/[，,;；]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const submitImportRows = async () => {
  if (!importRows.value.length) return
  importLoading.value = true
  try {
    const response = await batchCreateQa(importRows.value.map((row) => ({
      question: row.question,
      answer: row.answer,
      category: row.category,
      categoryDescription: row.categoryDescription,
      keywords: row.keywords,
      source: row.source,
      status: row.status
    })))
    if (response.data?.errorCount) {
      ElMessage.warning(`导入完成：成功 ${response.data.createdCount} 条，失败 ${response.data.errorCount} 条`)
    } else {
      ElMessage.success(`成功导入 ${importRows.value.length} 条问答`)
    }
    importVisible.value = false
    await Promise.all([fetchQaRecords(), fetchCategories()])
  } finally {
    importLoading.value = false
  }
}

const handleRebuildVector = async () => {
  await ElMessageBox.confirm('确认基于当前知识库数据重建向量库吗？', '重建向量库', {
    type: 'info',
    confirmButtonText: '开始重建',
    cancelButtonText: '取消'
  })
  rebuildLoading.value = true
  try {
    await rebuildVector()
    rebuildLoading.value = false
    ElMessage.success('向量库重建成功')
  } finally {
    rebuildLoading.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchQaRecords()])
})
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

.hidden-file {
  display: none;
}

.import-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.import-note {
  display: grid;
  gap: 4px;
  margin-bottom: 14px;
  color: #6b7c93;
  font-size: 13px;
}

.import-alert {
  margin-bottom: 14px;
}

.import-drop-zone {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 230px;
  padding: 34px 18px;
  border: 1px dashed #9ac4f8;
  border-radius: 16px;
  color: #4f6f90;
  background: linear-gradient(135deg, rgba(17, 120, 255, 0.06), rgba(19, 190, 167, 0.08));
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;
}

.import-drop-zone:hover {
  border-color: #1178ff;
  color: #1178ff;
  background: linear-gradient(135deg, rgba(17, 120, 255, 0.1), rgba(19, 190, 167, 0.12));
}

.import-drop-zone .el-icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  color: #fff;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  font-size: 24px;
}

.import-drop-zone strong {
  color: #172b4d;
  font-size: 18px;
}

.import-drop-zone span {
  font-size: 13px;
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
