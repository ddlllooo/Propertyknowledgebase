<template>
  <div class="password-reset-manage">
    <div class="title-panel">
      <h2>密码重置管理</h2>
      <p>处理用户发起的密码重置请求，生成临时密码</p>
    </div>

    <section class="stat-grid">
      <article v-for="item in statItems" :key="item.label" class="stat-card">
        <div class="stat-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable size="large" style="width: 140px;">
        <el-option label="全部" value="" />
        <el-option label="待处理" value="待处理" />
        <el-option label="已处理" value="已处理" />
        <el-option label="已忽略" value="已忽略" />
      </el-select>
      <el-input
        v-model="filterKeyword"
        placeholder="搜索用户名或邮箱"
        :prefix-icon="Search"
        size="large"
        clearable
        style="width: 260px;"
      />
      <el-button type="primary" size="large" @click="refreshList">刷新</el-button>
    </div>

    <div v-if="filteredList.length" class="request-list">
      <div v-for="item in filteredList" :key="item.id" class="request-card">
        <div class="card-header">
          <div class="user-info">
            <el-avatar :size="36" class="user-avatar">{{ item.username.slice(0, 1).toUpperCase() }}</el-avatar>
            <div>
              <strong>{{ item.username }}</strong>
              <small>{{ item.email }}</small>
            </div>
          </div>
          <el-tag :type="statusTagType(item.status)" size="large">{{ item.status }}</el-tag>
        </div>
        <div class="card-body">
          <span class="time-label">申请时间：{{ item.createdAt }}</span>
          <span v-if="item.handledAt" class="time-label">处理时间：{{ item.handledAt }}</span>
        </div>
        <div class="card-actions">
          <template v-if="item.status === '待处理'">
            <el-button type="primary" @click="handleReset(item)">重置密码</el-button>
            <el-button @click="handleIgnore(item)">忽略</el-button>
          </template>
          <template v-else-if="item.status === '已处理' && item.tempPassword">
            <el-button type="success" @click="showTempPassword(item)">查看临时密码</el-button>
          </template>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无密码重置请求" />

    <el-dialog v-model="tempDialogVisible" title="临时密码" width="420px">
      <p style="color: #6b7c93; margin-bottom: 16px;">请将以下临时密码告知用户：</p>
      <div class="temp-password-box">
        <span class="temp-password-text">{{ currentTempPassword }}</span>
      </div>
      <template #footer>
        <el-button @click="copyTempPwd">复制密码</el-button>
        <el-button type="primary" @click="tempDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Document, Clock, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getPasswordResetList, adminResetPassword, ignorePasswordReset } from '../../api/adminPasswordReset'

const list = ref([])
const filterStatus = ref('')
const filterKeyword = ref('')
const tempDialogVisible = ref(false)
const currentTempPassword = ref('')

const stats = computed(() => {
  const total = list.value.length
  const pending = list.value.filter((r) => r.status === '待处理').length
  const processed = list.value.filter((r) => r.status === '已处理').length
  const ignored = list.value.filter((r) => r.status === '已忽略').length
  return { total, pending, processed, ignored }
})

const statItems = computed(() => [
  {
    label: '全部请求',
    value: stats.value.total,
    icon: 'Document',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '待处理',
    value: stats.value.pending,
    icon: 'Clock',
    color: 'linear-gradient(135deg, #e6a23c, #f0c78a)'
  },
  {
    label: '已处理',
    value: stats.value.processed,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #20b486, #74d3b4)'
  },
  {
    label: '已忽略',
    value: stats.value.ignored,
    icon: 'CircleClose',
    color: 'linear-gradient(135deg, #909399, #b8bcc4)'
  }
])

const filteredList = computed(() => {
  let result = list.value
  if (filterStatus.value) {
    result = result.filter((r) => r.status === filterStatus.value)
  }
  if (filterKeyword.value) {
    const kw = filterKeyword.value.toLowerCase()
    result = result.filter(
      (r) => r.username.toLowerCase().includes(kw) || r.email.toLowerCase().includes(kw)
    )
  }
  return result
})

const statusTagType = (status) => {
  if (status === '待处理') return 'warning'
  if (status === '已处理') return 'success'
  return 'info'
}

const refreshList = async () => {
  try {
    const res = await getPasswordResetList({ page: 1, pageSize: 200 })
    list.value = res?.data?.list || []
  } catch {
    ElMessage.error('加载失败')
  }
}

const handleReset = async (item) => {
  await ElMessageBox.confirm(`确认为用户「${item.username}」重置密码吗？将生成临时密码。`, '重置密码', {
    type: 'warning',
    confirmButtonText: '确认重置',
    cancelButtonText: '取消'
  })
  try {
    const res = await adminResetPassword(item.id)
    ElMessage.success('密码重置成功')
    currentTempPassword.value = res?.data?.tempPassword || ''
    tempDialogVisible.value = true
    await refreshList()
  } catch (error) {
    const msg = error?.response?.data?.message || error?.message || '操作失败'
    ElMessage.error(msg)
  }
}

const handleIgnore = async (item) => {
  await ElMessageBox.confirm(`确认忽略用户「${item.username}」的密码重置请求吗？`, '忽略请求', {
    type: 'warning',
    confirmButtonText: '确认忽略',
    cancelButtonText: '取消'
  })
  try {
    await ignorePasswordReset(item.id)
    ElMessage.success('已忽略')
    await refreshList()
  } catch (error) {
    const msg = error?.response?.data?.message || error?.message || '操作失败'
    ElMessage.error(msg)
  }
}

const showTempPassword = (item) => {
  currentTempPassword.value = item.tempPassword || ''
  tempDialogVisible.value = true
}

const copyTempPwd = () => {
  if (currentTempPassword.value) {
    navigator.clipboard.writeText(currentTempPassword.value)
    ElMessage.success('已复制到剪贴板')
  }
}

onMounted(() => {
  refreshList()
})
</script>

<style scoped>
.password-reset-manage {
  display: grid;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
}

.title-panel {
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

.title-panel h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 800;
}

.title-panel p {
  margin: 0;
  opacity: 0.88;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 116px;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
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

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.request-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.request-card {
  padding: 20px 24px;
  border-radius: 20px;
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info strong {
  display: block;
  color: #172b4d;
}

.user-info small {
  display: block;
  color: #7b8fa6;
  font-size: 13px;
}

.user-avatar {
  background: linear-gradient(135deg, #1178ff, #13bea7);
}

.card-body {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.time-label {
  color: #7b8fa6;
  font-size: 13px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.temp-password-box {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border-radius: 12px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
}

.temp-password-text {
  font-size: 28px;
  font-weight: 800;
  color: #172b4d;
  letter-spacing: 2px;
  font-family: monospace;
}
</style>
