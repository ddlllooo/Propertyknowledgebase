<template>
  <main class="login-page" ref="loginPageRef">
    <!-- 艺术背景装饰 -->
    <div class="art-bg">
      <div class="geo geo-1"></div>
      <div class="geo geo-2"></div>
      <div class="geo geo-3"></div>
      <div class="geo geo-4"></div>
      <div class="line line-1"></div>
      <div class="line line-2"></div>
      <div class="line line-3"></div>
      <div class="dot-grid"></div>
    </div>

    <!-- 左侧品牌区 -->
    <section class="brand-section">
      <div class="brand-content">
        <div class="brand-tag">
          <span class="tag-dot"></span>
          智慧物业知识库
        </div>
        <h1 class="brand-title">
          <span class="title-line">有问题</span>
          <span class="title-line accent">问物业</span>
        </h1>
        <p class="brand-desc">
          缴费、报修、停车、装修
          <br>
          有疑问就来这里问
        </p>
        <div class="brand-stats">
          <div class="stat">
            <span class="stat-num">24h</span>
            <span class="stat-label">在线服务</span>
          </div>
          <div class="stat">
            <span class="stat-num">AI</span>
            <span class="stat-label">智能匹配</span>
          </div>
          <div class="stat">
            <span class="stat-num">100%</span>
            <span class="stat-label">问题覆盖</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 右侧登录区 -->
    <section class="login-section">
      <div class="login-card">
        <div class="card-header">
          <h2>登录</h2>
          <p>欢迎回来</p>
        </div>
        <el-form :model="form" :rules="rules" ref="loginFormRef" size="large" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入姓名或邮箱" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              placeholder="请输入密码"
              type="password"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <button type="button" class="link-btn" @click="openResetDialog">忘记密码？</button>
          </div>
          <el-button class="login-btn" type="primary" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form>
        <div class="divider">
          <span>或</span>
        </div>
        <el-button class="guest-btn" :loading="guestLoading" @click="handleGuestLogin">
          游客体验
        </el-button>
        <div class="register-link">
          还没有账号？
          <button type="button" @click="openRegisterDialog">立即注册</button>
        </div>
      </div>
    </section>

    <el-dialog v-model="registerVisible" title="注册账号" :width="registerDialogWidth" @closed="resetRegisterForm">
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top" size="large">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入您的姓名" :prefix-icon="User" />
        </el-form-item>
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
        <el-form-item label="验证码" prop="captchaCode">
          <div class="captcha-row">
            <el-input
              v-model="registerForm.captchaCode"
              placeholder="请输入验证码"
              :prefix-icon="Key"
              maxlength="4"
            />
            <img
              v-if="captchaImage"
              :src="captchaImage"
              alt="验证码"
              class="captcha-img"
              title="点击刷新验证码"
              @click="refreshCaptcha"
            />
            <div v-else class="captcha-img captcha-placeholder" @click="refreshCaptcha">加载中</div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetVisible" title="找回密码" :width="resetDialogWidth" @closed="resetResetForm">
      <!-- Step 1: Submit request -->
      <div v-if="resetStep === 1">
        <p style="color: #6b7c93; margin-bottom: 16px;">请输入您的用户名或邮箱，提交密码重置请求。如有紧急问题，请联系物业前台。</p>
        <el-input
          v-model="resetUsername"
          placeholder="请输入用户名或邮箱"
          :prefix-icon="User"
          size="large"
        />
      </div>
      <!-- Step 2: Request submitted, can query status -->
      <div v-if="resetStep === 2">
        <el-alert type="success" :closable="false" show-icon style="margin-bottom: 16px;">
          重置请求已提交，通常在 1 个工作日内处理。稍后可在此查询结果。
        </el-alert>
        <el-input
          v-model="resetUsername"
          placeholder="请输入用户名或邮箱查询状态"
          :prefix-icon="User"
          size="large"
        />
      </div>
      <!-- Step 3: Show result -->
      <div v-if="resetStep === 3">
        <div v-if="resetResult.status === '已处理'">
          <el-alert type="success" :closable="false" show-icon style="margin-bottom: 16px;">
            管理员已重置您的密码，请使用以下临时密码登录：
          </el-alert>
          <div class="temp-password-box">
            <span class="temp-password-text">{{ resetResult.tempPassword }}</span>
            <el-button type="primary" link @click="copyTempPassword">复制</el-button>
          </div>
          <p style="color: #e6a23c; margin-top: 12px; font-size: 13px;">
            注意：首次登录后必须修改密码才能正常使用系统。
          </p>
        </div>
        <div v-else-if="resetResult.status === '待处理'">
          <el-alert type="warning" :closable="false" show-icon>
            请求处理中，请稍后再试。
          </el-alert>
        </div>
        <div v-else>
          <el-alert type="info" :closable="false" show-icon>
            未找到密码重置请求。
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button v-if="resetStep === 3" @click="resetStep = 1">重新查询</el-button>
        <el-button v-if="resetStep === 1" type="primary" :loading="resetLoading" @click="handleRequestReset">提交请求</el-button>
        <el-button v-if="resetStep === 2" type="primary" :loading="resetLoading" @click="handleQueryStatus">查询状态</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { gsap } from 'gsap'
