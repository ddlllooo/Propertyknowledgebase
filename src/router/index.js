import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import UserLayout from '../layouts/UserLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import ChangePassword from '../views/ChangePassword.vue'
import UserHome from '../views/user/UserHome.vue'
import KnowledgeBase from '../views/user/KnowledgeBase.vue'
import ChatAgent from '../views/user/ChatAgent.vue'
import MyHistory from '../views/user/MyHistory.vue'
import MyFeedback from '../views/user/MyFeedback.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import QaManage from '../views/admin/QaManage.vue'
import CategoryManage from '../views/admin/CategoryManage.vue'
import FeedbackManage from '../views/admin/FeedbackManage.vue'
import ChatLogManage from '../views/admin/ChatLogManage.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import VectorManage from '../views/admin/VectorManage.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const token = sessionStorage.getItem('token')
      const role = sessionStorage.getItem('role')

      if (!token) return '/login'
      if (role === 'admin') return '/admin/home'
      return '/user/home'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { title: '修改密码' }
  },
  {
    path: '/user',
    component: UserLayout,
    redirect: '/user/home',
    meta: { requiresAuth: true, role: 'user' },
    children: [
      {
        path: 'home',
        name: 'UserHome',
        component: UserHome,
        meta: { title: '用户首页' }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: KnowledgeBase,
        meta: { title: '在线知识库' }
      },
      {
        path: 'chat',
        name: 'ChatAgent',
        component: ChatAgent,
        meta: { title: '智能问答' }
      },
      {
        path: 'history',
        name: 'MyHistory',
        component: MyHistory,
        meta: { title: '我的咨询记录' }
      },
      {
        path: 'feedback',
        name: 'MyFeedback',
        component: MyFeedback,
        meta: { title: '我的反馈' }
      }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/home',
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: AdminHome,
        meta: { title: '工作台' }
      },
      {
        path: 'qa',
        name: 'QaManage',
        component: QaManage,
        meta: { title: '知识库维护' }
      },
      {
        path: 'category',
        name: 'CategoryManage',
        component: CategoryManage,
        meta: { title: '分类管理' }
      },
      {
        path: 'feedback',
        name: 'FeedbackManage',
        component: FeedbackManage,
        meta: { title: '反馈处理' }
      },
      {
        path: 'password-reset',
        name: 'PasswordResetManage',
        component: () => import('../views/admin/PasswordResetManage.vue'),
        meta: { title: '密码重置管理' }
      },
      {
        path: 'logs',
        name: 'ChatLogManage',
        component: ChatLogManage,
        meta: { title: '咨询日志' }
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '数据看板' }
      },
      {
        path: 'vector',
        name: 'VectorManage',
        component: VectorManage,
        meta: { title: '向量库维护' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, _from, next) => {
  const token = sessionStorage.getItem('token')
  const role = sessionStorage.getItem('role')

  if (to.path === '/login' && token) {
    next(role === 'admin' ? '/admin/home' : '/user/home')
    return
  }

  if (to.path === '/change-password') {
    if (!token) {
      next('/login')
      return
    }
    next()
    return
  }

  if (to.path.startsWith('/admin')) {
    if (!token) {
      next('/login')
      return
    }

    if (role === 'user') {
      next('/user/home')
      return
    }

    if (role !== 'admin') {
      next('/login')
      return
    }
  }

  if (to.path.startsWith('/user')) {
    if (!token) {
      next('/login')
      return
    }

    if (role === 'admin') {
      next('/admin/home')
      return
    }

    if (role !== 'user') {
      next('/login')
      return
    }
  }

  next()
})

export default router
