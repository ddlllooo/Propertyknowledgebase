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
                <span>来源：{{ message.meta.answerSource }}</span>
                <span>参考问题：{{ message.meta.reference }}</span>
                <span>相似度：{{ message.meta.similarity }}</span>
              </div>
              <div v-if="message.canFeedback" class="feedback-actions">
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
            :disabled="sending"
            placeholder="请输入您的物业服务问题"
            maxlength="200"
            show-word-limit
            @keydown="onTextareaKeydown"
          />
          <el-button type="primary" :icon="Promotion" :loading="sending" @click="sendMessage">发送</el-button>
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
import { nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Promotion } from '@element-plus/icons-vue'
import { sendQuestion } from '../../api/chat'
import { createFeedback } from '../../api/feedback'

const CHAT_SESSION_KEY = 'userChatAgentMessages'

const messageBoxRef = ref()
const inputValue = ref('')
const feedbackVisible = ref(false)
const activeFeedbackMessage = ref(null)
const sending = ref(false)
const feedbackForm = reactive({
  type: '',
  content: ''
})

const defaultMessages = () => [
  {
    id: Date.now(),
    role: 'ai',
    content: '您好，我是智慧物业助手。您可以直接问我物业缴费、报修、停车、装修等问题。',
    canFeedback: false
  }
]

const messages = ref(defaultMessages())

const recommendedQuestions = [
  '物业费可以通过哪些方式缴纳？',
  '家中漏水应该如何报修？',
  '临时车辆如何进入小区？',
  '装修施工时间有什么规定？'
]

const scrollToBottom = async () => {
  await nextTick()
  if (messageBoxRef.value) {
    messageBoxRef.value.scrollTop = messageBoxRef.value.scrollHeight
  }
}

const loadCachedMessages = () => {
  const cached = sessionStorage.getItem(CHAT_SESSION_KEY)
  if (!cached) return

  try {
    const parsedMessages = JSON.parse(cached)
    if (Array.isArray(parsedMessages) && parsedMessages.length) {
      messages.value = parsedMessages
    }
  } catch {
    sessionStorage.removeItem(CHAT_SESSION_KEY)
  }
}

watch(
  messages,
  (value) => {
    sessionStorage.setItem(CHAT_SESSION_KEY, JSON.stringify(value))
  },
  { deep: true }
)

const QUESTION_MAX_LENGTH = 200

const sendMessage = async (presetQuestion) => {
  const question = (presetQuestion || inputValue.value).trim()
  if (!question) {
    ElMessage.warning('请输入咨询问题')
    return
  }
  if (question.length > QUESTION_MAX_LENGTH) {
    ElMessage.warning(`问题长度不能超过 ${QUESTION_MAX_LENGTH} 个字符`)
    return
  }

  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: question
  })
  inputValue.value = ''
  await scrollToBottom()

  sending.value = true
  try {
    const response = await sendQuestion({ question })
    const answer = response.data
    messages.value.push({
      id: Date.now() + 1,
      role: 'ai',
      content: answer.answer,
      chatLogId: answer.chatLogId,
      canFeedback: Boolean(answer.chatLogId),
      meta: {
        category: answer.category,
        answerSource: answer.answerSource || '知识库',
        reference: answer.matchedQuestion || '暂无明确参考问题',
        similarity: `${Math.round(answer.similarity * 100)}%`
      }
    })
    await scrollToBottom()
  } catch (error) {
    ElMessage.error('问题发送失败')
  } finally {
    sending.value = false
  }
}

const onTextareaKeydown = (e) => {
  if (e.isComposing) return
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const openFeedback = (type, message) => {
  activeFeedbackMessage.value = message
  feedbackForm.type = type === '需要人工处理' ? '需要人工' : type
  feedbackForm.content = ''
  feedbackVisible.value = true
}

const submitFeedback = async () => {
  if (!activeFeedbackMessage.value?.chatLogId) {
    ElMessage.warning('当前回答暂无法提交反馈')
    return
  }
  try {
    await createFeedback({
      chatLogId: activeFeedbackMessage.value.chatLogId,
      feedbackType: feedbackForm.type,
      suggestion: feedbackForm.content
    })
    feedbackVisible.value = false
    ElMessage.success('反馈已提交')
  } catch {
    ElMessage.error('反馈提交失败，请稍后重试')
  }
}

onMounted(async () => {
  loadCachedMessages()
  await scrollToBottom()
})
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