import { useDialogWidth } from '../composables/useDialogWidth'

const registerDialogWidth = useDialogWidth(460)
const resetDialogWidth = useDialogWidth(460)
import { Key, Lock, Message, User } from '@element-plus/icons-vue'
import { login, guestLogin, register, requestPasswordReset, getPasswordResetStatus, getCaptcha } from '../api/auth'

const router = useRouter()
const loginPageRef = ref(null)
let ctx

onMounted(() => {
  if (!loginPageRef.value) return
  ctx = gsap.context(() => {
    // 背景装饰动画
    gsap.from('.geo', {
      scale: 0.8,
      opacity: 0,
      duration: 1.5,
      stagger: 0.2,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 品牌区入场
    gsap.from('.brand-tag', {
      x: -30,
      opacity: 0,
      duration: 0.6,
      delay: 0.3,
      ease: 'power3.out',
      clearProps: 'all'
    })

    gsap.from('.title-line', {
      y: 60,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      delay: 0.5,
      ease: 'power3.out',
      clearProps: 'all'
    })

    gsap.from('.brand-desc', {
      y: 30,
      opacity: 0,
      duration: 0.6,
      delay: 0.9,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.stat', {
      y: 40,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      delay: 1.1,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 登录卡片入场
    gsap.from('.login-card', {
      y: 40,
      opacity: 0,
      duration: 0.8,
      delay: 0.4,
      ease: 'power3.out',
      clearProps: 'all'
    })

    gsap.from('.card-header', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 0.7,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.login-card .el-form-item', {
      y: 25,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      delay: 0.8,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.login-btn', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 1.1,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 装饰线条动画
    gsap.from('.line', {
      scaleX: 0,
      scaleY: 0,
      opacity: 0,
      duration: 1.2,
      stagger: 0.2,
      delay: 0.5,
      ease: 'power2.inOut',
      clearProps: 'all'
    })

    // 背景光晕持续动画
    gsap.to('.geo-1', {
      x: 30,
      y: 20,
      duration: 8,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })

    gsap.to('.geo-2', {
      x: -20,
      y: -30,
      duration: 10,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })

    gsap.to('.geo-3', {
      x: 25,
      y: -15,
      duration: 7,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })
  }, loginPageRef.value)
})

onUnmounted(() => {
  ctx?.revert()
})

const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const guestLoading = ref(false)
const registerLoading = ref(false)
const registerVisible = ref(false)
const resetVisible = ref(false)
const resetLoading = ref(false)
const resetStep = ref(1)
const resetUsername = ref('')
const resetResult = ref({})
const captchaImage = ref('')
const rememberMe = ref(localStorage.getItem('rememberMe') === '1')

const form = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  captchaCode: ''
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
  username: [{ required: true, message: '请输入姓名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '姓名长度应在 1 到 50 个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] },
    { max: 100, message: '邮箱长度不能超过 100 个字符', trigger: 'blur' }
  ],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  captchaCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为 4 位数字', trigger: 'blur' }
  ]
}

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
    username: data?.username || user?.username || data?.email || user?.email || form.username,
    mustChangePassword: data?.mustChangePassword || false
  }
}

