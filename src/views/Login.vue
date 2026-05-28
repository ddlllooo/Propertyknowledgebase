<template>
  <main class="login-page" ref="loginPageRef">
    <section class="brand-panel">
      <div class="floating-circle circle-1"></div>
      <div class="floating-circle circle-2"></div>
      <div class="floating-circle circle-3"></div>
      <div class="brand-badge">
        <el-icon><Connection /></el-icon>
        业主服务
      </div>
      <h1>有问题？问物业</h1>
      <p>
        缴费、报修、停车、装修——有疑问就来这里问，随时为您解答。
      </p>
    </section>

    <section class="login-card">
      <div class="card-head">
        <span>登录</span>
        <small>欢迎使用</small>
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
        <div class="remember-row">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
        </div>
        <el-button class="login-button" type="primary" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
      <div class="register-entry">
        还没有账号？
        <button type="button" @click="openRegisterDialog">立即注册</button>
      </div>
      <div class="forgot-entry">
        <button type="button" @click="openResetDialog">忘记密码？</button>
      </div>
      <div class="guest-entry">
        <el-button class="guest-button" :loading="guestLoading" @click="handleGuestLogin">
          游客体验
        </el-button>
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
import { Connection, Key, Lock, Message, User } from '@element-plus/icons-vue'
import { login, guestLogin, register, requestPasswordReset, getPasswordResetStatus, getCaptcha } from '../api/auth'

const router = useRouter()
const loginPageRef = ref(null)
let ctx

onMounted(() => {
  if (!loginPageRef.value) return
  ctx = gsap.context(() => {
    // 品牌面板滑入
    gsap.from('.brand-panel', {
      x: -80,
      opacity: 0,
      duration: 0.8,
      ease: 'power3.out',
      clearProps: 'all'
    })
    // 品牌面板内元素依次淡入
    gsap.from('.brand-badge', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 0.3,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.brand-panel h1', {
      y: 30,
      opacity: 0,
      duration: 0.6,
      delay: 0.5,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.brand-panel p', {
      y: 30,
      opacity: 0,
      duration: 0.6,
      delay: 0.7,
      ease: 'power2.out',
      clearProps: 'all'
    })
    // 登录卡片滑入
    gsap.from('.login-card', {
      x: 80,
      opacity: 0,
      duration: 0.8,
      ease: 'power3.out',
      clearProps: 'all'
    })
    // 登录卡片内元素依次淡入
    gsap.from('.card-head', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 0.4,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.login-card .el-form-item', {
      y: 25,
      opacity: 0,
      duration: 0.5,
      stagger: 0.12,
      delay: 0.5,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.remember-row', {
      y: 20,
      opacity: 0,
      duration: 0.4,
      delay: 0.9,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.login-button', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 1.0,
      ease: 'power2.out',
      clearProps: 'all'
    })
    gsap.from('.register-entry, .forgot-entry, .guest-entry', {
      y: 15,
      opacity: 0,
      duration: 0.4,
      stagger: 0.1,
      delay: 1.1,
      ease: 'power2.out',
      clearProps: 'all'
    })
    // 浮动圆圈持续动画
    gsap.to('.circle-1', {
      y: 20,
      x: -10,
      duration: 4,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })
    gsap.to('.circle-2', {
      y: -15,
      x: 10,
      duration: 5,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    })
    gsap.to('.circle-3', {
      y: 12,
      x: -8,
      duration: 3.5,
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
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 460px);
  gap: 42px;
  align-items: center;
  padding: 64px clamp(28px, 6vw, 96px);
  background:
    linear-gradient(135deg, rgba(17, 120, 255, 0.14), rgba(19, 190, 167, 0.08)),
    #f4f8fb;
}

.brand-panel {
  position: relative;
  min-height: 420px;
  padding: 48px;
  border-radius: 24px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(10, 103, 230, 0.92), rgba(18, 184, 166, 0.86)),
    url("/images/bg-login.jpg")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 16px 48px rgba(17, 98, 191, 0.18);
  overflow: hidden;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -60px;
  right: -40px;
}

.circle-2 {
  width: 140px;
  height: 140px;
  bottom: -30px;
  left: -20px;
}

.circle-3 {
  width: 80px;
  height: 80px;
  top: 50%;
  right: 20%;
}

.brand-badge {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}

.brand-panel h1 {
  max-width: 720px;
  margin: 36px 0 16px;
  font-size: clamp(26px, 3.5vw, 40px);
  line-height: 1.2;
  font-weight: 700;
}

.brand-panel p {
  max-width: 650px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 18px;
  line-height: 1.9;
}

.login-card {
  padding: 40px;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 8px 32px rgba(15, 62, 111, 0.1);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 26px;
}

.card-head span {
  color: #172b4d;
  font-size: 32px;
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
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(17, 120, 255, 0.35);
}

.login-button:active {
  transform: translateY(0);
}

.remember-row {
  margin-bottom: 16px;
}

.remember-row :deep(.el-checkbox__label) {
  color: #6b7c93;
  font-size: 14px;
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
  transition: color 0.2s ease;
}

.register-entry button:hover {
  color: #13bea7;
}

.forgot-entry {
  margin-top: 8px;
  text-align: center;
}

.forgot-entry button {
  padding: 0;
  border: 0;
  color: #6b7c93;
  background: transparent;
  font-size: 13px;
  cursor: pointer;
}

.forgot-entry button:hover {
  color: #0e6fff;
}

.guest-entry {
  margin-top: 20px;
  text-align: center;
}

.guest-button {
  width: 100%;
  height: 42px;
  border-radius: 14px;
  border: 1px solid #d8e5ef;
  color: #5a6f85;
  background: #fff;
  font-weight: 600;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.guest-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(17, 120, 255, 0.15);
  color: #1178ff;
  border-color: #b3d8ff;
  background: #f0f7ff;
}

.temp-password-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
}

.temp-password-text {
  font-size: 24px;
  font-weight: 800;
  color: #172b4d;
  letter-spacing: 2px;
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
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #dcdfe6;
}

.captcha-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  color: #909399;
  font-size: 13px;
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: auto;
  }
}

@media (max-width: 767px) {
  .login-page {
    padding: 16px;
  }

  .brand-panel {
    padding: 24px 20px;
  }

  .brand-panel h1 {
    font-size: clamp(24px, 6vw, 36px);
    margin: 24px 0 12px;
  }

  .brand-panel p {
    font-size: 15px;
    line-height: 1.7;
  }

  .login-card {
    padding: 24px;
  }

  .captcha-row {
    flex-direction: column;
    gap: 12px;
  }

  .captcha-row .el-input {
    flex: 1;
  }
}
</style>
