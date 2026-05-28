<template>
  <main class="login-page" ref="loginPageRef">
    <!-- 左侧品牌区 -->
    <section class="brand-section">
      <div class="brand-inner">
        <!-- 品牌标识 -->
        <div class="brand-header">
          <div class="logo-mark">
            <el-icon><Connection /></el-icon>
          </div>
          <div>
            <h2 class="logo-title">智慧物业</h2>
            <p class="logo-sub">知识库咨询平台</p>
          </div>
        </div>

        <!-- 主标题 -->
        <h1 class="brand-title">
          有问题，<br>
          <span class="accent">随时问物业</span>
        </h1>
        <p class="brand-desc">
          缴费、报修、停车、装修，AI 助手为您即时解答
        </p>

        <!-- 服务卡片网格 -->
        <div class="service-grid">
          <div class="service-card" v-for="item in services" :key="item.title">
            <div class="service-icon" :style="{ background: item.bg }">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
            </div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>

        <!-- 底部数据 -->
        <div class="brand-footer">
          <div class="footer-stat">
            <span class="stat-value">24h</span>
            <span class="stat-label">在线服务</span>
          </div>
          <div class="footer-divider"></div>
          <div class="footer-stat">
            <span class="stat-value">AI</span>
            <span class="stat-label">智能匹配</span>
          </div>
          <div class="footer-divider"></div>
          <div class="footer-stat">
            <span class="stat-value">100%</span>
            <span class="stat-label">问题覆盖</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 右侧登录区 -->
    <section class="login-section">
      <div class="login-card">
        <!-- 顶部装饰条 -->
        <div class="card-accent"></div>

        <div class="card-header">
          <div class="header-icon">
            <el-icon :size="28"><Connection /></el-icon>
          </div>
          <h2>欢迎回来</h2>
          <p>登录您的智慧物业账号</p>
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
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form>

        <div class="divider">
          <span>其他方式</span>
        </div>

        <div class="alt-actions">
          <el-button class="guest-btn" :loading="guestLoading" @click="handleGuestLogin">
            <el-icon><User /></el-icon>
            游客体验
          </el-button>
          <el-button class="register-btn" @click="openRegisterDialog">
            <el-icon><Key /></el-icon>
            注册账号
          </el-button>
        </div>

        <p class="card-footer-text">
          登录即表示您同意平台服务条款
        </p>
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
import { Connection, Key, Lock, Message, User, Van, Money, House, Setting } from '@element-plus/icons-vue'
import { login, guestLogin, register, requestPasswordReset, getPasswordResetStatus, getCaptcha } from '../api/auth'

const router = useRouter()
const loginPageRef = ref(null)
let ctx

onMounted(() => {
  if (!loginPageRef.value) return
  ctx = gsap.context(() => {
    // 品牌标识入场
    gsap.from('.brand-header', {
      x: -40,
      opacity: 0,
      duration: 0.7,
      ease: 'power3.out',
      clearProps: 'all'
    })

    // 主标题入场
    gsap.from('.brand-title', {
      y: 50,
      opacity: 0,
      duration: 0.8,
      delay: 0.2,
      ease: 'power3.out',
      clearProps: 'all'
    })

    // 描述文字入场
    gsap.from('.brand-desc', {
      y: 30,
      opacity: 0,
      duration: 0.6,
      delay: 0.5,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 服务卡片依次入场
    gsap.from('.service-card', {
      y: 40,
      opacity: 0,
      duration: 0.6,
      stagger: 0.12,
      delay: 0.6,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 底部数据入场
    gsap.from('.footer-stat', {
      y: 30,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      delay: 1.0,
      ease: 'power2.out',
      clearProps: 'all'
    })

    // 登录卡片入场
    gsap.from('.login-card', {
      y: 50,
      opacity: 0,
      duration: 0.8,
      delay: 0.3,
      ease: 'power3.out',
      clearProps: 'all'
    })

    gsap.from('.card-header', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      delay: 0.6,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.login-card .el-form-item', {
      y: 25,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      delay: 0.7,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.form-options', {
      y: 20,
      opacity: 0,
      duration: 0.4,
      delay: 1.0,
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

    gsap.from('.divider', {
      scaleX: 0,
      opacity: 0,
      duration: 0.5,
      delay: 1.2,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.alt-actions .el-button', {
      y: 15,
      opacity: 0,
      duration: 0.4,
      stagger: 0.1,
      delay: 1.3,
      ease: 'power2.out',
      clearProps: 'all'
    })

    gsap.from('.card-footer-text', {
      opacity: 0,
      duration: 0.4,
      delay: 1.5,
      ease: 'power2.out',
      clearProps: 'all'
    })
  }, loginPageRef.value)
})

onUnmounted(() => {
  ctx?.revert()
})

const services = [
  { title: '物业缴费', desc: '在线查询与缴纳', icon: 'Money', bg: 'linear-gradient(135deg, #1178ff22, #1178ff08)' },
  { title: '报修服务', desc: '快速提交报修', icon: 'Van', bg: 'linear-gradient(135deg, #13bea722, #13bea708)' },
  { title: '停车管理', desc: '车位查询登记', icon: 'House', bg: 'linear-gradient(135deg, #7c6cff22, #7c6cff08)' },
  { title: '装修咨询', desc: '规范与流程', icon: 'Setting', bg: 'linear-gradient(135deg, #ffb02022, #ffb02008)' }
]

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
  grid-template-columns: 1.1fr 0.9fr;
  background: #f8fafc;
  overflow: hidden;
}

/* 左侧品牌区 */
.brand-section {
  display: flex;
  align-items: center;
  padding: 60px 72px;
  background:
    radial-gradient(circle at 20% 80%, rgba(17, 120, 255, 0.06), transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(19, 190, 167, 0.05), transparent 50%),
    #fff;
}

.brand-inner {
  width: 100%;
  max-width: 600px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 56px;
}

.logo-mark {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  color: #fff;
  font-size: 24px;
  box-shadow: 0 8px 24px rgba(17, 120, 255, 0.25);
}

.logo-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #172b4d;
}

.logo-sub {
  margin: 2px 0 0;
  font-size: 13px;
  color: #8a9db1;
}

.brand-title {
  margin: 0 0 20px;
  font-size: clamp(36px, 5vw, 52px);
  font-weight: 800;
  line-height: 1.15;
  color: #172b4d;
  letter-spacing: -0.02em;
}

.brand-title .accent {
  color: #1178ff;
}

.brand-desc {
  margin: 0 0 48px;
  color: #6b7c93;
  font-size: 17px;
  line-height: 1.7;
}

/* 服务卡片网格 */
.service-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

.service-card {
  padding: 20px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #e8eef4;
  transition: all 0.25s;
}

.service-card:hover {
  border-color: #1178ff33;
  box-shadow: 0 8px 24px rgba(17, 120, 255, 0.08);
  transform: translateY(-2px);
}

.service-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  margin-bottom: 14px;
  color: #1178ff;
}

.service-card h3 {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
  color: #172b4d;
}

.service-card p {
  margin: 0;
  font-size: 13px;
  color: #8a9db1;
}

/* 底部数据 */
.brand-footer {
  display: flex;
  align-items: center;
  gap: 32px;
}

.footer-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #172b4d;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 12px;
  color: #8a9db1;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.footer-divider {
  width: 1px;
  height: 40px;
  background: #e8eef4;
}

/* 右侧登录区 */
.login-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 40px 44px 36px;
  border-radius: 24px;
  background: #fff;
  box-shadow:
    0 2px 8px rgba(15, 62, 111, 0.04),
    0 12px 40px rgba(15, 62, 111, 0.08);
  border: 1px solid #e8eef4;
  overflow: hidden;
}