const handleLogin = async () => {
  await loginFormRef.value.validate()
  loading.value = true
  try {
    const response = await login({
      username: form.username,
      password: form.password,
      rememberMe: rememberMe.value
    })
    const userInfo = normalizeLoginResult(response)

    const storage = rememberMe.value ? localStorage : sessionStorage
    storage.setItem('token', userInfo.token)
    storage.setItem('role', userInfo.role)
    storage.setItem('username', userInfo.username)
    localStorage.setItem('rememberMe', rememberMe.value ? '1' : '0')

    // 清理另一个 storage 避免冲突
    const other = rememberMe.value ? sessionStorage : localStorage
    other.removeItem('token')
    other.removeItem('role')
    other.removeItem('username')

    if (userInfo.mustChangePassword) {
      sessionStorage.setItem('mustChangePassword', 'true')
      ElMessage.warning('请先修改初始密码')
      router.push('/change-password')
      return
    }

    ElMessage.success('登录成功')
    router.push(userInfo.role === 'admin' ? '/admin/home' : '/user/home')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '登录失败'))
  } finally {
    loading.value = false
  }
}

const generateGuestId = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const handleGuestLogin = async () => {
  guestLoading.value = true
  try {
    const guestId = generateGuestId()
    const response = await guestLogin({ guestId })
    const data = response?.data || {}

    sessionStorage.setItem('token', data.token)
    sessionStorage.setItem('role', 'guest')
    sessionStorage.setItem('username', '游客')
    sessionStorage.setItem('guestId', data.guestId || guestId)

    // 清理 localStorage 避免冲突
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')

    ElMessage.success('游客登录成功')
    router.push('/user/home')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '游客登录失败'))
  } finally {
    guestLoading.value = false
  }
}

const refreshCaptcha = async () => {
  try {
    const res = await getCaptcha()
    captchaImage.value = res?.data?.image || ''
  } catch {
    captchaImage.value = ''
  }
}

const openRegisterDialog = () => {
  registerVisible.value = true
  refreshCaptcha()
}

const resetRegisterForm = () => {
  registerFormRef.value?.resetFields()
  Object.assign(registerForm, {
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    captchaCode: ''
  })
  captchaImage.value = ''
}

const handleRegister = async () => {
  await registerFormRef.value.validate()
  registerLoading.value = true
  try {
    await register({
      name: registerForm.name,
      email: registerForm.email,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword,
      captchaCode: registerForm.captchaCode
    })
    ElMessage.success('注册成功，请登录')
    form.username = registerForm.name
    registerVisible.value = false
    resetRegisterForm()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '注册失败'))
  } finally {
    registerLoading.value = false
  }
}

const openResetDialog = () => {
  resetVisible.value = true
  resetStep.value = 1
  resetUsername.value = ''
  resetResult.value = {}
}

const resetResetForm = () => {
  resetStep.value = 1
  resetUsername.value = ''
  resetResult.value = {}
}

const handleRequestReset = async () => {
  if (!resetUsername.value.trim()) {
    ElMessage.warning('请输入用户名或邮箱')
    return
  }
  resetLoading.value = true
  try {
    await requestPasswordReset({ username: resetUsername.value.trim() })
    ElMessage.success('重置请求已提交')
    resetStep.value = 2
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '提交失败'))
  } finally {
    resetLoading.value = false
  }
}

