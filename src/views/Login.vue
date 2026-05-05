<template>
  <main class="login-page">
    <section class="brand-panel">
      <div class="brand-badge">
        <el-icon><Connection /></el-icon>
        智慧物业服务
      </div>
      <h1>智慧物业知识库咨询平台</h1>
      <p>
        面向业主的轻量化知识查询与智能问答入口，让缴费、报修、停车、装修等服务咨询更高效。
      </p>
      <div class="feature-grid">
        <div v-for="item in features" :key="item.title" class="feature-item">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </div>
      </div>
    </section>

    <section class="login-card">
      <div class="card-head">
        <span>平台登录</span>
        <small>普通用户 / 管理员</small>
      </div>
      <el-form :model="form" :rules="rules" ref="loginFormRef" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入账号 user 或 admin" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            placeholder="请输入密码 123456"
            type="password"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-button class="login-button" type="primary" :loading="loading" @click="handleLogin">
          登录平台
        </el-button>
      </el-form>
      <div class="register-entry">
        还没有账号？
        <button type="button" @click="openRegisterDialog">立即注册</button>
      </div>
    </section>

    <el-dialog v-model="registerVisible" title="注册账号" width="460px" @closed="resetRegisterForm">
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top" size="large">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="不少于 6 位，且同时包含字母和数字"
            type="password"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection, Lock, Message, User } from '@element-plus/icons-vue'
import { login, register } from '../api/auth'

const router = useRouter()
const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const registerLoading = ref(false)
const registerVisible = ref(false)

const form = reactive({
  username: 'user',
  password: '123456'
})

const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
    return
  }
  if (value.length < 6) {
    callback(new Error('密码长度不少于 6 位'))
    return
  }
  if (!/^(?=.*[A-Za-z])(?=.*\d).+$/.test(value)) {
    callback(new Error('密码必须同时包含字母和数字'))
    return
  }
  callback()
}

const validateConfirmPassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
    return
  }
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const features = [
  { title: '知识检索', icon: 'Search' },
  { title: '智能问答', icon: 'ChatDotRound' },
  { title: '咨询记录', icon: 'Clock' },
  { title: '反馈闭环', icon: 'EditPen' }
]

const getErrorMessage = (error, fallback = '操作失败') => {
  const data = error?.response?.data
  if (typeof data === 'string') return data
  return data?.message || error?.message || fallback
}

const normalizeLoginResult = (response) => {
  const data = response?.data || {}
  const user = data?.user || {}

  return {
    token: data?.token || data?.accessToken || data?.access_token,
    role: data?.role || user?.role || 'user',
    username: data?.username || user?.username || data?.email || user?.email || form.username
  }
}

const handleLogin = async () => {
  await loginFormRef.value.validate()
  loading.value = true
  try {
    const response = await login({
      username: form.username,
      password: form.password
    })
    const userInfo = normalizeLoginResult(response)

    sessionStorage.setItem('token', userInfo.token)
    sessionStorage.setItem('role', userInfo.role)
    sessionStorage.setItem('username', userInfo.username)
    ElMessage.success('登录成功')
    router.push(userInfo.role === 'admin' ? '/admin/home' : '/user/home')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '登录失败'))
  } finally {
    loading.value = false
  }
}

const openRegisterDialog = () => {
  registerVisible.value = true
}

const resetRegisterForm = () => {
  registerFormRef.value?.resetFields()
  Object.assign(registerForm, {
    email: '',
    password: '',
    confirmPassword: ''
  })
}

const handleRegister = async () => {
  await registerFormRef.value.validate()
  registerLoading.value = true
  try {
    await register({
      email: registerForm.email,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword
    })
    ElMessage.success('注册成功，请登录')
    form.username = registerForm.email
    registerVisible.value = false
    resetRegisterForm()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '注册失败'))
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) 420px;
  gap: 42px;
  align-items: center;
  padding: 64px clamp(28px, 6vw, 96px);
  background:
    linear-gradient(135deg, rgba(17, 120, 255, 0.14), rgba(19, 190, 167, 0.08)),
    #f4f8fb;
}

.brand-panel {
  min-height: 520px;
  padding: 54px;
  border-radius: 30px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(10, 103, 230, 0.92), rgba(18, 184, 166, 0.86)),
    url("https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1400&q=80")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 26px 70px rgba(17, 98, 191, 0.26);
  overflow: hidden;
}

.brand-badge {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(10px);
}

.brand-panel h1 {
  max-width: 720px;
  margin: 58px 0 20px;
  font-size: clamp(36px, 5vw, 62px);
  line-height: 1.12;
  font-weight: 800;
}

.brand-panel p {
  max-width: 650px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 18px;
  line-height: 1.9;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 14px;
  margin-top: 56px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.13);
  backdrop-filter: blur(10px);
}

.login-card {
  padding: 34px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 20px 60px rgba(15, 62, 111, 0.16);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 26px;
}

.card-head span {
  color: #172b4d;
  font-size: 28px;
  font-weight: 800;
}

.card-head small {
  color: #6b7c93;
}

.login-button {
  width: 100%;
  height: 46px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(120deg, #1178ff, #13bea7);
  font-weight: 700;
}

.register-entry {
  margin-top: 16px;
  color: #6b7c93;
  text-align: center;
}

.register-entry button {
  padding: 0;
  border: 0;
  color: #0e6fff;
  background: transparent;
  font-weight: 700;
  cursor: pointer;
}

.register-entry button:hover {
  color: #13bea7;
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: auto;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 22px;
  }

  .brand-panel {
    padding: 32px 24px;
  }

  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