.card-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1178ff, #13bea7, #7c6cff);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(17, 120, 255, 0.1), rgba(19, 190, 167, 0.1));
  color: #1178ff;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 800;
  color: #172b4d;
}

.card-header p {
  margin: 0;
  color: #8a9db1;
  font-size: 14px;
}

.login-card :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-card :deep(.el-input__wrapper) {
  background: #f8fafc;
  border: 1px solid #e8eef4;
  border-radius: 14px;
  box-shadow: none;
  height: 52px;
  padding: 0 18px;
  transition: all 0.25s;
}

.login-card :deep(.el-input__wrapper:hover) {
  border-color: #c0d0e0;
}

.login-card :deep(.el-input__wrapper.is-focus) {
  border-color: #1178ff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(17, 120, 255, 0.1);
}

.login-card :deep(.el-input__prefix) {
  color: #8a9db1;
}

.login-card :deep(.el-input__inner) {
  font-size: 15px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.form-options :deep(.el-checkbox__label) {
  color: #6b7c93;
  font-size: 14px;
}

.link-btn {
  padding: 0;
  border: 0;
  background: transparent;
  color: #1178ff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.link-btn:hover {
  color: #0d65e0;
}

.login-btn {
  width: 100%;
  height: 52px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #1178ff, #0e6fff);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.04em;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(17, 120, 255, 0.25);
}

.login-btn:hover {
  background: linear-gradient(135deg, #2b86ff, #1178ff);
  box-shadow: 0 8px 28px rgba(17, 120, 255, 0.35);
  transform: translateY(-2px);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(17, 120, 255, 0.2);
}

.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 28px 0 20px;
  color: #b0bec5;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e8eef4;
}

.alt-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.alt-actions :deep(.el-button) {
  height: 44px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s;
}

.guest-btn {
  border: 1px solid #d8e5ef;
  background: #fff;
  color: #5a6f85;
}

.guest-btn:hover {
  border-color: #13bea7;
  color: #13bea7;
  background: #f0faf8;
}

.register-btn {
  border: 1px solid #d8e5ef;
  background: #fff;
  color: #5a6f85;
}

.register-btn:hover {
  border-color: #1178ff;
  color: #1178ff;
  background: #f0f7ff;
}

.card-footer-text {
  margin: 24px 0 0;
  text-align: center;
  font-size: 12px;
  color: #b0bec5;
}

/* 弹窗样式 */
.temp-password-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  border-radius: 14px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
}

.temp-password-text {
  font-size: 28px;
  font-weight: 800;
  color: #172b4d;
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
  border: 1px solid #dcdfe6;
}

.captcha-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 130px;
  color: #909399;
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-section {
    padding: 48px 40px;
  }

  .brand-header {
    margin-bottom: 40px;
  }

  .service-grid {
    max-width: 480px;
    margin: 0 auto 40px;
  }

  .brand-footer {
    justify-content: center;
  }

  .login-section {
    padding: 40px;
  }

  .login-card {
    max-width: 460px;
    margin: 0 auto;
  }
}

@media (max-width: 767px) {
  .brand-section {
    padding: 32px 20px;
  }

  .brand-header {
    margin-bottom: 32px;
  }

  .brand-title {
    font-size: 32px;
  }

  .brand-desc {
    font-size: 15px;
    margin-bottom: 32px;
  }

  .service-grid {
    grid-template-columns: 1fr;
  }

  .service-card {
    padding: 16px;
  }

  .brand-footer {
    gap: 24px;
  }

  .stat-value {
    font-size: 22px;
  }

  .login-section {
    padding: 20px;
  }

  .login-card {
    padding: 32px 20px 28px;
  }

  .card-header h2 {
    font-size: 22px;
  }

  .alt-actions {
    grid-template-columns: 1fr;
  }
}
</style>