const handleQueryStatus = async () => {
  if (!resetUsername.value.trim()) {
    ElMessage.warning('请输入用户名或邮箱')
    return
  }
  resetLoading.value = true
  try {
    const response = await getPasswordResetStatus({ username: resetUsername.value.trim() })
    resetResult.value = response?.data || {}
    resetStep.value = 3
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '查询失败'))
  } finally {
    resetLoading.value = false
  }
}

const copyTempPassword = () => {
  if (resetResult.value?.tempPassword) {
    navigator.clipboard.writeText(resetResult.value.tempPassword)
    ElMessage.success('已复制到剪贴板')
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
  background: #0a0a0f;
}

/* 艺术背景装饰 */
.art-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.geo {
  position: absolute;
  border-radius: 50%;
}

.geo-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  left: -100px;
  background: radial-gradient(circle, oklch(0.5 0.2 250 / 0.15), transparent 70%);
}

.geo-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  right: -50px;
  background: radial-gradient(circle, oklch(0.6 0.25 170 / 0.12), transparent 70%);
}

.geo-3 {
  width: 300px;
  height: 300px;
  top: 40%;
  left: 30%;
  background: radial-gradient(circle, oklch(0.55 0.18 300 / 0.1), transparent 70%);
}

.geo-4 {
  width: 200px;
  height: 200px;
  top: 20%;
  right: 20%;
  background: radial-gradient(circle, oklch(0.65 0.2 200 / 0.08), transparent 70%);
}

.line {
  position: absolute;
  background: oklch(1 0 0 / 0.03);
}

.line-1 {
  width: 1px;
  height: 100%;
  left: 50%;
}

.line-2 {
  width: 100%;
  height: 1px;
  top: 30%;
}

.line-3 {
  width: 100%;
  height: 1px;
  top: 70%;
}

