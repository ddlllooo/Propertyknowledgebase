<template>
  <el-container class="user-layout">
    <el-aside v-if="!isMobile" width="248px" class="sidebar">
      <router-link class="logo" to="/user/home">
        <span class="logo-icon"><el-icon><HomeFilled /></el-icon></span>
        <span>
          <strong>智慧物业</strong>
          <small>知识咨询平台</small>
        </span>
      </router-link>

      <el-menu :default-active="route.path" router class="nav-menu">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div class="topbar-left">
          <button v-if="isMobile" class="hamburger" @click="drawerVisible = true">
            <el-icon :size="22"><Expand /></el-icon>
          </button>
          <div>
            <p class="eyebrow">普通用户端</p>
            <h1>{{ currentTitle }}</h1>
          </div>
        </div>
        <div class="top-actions">
          <el-tag effect="light" round>在线服务</el-tag>
          <el-dropdown @command="handleCommand">
            <button class="user-button">
              <el-avatar :size="34" class="avatar">{{ username.slice(0, 1).toUpperCase() }}</el-avatar>
              <span>{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>

    <!-- Mobile drawer -->
    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="280px"
      :show-close="false"
      class="mobile-drawer"
    >
      <template #header>
        <router-link class="logo" to="/user/home" @click="drawerVisible = false">
          <span class="logo-icon"><el-icon><HomeFilled /></el-icon></span>
          <span>
            <strong>智慧物业</strong>
            <small>知识咨询平台</small>
          </span>
        </router-link>
      </template>
      <el-menu :default-active="route.path" router class="drawer-menu">
        <el-menu-item
          v-for="item in menus"
          :key="item.path"
          :index="item.path"
          @click="drawerVisible = false"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

    <!-- Mobile bottom nav -->
    <nav v-if="isMobile" class="mobile-bottom-nav">
      <router-link
        v-for="item in menus"
        :key="item.path"
        :to="item.path"
        class="bottom-nav-item"
        :class="{ active: route.path === item.path }"
      >
        <el-icon :size="20"><component :is="item.icon" /></el-icon>
        <span>{{ item.label.replace('我的', '') }}</span>
      </router-link>
    </nav>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ArrowDown, HomeFilled, SwitchButton, Expand } from '@element-plus/icons-vue'
import { isMobile } from '../composables/useBreakpoint'

const route = useRoute()
const router = useRouter()
const username = sessionStorage.getItem('username') || localStorage.getItem('username') || 'user'
const drawerVisible = ref(false)

const menus = [
  { label: '用户首页', path: '/user/home', icon: 'DataAnalysis' },
  { label: '在线知识库', path: '/user/knowledge', icon: 'Collection' },
  { label: '智能问答', path: '/user/chat', icon: 'ChatDotRound' },
  { label: '咨询记录', path: '/user/history', icon: 'Clock' },
  { label: '我的反馈', path: '/user/feedback', icon: 'EditPen' }
]

const currentTitle = computed(() => route.meta.title || '智慧物业服务')

const handleCommand = async (command) => {
  if (command !== 'logout') return
  await ElMessageBox.confirm('确认退出当前账号吗？', '退出登录', {
    type: 'warning',
    confirmButtonText: '退出',
    cancelButtonText: '取消'
  })
  sessionStorage.clear()
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  background: #f4f8fb;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 24px 18px;
  border-right: 1px solid rgba(207, 224, 237, 0.85);
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(18px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 8px 24px;
}

.logo-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  box-shadow: 0 12px 28px rgba(17, 120, 255, 0.24);
}

.logo strong,
.logo small {
  display: block;
}

.logo strong {
  color: #152b4a;
  font-size: 19px;
}

.logo small {
  margin-top: 3px;
  color: #7890a8;
}

.nav-menu {
  border-right: 0;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  height: 48px;
  margin: 8px 0;
  border-radius: 14px;
  color: #5a6f85;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: #0e6fff;
  background: linear-gradient(90deg, rgba(17, 120, 255, 0.13), rgba(19, 190, 167, 0.1));
  font-weight: 700;
}

.topbar {
  height: 82px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 1px solid rgba(207, 224, 237, 0.8);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(16px);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hamburger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--tap-min);
  height: var(--tap-min);
  border: none;
  border-radius: 12px;
  background: transparent;
  color: #172b4d;
  cursor: pointer;
}

.hamburger:active {
  background: rgba(17, 120, 255, 0.08);
}

.eyebrow {
  margin: 0 0 5px;
  color: #7890a8;
  font-size: 13px;
}

.topbar h1 {
  margin: 0;
  color: #172b4d;
  font-size: 22px;
}

.top-actions,
.user-button {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-button {
  height: 42px;
  padding: 5px 12px 5px 5px;
  border: 1px solid #d8e5ef;
  border-radius: 999px;
  color: #243b53;
  background: #fff;
  cursor: pointer;
}

.avatar {
  background: linear-gradient(135deg, #1178ff, #13bea7);
}

.content {
  padding: 28px;
}

/* Drawer menu */
.drawer-menu {
  border-right: 0;
  background: transparent;
}

.drawer-menu :deep(.el-menu-item) {
  height: 48px;
  margin: 6px 0;
  border-radius: 14px;
  color: #5a6f85;
}

.drawer-menu :deep(.el-menu-item.is-active) {
  color: #0e6fff;
  background: linear-gradient(90deg, rgba(17, 120, 255, 0.13), rgba(19, 190, 167, 0.1));
  font-weight: 700;
}

/* Bottom navigation */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  height: 60px;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  border-top: 1px solid rgba(207, 224, 237, 0.8);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
}

.bottom-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: #7890a8;
  font-size: 11px;
  text-decoration: none;
  transition: color 0.2s;
}

.bottom-nav-item.active {
  color: #0e6fff;
}

.bottom-nav-item span {
  line-height: 1.2;
}

@media (max-width: 767px) {
  .user-layout {
    display: block;
  }

  .topbar {
    height: 60px;
    padding: 0 16px;
  }

  .topbar h1 {
    font-size: 18px;
  }

  .eyebrow {
    display: none;
  }

  .top-actions .el-tag {
    display: none;
  }

  .user-button span {
    display: none;
  }

  .content {
    padding: 16px;
    padding-bottom: 80px;
  }
}
</style>
