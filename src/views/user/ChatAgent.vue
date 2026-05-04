<template>
  <div class="page-shell chat-page">
    <section class="assistant-card">
      <div class="assistant-icon">
        <el-icon><ChatDotRound /></el-icon>
      </div>
      <div>
        <h2>我是智慧物业助手</h2>
        <p>可以帮您快速查询缴费、报修、停车、装修等问题。</p>
      </div>
    </section>

    <section class="chat-layout">
      <div class="chat-panel soft-card">
        <div ref="messageBoxRef" class="message-box">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-row"
            :class="message.role"
          >
            <el-avatar :size="36" :class="message.role === 'ai' ? 'ai-avatar' : 'user-avatar'">
              {{ message.role === 'ai' ? 'AI' : '我' }}
            </el-avatar>
            <div class="bubble">
              <p>{{ message.content }}</p>
              <div v-if="message.meta" class="answer-meta">
                <el-tag size="small">{{ message.meta.category }}</el-tag>
                <span>参考问题：{{ message.meta.reference }}</span>
                <span>相似度：{{ message.meta.similarity }}</span>
              </div>
              <div v-if="message.role === 'ai'" class="feedback-actions">
                <el-button size="small" text type="success" @click="openFeedback('有帮助', message)">
                  有帮助
                </el-button>
                <el-button size="small" text @click="openFeedback('没帮助', message)">没帮助</el-button>
                <el-button size="small" text type="warning" @click="openFeedback('需要人工处理', message)">
                  需要人工处理
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="input-bar">
          <el-input
            v-model="inputValue"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 3 }"
            resize="none"
            placeholder="请输入您的物业服务问题"
            @keydown.enter.prevent="sendMessage()"
          />
          <el-button type="primary" :icon="Promotion" @click="sendMessage">发送</el-button>
        </div>
      </div>

      <aside class="side-panel">
        <div class="soft-card tips-card">
          <h3>使用提示</h3>
          <p>描述越具体，匹配越准确。可以包含事项、位置、时间和期望处理方式。</p>
          <div class="tip-list">
            <span>物业费怎么缴</span>
            <span>厨房漏水报修</span>
            <span>临时停车登记</span>
          </div>
        </div>

        <div class="soft-card recommend-card">
          <h3>推荐问题</h3>
          <button v-for="question in recommendedQuestions" :key="question" @click="sendMessage(question)">
            {{ question }}
          </button>
        </div>
      </aside>
    </section>

    <el-dialog v-model="feedbackVisible" title="提交反馈" width="460px">
      <el-form label-position="top">
        <el-form-item label="反馈类型">
          <el-input v-model="feedbackForm.type" disabled />
        </el-form-item>
        <el-form-item label="反馈建议">
          <el-input
            v-model="feedbackForm.content"
            type="textarea"
            :rows="4"
            placeholder="请补充您的建议，便于物业持续优化知识库"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feedbackVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFeedback">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { nextTick, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Promotion } from '@element-plus/icons-vue'

const messageBoxRef = ref()
const inputValue = ref('')
const feedbackVisible = ref(false)
const feedbackForm = reactive({
  type: '',
  content: ''
})

const messages = ref([
  {
    id: Date.now(),
    role: 'ai',
    content: '您好，我是智慧物业助手。您可以直接问我物业缴费、报修、停车、装修等问题。'
  }
])

const recommendedQuestions = [
  '物业费可以通过哪些方式缴纳？',
  '家中漏水应该如何报修？',
  '临时车辆如何进入小区？',
  '装修施工时间有什么规定？'
]

const answerRules = [
  {
    keywords: ['物业费'],
    content: '物业费可通过物业服务中心、社区小程序、银行代扣或线上支付入口缴纳，线上缴费后可查询电子凭证。',
    category: '物业缴费',
    reference: '物业费可以通过哪些方式缴纳？',
    similarity: '92%'
  },
  {
    keywords: ['报修', '漏水'],
    content: '如需报修，请在小程序提交故障位置、照片和联系方式。漏水等紧急情况请先关闭水阀，并拨打物业 24 小时值班电话。',
    category: '报修服务',
    reference: '家中漏水应该如何报修？',
    similarity: '95%'
  },
  {
    keywords: ['停车'],
    content: '停车相关业务包括月租车位办理、临时车辆登记和车牌识别维护。月租车位需提交车辆信息并完成费用缴纳。',
    category: '停车管理',
    reference: '小区停车位如何办理月租？',
    similarity: '90%'
  },
  {
    keywords: ['装修'],
    content: '装修前需提交装修申请、施工图纸、施工人员信息并签署装修管理协议，审核通过后方可进场施工。',
    category: '装修管理',
    reference: '装修前需要办理哪些手续？',
    similarity: '93%'
  }
]