.dot-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(oklch(1 0 0 / 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* 左侧品牌区 */
.brand-section {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  padding: 80px;
}

.brand-content {
  max-width: 560px;
}

.brand-tag {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 100px;
  border: 1px solid oklch(1 0 0 / 0.1);
  background: oklch(1 0 0 / 0.03);
  color: oklch(0.8 0.05 250);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.05em;
  margin-bottom: 48px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: oklch(0.7 0.25 170);
  box-shadow: 0 0 12px oklch(0.7 0.25 170 / 0.6);
}

.brand-title {
  margin: 0 0 32px;
}

.title-line {
  display: block;
  font-size: clamp(56px, 8vw, 96px);
  font-weight: 800;
  line-height: 1.05;
  color: oklch(0.95 0.02 250);
  letter-spacing: -0.03em;
}

.title-line.accent {
  color: oklch(0.75 0.25 170);
  text-shadow: 0 0 60px oklch(0.7 0.25 170 / 0.3);
}

.brand-desc {
  margin: 0 0 56px;
  color: oklch(0.6 0.02 250);
  font-size: 18px;
  line-height: 1.8;
}

.brand-stats {
  display: flex;
  gap: 48px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-num {
  font-size: 32px;
  font-weight: 800;
  color: oklch(0.9 0.05 250);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 13px;
  color: oklch(0.5 0.02 250);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* 右侧登录区 */
.login-section {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 48px;
  border-radius: 24px;
  background: oklch(0.12 0.02 250);
  border: 1px solid oklch(1 0 0 / 0.06);
  backdrop-filter: blur(20px);
}

.card-header {
  margin-bottom: 40px;
}

.card-header h2 {
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 800;
  color: oklch(0.95 0.02 250);
  letter-spacing: -0.02em;
}

.card-header p {
  margin: 0;
  color: oklch(0.5 0.02 250);
  font-size: 15px;
}

.login-card :deep(.el-input__wrapper) {
  background: oklch(0.15 0.02 250);
  border: 1px solid oklch(1 0 0 / 0.08);
  border-radius: 14px;
  box-shadow: none;
  height: 52px;
}

.login-card :deep(.el-input__wrapper:hover),
.login-card :deep(.el-input__wrapper.is-focus) {
  border-color: oklch(0.7 0.25 170);
  box-shadow: 0 0 0 3px oklch(0.7 0.25 170 / 0.1);
}

.login-card :deep(.el-input__inner) {
  color: oklch(0.9 0.02 250);
}

.login-card :deep(.el-input__inner::placeholder) {
  color: oklch(0.4 0.02 250);
}

.login-card :deep(.el-input__prefix) {
  color: oklch(0.5 0.02 250);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.form-options :deep(.el-checkbox__label) {
  color: oklch(0.5 0.02 250);
  font-size: 14px;
}

.form-options :deep(.el-checkbox__inner) {
  background: oklch(0.15 0.02 250);
  border-color: oklch(1 0 0 / 0.15);
}

.link-btn {
  padding: 0;
  border: 0;
  background: transparent;
  color: oklch(0.7 0.25 170);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.link-btn:hover {
  color: oklch(0.8 0.25 170);
}

.login-btn {
  width: 100%;
  height: 52px;
  border: 0;
  border-radius: 14px;
  background: oklch(0.65 0.25 170);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.3s;
}

.login-btn:hover {
  background: oklch(0.7 0.25 170);
  box-shadow: 0 8px 32px oklch(0.65 0.25 170 / 0.4);
  transform: translateY(-2px);
}

.login-btn:active {
  transform: translateY(0);
}

.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 28px 0;
  color: oklch(0.4 0.02 250);
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: oklch(1 0 0 / 0.06);
}

.guest-btn {
  width: 100%;
  height: 48px;
  border-radius: 14px;
  border: 1px solid oklch(1 0 0 / 0.1);
  background: transparent;
  color: oklch(0.7 0.02 250);
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s;
}

.guest-btn:hover {
  border-color: oklch(0.7 0.25 170);
  color: oklch(0.7 0.25 170);
  background: oklch(0.7 0.25 170 / 0.05);
}

.register-link {
  margin-top: 32px;
  text-align: center;
  color: oklch(0.5 0.02 250);
  font-size: 14px;
}

.register-link button {
  padding: 0;
  border: 0;
  background: transparent;
  color: oklch(0.7 0.25 170);
  font-weight: 700;
  cursor: pointer;
  transition: color 0.2s;
}

.register-link button:hover {
  color: oklch(0.8 0.25 170);
}

/* 弹窗样式 */
.temp-password-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  border-radius: 14px;
  background: oklch(0.15 0.02 250);
  border: 1px solid oklch(0.7 0.25 170 / 0.3);
}

.temp-password-text {
  font-size: 28px;
  font-weight: 800;
  color: oklch(0.9 0.02 250);
  letter-spacing: 4px;
  font-family: monospace;
}

.captcha-row {
  display: flex;
  gap: 12px;
  width: 100%;
}

.captcha-row .el-input {
  flex: 1;
}

.captcha-img {
  height: 44px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid oklch(1 0 0 / 0.1);
}

.captcha-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 130px;
  color: oklch(0.5 0.02 250);
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-section {
    padding: 60px 40px 40px;
  }

  .brand-content {
    max-width: 100%;
    text-align: center;
  }

  .brand-tag {
    margin-bottom: 32px;
  }

  .brand-stats {
    justify-content: center;
  }

  .login-section {
    padding: 40px;
  }
}

@media (max-width: 767px) {
  .brand-section {
    padding: 40px 20px 32px;
  }

  .title-line {
    font-size: 48px;
  }

  .brand-desc {
    font-size: 15px;
    margin-bottom: 32px;
  }

  .brand-stats {
    gap: 32px;
  }

  .stat-num {
    font-size: 24px;
  }

  .login-section {
    padding: 20px;
  }

  .login-card {
    padding: 32px 24px;
  }
}
</style>
