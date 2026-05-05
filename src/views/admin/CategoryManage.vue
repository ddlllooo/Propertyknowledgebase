<template>
  <div class="category-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Category Center</el-tag>
        <h1>分类管理</h1>
        <p>维护知识库分类结构，让用户更快定位问题。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增分类</el-button>
    </section>

    <section class="overview-grid">
      <article v-for="item in overviewCards" :key="item.label" class="overview-card">
        <div class="overview-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="toolbar-card">
      <el-input v-model="keyword" clearable placeholder="搜索分类名称或描述" :prefix-icon="Search" />
      <el-select v-model="statusFilter" placeholder="状态筛选">
        <el-option label="全部状态" value="全部" />
        <el-option label="启用" value="启用" />
        <el-option label="停用" value="停用" />
      </el-select>
    </section>

    <section class="category-grid">
      <article v-for="item in filteredCategories" :key="item.id" class="category-card">
        <div class="card-head">
          <div>
            <h2>{{ item.name }}</h2>
            <span>排序 {{ item.sortOrder }}</span>
          </div>
          <el-tag :type="item.status === '启用' ? 'success' : 'info'" round>{{ item.status }}</el-tag>
        </div>

        <p>{{ item.description }}</p>

        <div class="visual-row">
          <div class="count-block">
            <strong>{{ item.questionCount }}</strong>
            <span>关联问答</span>
          </div>
          <div class="progress-block">
            <span>知识占比</span>
            <el-progress
              :percentage="getQuestionPercent(item.questionCount)"
              :show-text="false"
              :stroke-width="8"
            />
          </div>
        </div>

        <div class="meta-row">
          <span>创建时间：{{ item.createdAt }}</span>
        </div>

        <div class="card-actions">
          <el-button type="primary" link @click="openEditDialog(item)">编辑</el-button>
          <el-button :type="item.status === '启用' ? 'warning' : 'success'" link @click="toggleStatus(item)">
            {{ item.status === '启用' ? '停用' : '启用' }}
          </el-button>
          <el-button type="danger" link @click="handleDelete(item)">删除</el-button>
        </div>
      </article>
    </section>

    <el-empty v-if="filteredCategories.length === 0" description="暂无匹配分类" />

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增分类' : '编辑分类'" width="560px">
      <el-form ref="categoryFormRef" :model="categoryForm" :rules="rules" label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="4"
            resize="none"
            placeholder="请输入该分类覆盖的业务范围"
          />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="排序值" prop="sortOrder">
            <el-input-number v-model="categoryForm.sortOrder" :min="1" :max="99" controls-position="right" />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="categoryForm.status">
              <el-radio-button label="启用" />
              <el-radio-button label="停用" />
            </el-radio-group>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategoryForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { createCategory, deleteCategory, getCategoryList, updateCategory } from '../../api/adminCategory'
import { getAdminQaList } from '../../api/adminQa'

const keyword = ref('')
const statusFilter = ref('全部')
const dialogVisible = ref(false)
const dialogMode = ref('create')
const categoryFormRef = ref()

const categories = ref([])
const qaTotal = ref(0)

const createEmptyForm = () => ({
  id: null,
  name: '',
  description: '',
  questionCount: 0,
  sortOrder: categories.value.length + 1,
  status: '启用',
  createdAt: new Date().toISOString().slice(0, 10)
})

const categoryForm = reactive(createEmptyForm())

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入分类描述', trigger: 'blur' }],
  sortOrder: [{ required: true, message: '请输入排序值', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const overviewCards = computed(() => [
  {
    label: '分类总数',
    value: categories.value.length,
    icon: 'Grid',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '启用分类',
    value: categories.value.filter((item) => item.status === '启用').length,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '停用分类',
    value: categories.value.filter((item) => item.status === '停用').length,
    icon: 'CircleClose',
    color: 'linear-gradient(135deg, #7c8da5, #a5b5c6)'
  },
  {
    label: '问答总数',
    value: qaTotal.value,
    icon: 'Collection',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  }
])

const filteredCategories = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()

  return categories.value
    .filter((item) => {
      const keywordMatched =
        !normalizedKeyword || `${item.name} ${item.description}`.toLowerCase().includes(normalizedKeyword)
      const statusMatched = statusFilter.value === '全部' || item.status === statusFilter.value
      return keywordMatched && statusMatched
    })
    .sort((a, b) => a.sortOrder - b.sortOrder)
})

