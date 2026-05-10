<template>
  <div class="user-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>User Management</el-tag>
        <h1>用户管理</h1>
        <p>管理系统用户账号、角色和状态。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增用户</el-button>
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
          placeholder="搜索用户名、昵称、邮箱"
          :prefix-icon="Search"
          @input="onKeywordInput"
        />
        <el-select v-model="filters.role" placeholder="角色筛选">
          <el-option label="全部角色" value="全部" />
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态筛选">
          <el-option label="全部状态" value="全部" />
          <el-option label="启用" value="启用" />
          <el-option label="停用" value="停用" />
        </el-select>
      </div>
      <div class="action-row">
        <el-button type="success" :disabled="!selectedIds.length" @click="batchEnable">批量启用</el-button>
        <el-button type="warning" :disabled="!selectedIds.length" @click="batchDisable">批量停用</el-button>
      </div>
    </section>

    <section v-loading="loading" class="table-card">
      <el-table :data="userRecords" row-key="id" stripe @selection-change="onSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" round>
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '启用' ? 'success' : 'info'" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="注册时间" width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button
                size="small"
                :type="row.status === '启用' ? 'warning' : 'success'"
                link
                @click="toggleStatus(row)"
              >
                {{ row.status === '启用' ? '停用' : '启用' }}
              </el-button>
              <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
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
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增用户' : '编辑用户'" width="560px">
      <el-form ref="formRef" :model="userForm" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="dialogMode === 'edit'" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="角色" prop="role">
            <el-select v-model="userForm.role">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="userForm.status">
              <el-option label="启用" value="启用" />
              <el-option label="停用" value="停用" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item :label="dialogMode === 'create' ? '密码' : '重置密码（留空则不修改）'" prop="password">
          <el-input v-model="userForm.password" type="password" show-password placeholder="至少6位，包含字母和数字" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { batchUpdateUserStatus, createUser, deleteUser, getUserList, updateUser } from '../../api/adminUser'

const userRecords = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref([])

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref()

const filters = reactive({
  keyword: '',
  role: '全部',
  status: '全部'
})

const userForm = reactive({
  id: null,
  username: '',
  email: '',
  nickname: '',
  role: 'user',
  status: '启用',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (dialogMode.value === 'create' && (!value || value.length < 6)) {
          callback(new Error('密码不能少于6位'))
        } else if (value && value.length < 6) {
          callback(new Error('密码不能少于6位'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const stats = computed(() => [
  {
    label: '总用户数',
    value: total.value,
    icon: 'User',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '管理员',
    value: userRecords.value.filter((u) => u.role === 'admin').length,
    icon: 'Star',
    color: 'linear-gradient(135deg, #ff6b6b, #ff9b8a)'
  },
  {
    label: '已启用',
    value: userRecords.value.filter((u) => u.status === '启用').length,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '已停用',
    value: userRecords.value.filter((u) => u.status === '停用').length,
    icon: 'CircleClose',
    color: 'linear-gradient(135deg, #7c8da5, #a5b5c6)'
  }
])

let keywordTimer = null
const onKeywordInput = () => {
  clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 400)
}

watch(
  () => [filters.role, filters.status],
  () => {
    currentPage.value = 1
    fetchUsers()
  }
)

const buildParams = () => {
  const params = { page: currentPage.value, pageSize: pageSize.value }
  if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
  if (filters.role !== '全部') params.role = filters.role
  if (filters.status !== '全部') params.status = filters.status
  return params
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await getUserList(buildParams())
    userRecords.value = response.data?.list || []
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

const onSelectionChange = (rows) => {
  selectedIds.value = rows.map((r) => r.id)
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  Object.assign(userForm, { id: null, username: '', email: '', nickname: '', role: 'user', status: '启用', password: '' })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogMode.value = 'edit'
  Object.assign(userForm, { ...row, password: '' })
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()

  if (dialogMode.value === 'create') {
    await createUser({
      username: userForm.username,
      email: userForm.email,
      nickname: userForm.nickname,
      role: userForm.role,
      password: userForm.password
    })
    ElMessage.success('用户创建成功')
  } else {
    const payload = {
      email: userForm.email,
      nickname: userForm.nickname,
      role: userForm.role,
      status: userForm.status
    }
    if (userForm.password) {
      payload.password = userForm.password
    }
    await updateUser(userForm.id, payload)
    ElMessage.success('用户信息已更新')
  }

  dialogVisible.value = false
  await fetchUsers()
}

const toggleStatus = async (row) => {
  const status = row.status === '启用' ? '停用' : '启用'
  await updateUser(row.id, { status })
  row.status = status
  ElMessage.success(`已${status}用户 ${row.username}`)
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确认删除用户"${row.username}"吗？此操作不可恢复。`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteUser(row.id)
  await fetchUsers()
  ElMessage.success('用户已删除')
}

const batchEnable = async () => {
  await batchUpdateUserStatus(selectedIds.value, '启用')
  await fetchUsers()
  ElMessage.success('批量启用成功')
}

const batchDisable = async () => {
  await ElMessageBox.confirm(`确认停用选中的 ${selectedIds.value.length} 个用户吗？`, '批量停用', {
    type: 'warning'
  })
  await batchUpdateUserStatus(selectedIds.value, '停用')
  await fetchUsers()
  ElMessage.success('批量停用成功')
}

onMounted(fetchUsers)
</script>

<style scoped>
.user-page {
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
    url("/images/bg-office.jpg")
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
  grid-template-columns: minmax(240px, 1fr) 150px 140px;
  gap: 12px;
  flex: 1;
}

.action-row {
  display: flex;
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

.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
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
