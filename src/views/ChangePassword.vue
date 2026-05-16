<template>
  <main class="change-password-page">
    <section class="change-password-card">
      <div class="card-head">
        <span>修改密码</span>
        <small>首次登录需修改初始密码</small>
      </div>
      <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 20px;">
        您正在使用临时密码登录，请设置新密码后才能正常使用系统。
      </el-alert>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleSubmit">
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            placeholder="不少于 6 位，且同时包含字母和数字"
            type="password"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            placeholder="请再次输入新密码"
            type="password"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-button class="submit-button" type="primary" :loading="loading" @click="handleSubmit">
          确认修改
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import { changePassword } from '../api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  newPassword: '',
  confirmPassword: ''
})

const validatePassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
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
    callback(new Error('请确认新密码'))
    return
  }
  if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const rules = {
  newPassword: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleSubmit = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await changePassword({ newPassword: form.newPassword })
    ElMessage.success('密码修改成功')
    sessionStorage.removeItem('mustChangePassword')
    const role = sessionStorage.getItem('role') || localStorage.getItem('role')
    router.push(role === 'admin' ? '/admin/home' : '/user/home')
  } catch (error) {
    const data = error?.response?.data
    const message = typeof data === 'string' ? data : data?.message || error?.message || '修改失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.change-password-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px;
  background:
    linear-gradient(135deg, rgba(17, 120, 255, 0.14), rgba(19, 190, 167, 0.08)),
    #f4f8fb;
}

.change-password-card {
  width: 100%;
  max-width: 440px;
  padding: 34px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 20px 60px rgba(15, 62, 111, 0.16);
}

.card-head {
  margin-bottom: 26px;
}

.card-head span {
  display: block;
  color: #172b4d;
  font-size: 28px;
  font-weight: 800;
}

.card-head small {
  color: #6b7c93;
}

.submit-button {
  width: 100%;
  height: 46px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(120deg, #1178ff, #13bea7);
  font-weight: 700;
}

@media (max-width: 767px) {
  .change-password-page {
    padding: 20px;
  }

  .change-password-card {
    padding: 24px;
  }

  .card-head span {
    font-size: 22px;
  }
}
</style>
