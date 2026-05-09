<template>
  <el-container class="admin-layout">
    <el-aside width="260px" class="admin-sidebar">
      <router-link class="admin-logo" to="/admin/home">
        <span class="logo-mark">
          <el-icon><Setting /></el-icon>
        </span>
        <span>
          <strong>智慧物业管理端</strong>
          <small>Knowledge Admin</small>
        </span>
      </router-link>

      <el-menu :default-active="route.path" router class="admin-menu">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div class="page-title">
          <span>管理员端</span>
          <h1>{{ currentTitle }}</h1>
        </div>

        <div class="header-actions">
          <el-tag type="primary" effect="light" round>管理员</el-tag>
          <div class="admin-profile">
            <el-avatar :size="34" class="admin-avatar">
              {{ adminName.slice(0, 1).toUpperCase() }}
            </el-avatar>
            <span>{{ adminName }}</span>
          </div>
          <el-button :icon="SwitchButton" round @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Setting, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const adminName = sessionStorage.getItem('username') || 'admin'

const menus = [
  { label: '工作台', path: '/admin/home', icon: 'Monitor' },
  { label: '知识库维护', path: '/admin/qa', icon: 'Collection' },
  { label: '分类管理', path: '/admin/category', icon: 'FolderOpened' },
  { label: '反馈处理', path: '/admin/feedback', icon: 'ChatLineRound' },
  { label: '密码重置', path: '/admin/password-reset', icon: 'Key' },
  { label: '咨询日志', path: '/admin/logs', icon: 'Tickets' },
  { label: '数据看板', path: '/admin/dashboard', icon: 'DataAnalysis' },
  { label: '向量库维护', path: '/admin/vector', icon: 'Connection' }
]

const currentTitle = computed(() => {
  return route.meta.title || menus.find((item) => item.path === route.path)?.label || '工作台'
})

const handleLogout = async () => {
  await ElMessageBox.confirm('确认退出管理员账号吗？', '退出登录', {
    type: 'warning',
    confirmButtonText: '退出',
    cancelButtonText: '取消'
  })
  sessionStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background:
    radial-gradient(circle at 6% 4%, rgba(17, 120, 255, 0.09), transparent 28%),
    radial-gradient(circle at 94% 10%, rgba(19, 190, 167, 0.1), transparent 30%),
    #f5f8fb;
}

.admin-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 24px 18px;
  border-right: 1px solid rgba(210, 225, 237, 0.86);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px);
}

.admin-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 8px 26px;
}

.logo-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 15px;
  color: #fff;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  box-shadow: 0 12px 28px rgba(17, 120, 255, 0.24);
}

.admin-logo strong,
.admin-logo small {
  display: block;
}

.admin-logo strong {
  color: #172b4d;
  font-size: 18px;
  font-weight: 800;
}

.admin-logo small {
  margin-top: 4px;
  color: #7b8fa6;
  font-size: 12px;
}

.admin-menu {
  border-right: 0;
  background: transparent;
}

.admin-menu :deep(.el-menu-item) {
  height: 48px;
  margin: 8px 0;
  border-radius: 14px;
  color: #5b7088;
}

.admin-menu :deep(.el-menu-item:hover) {
  color: #0e6fff;
  background: rgba(17, 120, 255, 0.08);
}

.admin-menu :deep(.el-menu-item.is-active) {
  color: #0e6fff;
  background: linear-gradient(90deg, rgba(17, 120, 255, 0.14), rgba(19, 190, 167, 0.1));
  font-weight: 700;
}

.admin-header {
  height: 82px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid rgba(210, 225, 237, 0.82);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
}

.page-title span {
  color: #7b8fa6;
  font-size: 13px;
}

.page-title h1 {
  margin: 5px 0 0;
  color: #172b4d;
  font-size: 22px;
  font-weight: 800;
}

.header-actions,
.admin-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-profile {
  height: 42px;
  padding: 5px 14px 5px 5px;
  border: 1px solid #d9e6f0;
  border-radius: 999px;
  color: #263c54;
  background: #fff;
}

.admin-avatar {
  background: linear-gradient(135deg, #1178ff, #13bea7);
}

.admin-main {
  min-height: calc(100vh - 82px);
  padding: 30px;
}

@media (max-width: 980px) {
  .admin-layout {
    display: block;
  }

  .admin-sidebar {
    position: static;
    width: 100% !important;
    height: auto;
  }

  .admin-menu {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .admin-header {
    height: auto;
    min-height: 82px;
    align-items: flex-start;
    gap: 16px;
    padding: 18px;
    flex-direction: column;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .admin-main {
    padding: 20px;
  }
}
</style>