const maxQuestionCount = computed(() => Math.max(...categories.value.map((item) => item.questionCount), 1))

const getQuestionPercent = (count) => {
  return Math.round((count / maxQuestionCount.value) * 100)
}

const assignForm = (data) => {
  Object.assign(categoryForm, {
    ...createEmptyForm(),
    ...data
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

const submitCategoryForm = async () => {
  await categoryFormRef.value.validate()

  const payload = {
    name: categoryForm.name,
    description: categoryForm.description,
    sortOrder: categoryForm.sortOrder,
    status: categoryForm.status
  }

  if (dialogMode.value === 'create') {
    await createCategory(payload)
    ElMessage.success('新增分类成功')
  } else {
    await updateCategory(categoryForm.id, payload)
    ElMessage.success('编辑分类成功')
  }

  dialogVisible.value = false
  await fetchCategories()
}

const toggleStatus = async (row) => {
  const status = row.status === '启用' ? '停用' : '启用'
  await updateCategory(row.id, { status })
  row.status = status
  ElMessage.success(`已${row.status}该分类`)
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确认删除“${row.name}”分类吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteCategory(row.id)
  await fetchCategories()
  ElMessage.success('删除成功')
}

const fetchCategories = async () => {
  const response = await getCategoryList()
  categories.value = response.data || []
}

const fetchQaTotal = async () => {
  const response = await getAdminQaList({ page: 1, pageSize: 1 })
  qaTotal.value = response.data?.total || 0
}

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchQaTotal()])
})
</script>

<style scoped>
.category-page {
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
    url("https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1400&q=80")
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
  margin-top: 4px;
  border: 0;
  color: #1178ff;
  background: #fff;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.overview-card,
.toolbar-card,
.category-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 116px;
  padding: 22px;
  border-radius: 20px;
}

.overview-icon {
  display: grid;
  place-items: center;
  width: 50px;
  height: 50px;
  border-radius: 16px;
  color: #fff;
  font-size: 22px;
}

.overview-card strong {
  display: block;
  color: #172b4d;
  font-size: 30px;
  line-height: 1.1;
}

.overview-card span {
  display: block;
  margin-top: 7px;
  color: #6b7c93;
}

.toolbar-card {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) 180px;
  gap: 12px;
  padding: 18px;
  border-radius: 20px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.category-card {
  padding: 22px;
  border-radius: 22px;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(21, 56, 98, 0.13);
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
  font-size: 22px;
}

.card-head span {
  display: block;
  margin-top: 6px;
  color: #8a9db1;
  font-size: 13px;
}

.category-card p {
  min-height: 54px;
  margin: 18px 0;
  color: #5d7188;
  line-height: 1.75;
}

.visual-row {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(120deg, #f0f7ff, #effbf8);
}

.count-block strong,
.count-block span,
.progress-block span {
  display: block;
}

.count-block strong {
  color: #1178ff;
  font-size: 32px;
  line-height: 1;
}

.count-block span,
.progress-block span {
  color: #6b7c93;
  font-size: 13px;
}

.progress-block .el-progress {
  margin-top: 10px;
}

.meta-row {
  margin-top: 16px;
  color: #8a9db1;
  font-size: 13px;
}

.card-actions {
  display: flex;
  gap: 14px;
  margin-top: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 16px;
}

@media (max-width: 1120px) {
  .category-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .title-panel {
    flex-direction: column;
  }

  .overview-grid,
  .toolbar-card,
  .category-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