const scrollToBottom = async () => {
  await nextTick()
  if (messageBoxRef.value) {
    messageBoxRef.value.scrollTop = messageBoxRef.value.scrollHeight
  }
}

const resolveAnswer = (question) => {
  const rule = answerRules.find((item) => item.keywords.some((keyword) => question.includes(keyword)))
  if (rule) {
    return {
      content: rule.content,
      meta: {
        category: rule.category,
        reference: rule.reference,
        similarity: rule.similarity
      }
    }
  }

  return {
    content: '您好，该问题暂未在知识库中找到明确答案，建议联系人工客服进一步核实。',
    meta: {
      category: '未命中',
      reference: '暂无明确参考问题',
      similarity: '38%'
    }
  }
}

const sendMessage = async (presetQuestion) => {
  const question = (presetQuestion || inputValue.value).trim()
  if (!question) {
    ElMessage.warning('请输入咨询问题')
    return
  }

  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: question
  })
  inputValue.value = ''
  await scrollToBottom()

  setTimeout(async () => {
    const answer = resolveAnswer(question)
    messages.value.push({
      id: Date.now() + 1,
      role: 'ai',
      ...answer
    })
    await scrollToBottom()
  }, 300)
}

const openFeedback = (type) => {
  feedbackForm.type = type
  feedbackForm.content = ''
  feedbackVisible.value = true
}

const submitFeedback = () => {
  feedbackVisible.value = false
  ElMessage.success('反馈已提交')
}
</script>

<style scoped>
.chat-page {
  display: grid;
  gap: 20px;
}

.assistant-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px 28px;
  border-radius: 24px;
  color: #fff;
  background: linear-gradient(120deg, #1178ff, #13bea7);
  box-shadow: 0 20px 46px rgba(17, 120, 255, 0.18);
}

.assistant-icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.18);
  font-size: 28px;
}

.assistant-card h2,
.assistant-card p {
  margin: 0;
}

.assistant-card p {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.86);
}

.chat-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 20px;
}

.chat-panel {
  display: grid;
  grid-template-rows: minmax(520px, calc(100vh - 286px)) auto;
  overflow: hidden;
}

.message-box {
  padding: 24px;
  overflow-y: auto;
}

.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.ai-avatar {
  background: linear-gradient(135deg, #1178ff, #13bea7);
}

.user-avatar {
  background: #7c8da5;
}

.bubble {
  max-width: 78%;
  padding: 15px 16px;
  border-radius: 18px;
  color: #34495e;
  background: #f3f8fd;
  line-height: 1.75;
}

.message-row.user .bubble {
  color: #fff;
  background: linear-gradient(120deg, #1178ff, #13bea7);
}

.bubble p {
  margin: 0;
}

.answer-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-top: 12px;
  color: #6b7c93;
  font-size: 13px;
}

.feedback-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.input-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 96px;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e0ebf4;
  background: #fff;
}

.input-bar .el-button {
  height: 42px;
  border-radius: 13px;
}

.side-panel {
  display: grid;
  gap: 18px;
  align-content: start;
}

.tips-card,
.recommend-card {
  padding: 22px;
}

.tips-card h3,
.recommend-card h3 {
  margin: 0 0 12px;
  color: #172b4d;
}

.tips-card p {
  margin: 0;
  color: #60758c;
  line-height: 1.75;
}

.tip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.tip-list span {
  padding: 7px 10px;
  border-radius: 999px;
  color: #1178ff;
  background: #edf7ff;
  font-size: 13px;
}

.recommend-card button {
  width: 100%;
  margin-top: 10px;
  padding: 13px;
  border: 1px solid #e2edf6;
  border-radius: 14px;
  color: #354b63;
  background: #fff;
  cursor: pointer;
  text-align: left;
}

.recommend-card button:hover {
  color: #0e6fff;
  background: #f0f7ff;
}

@media (max-width: 1020px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }

  .chat-panel {
    grid-template-rows: minmax(520px, 62vh) auto;
  }
}
</style>
