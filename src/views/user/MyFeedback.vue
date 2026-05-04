<template>
  <div class="page-shell feedback-page">
    <section class="intro-card">
      <div class="intro-icon">
        <el-icon><EditPen /></el-icon>
      </div>
      <div>
        <h2>您的反馈将帮助我们持续优化物业知识库，让回答更加准确。</h2>
        <p>所有反馈会进入知识维护流程，处理进展可在本页查看。</p>
      </div>
    </section>

    <section class="status-tabs">
      <button
        v-for="item in statusOptions"
        :key="item"
        :class="{ active: currentStatus === item }"
        @click="currentStatus = item"
      >
        {{ item }}
      </button>
    </section>

    <section class="feedback-grid">
      <article v-for="item in filteredFeedback" :key="item.id" class="feedback-card soft-card">
        <div class="feedback-head">
          <div>
            <span class="time">{{ item.time }}</span>
            <h3>{{ item.question }}</h3>
          </div>
          <el-tag :type="statusTypeMap[item.status]" round>{{ item.status }}</el-tag>
        </div>
        <div class="info-row">
          <span>反馈类型</span>
          <el-tag effect="plain">{{ item.type }}</el-tag>
        </div>
        <div class="content-block">
          <span>反馈建议</span>
          <p>{{ item.suggestion }}</p>
        </div>
        <div class="reply-block">
          <span>管理员回复</span>
          <p>{{ item.reply }}</p>
        </div>
      </article>
    </section>

    <el-empty v-if="filteredFeedback.length === 0" description="暂无该状态反馈" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { EditPen } from '@element-plus/icons-vue'
import { feedbackList } from '../../mock/mockData'

const currentStatus = ref('全部')
const statusOptions = ['全部', '待处理', '处理中', '已处理', '已忽略']

const statusTypeMap = {
  待处理: 'warning',
  处理中: 'primary',
  已处理: 'success',
  已忽略: 'info'
}

const filteredFeedback = computed(() => {
  if (currentStatus.value === '全部') return feedbackList
  return feedbackList.filter((item) => item.status === currentStatus.value)
})
</script>

<style scoped>
.feedback-page {
  display: grid;
  gap: 20px;
}

.intro-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 28px;
  border-radius: 24px;
  color: #fff;
  background:
    linear-gradient(120deg, rgba(17, 120, 255, 0.94), rgba(19, 190, 167, 0.84)),
    url("https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=80")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 20px 48px rgba(17, 120, 255, 0.2);
}

.intro-icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 60px;
  height: 60px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.18);
  font-size: 28px;
}

.intro-card h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.45;
}

.intro-card p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.86);
}

.status-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.status-tabs button {
  min-width: 84px;
  height: 38px;
  border: 1px solid #dbe8f2;
  border-radius: 999px;
  color: #4e6680;
  background: #fff;
  cursor: pointer;
}

.status-tabs button.active {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(120deg, #1178ff, #13bea7);
  box-shadow: 0 10px 24px rgba(17, 120, 255, 0.18);
}

.feedback-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.feedback-card {
  padding: 22px;
}

.feedback-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.time {
  color: #8a9db1;
  font-size: 13px;
}

.feedback-card h3 {
  margin: 8px 0 0;
  color: #172b4d;
  font-size: 19px;
  line-height: 1.45;
}

.info-row,
.content-block,
.reply-block {
  margin-top: 18px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-row > span,
.content-block > span,
.reply-block > span {
  color: #7890a8;
  font-size: 13px;
}

.content-block p,
.reply-block p {
  margin: 8px 0 0;
  color: #465f78;
  line-height: 1.75;
}

.reply-block {
  padding: 14px;
  border-radius: 16px;
  background: #f3f8fd;
}

@media (max-width: 860px) {
  .feedback-grid {
    grid-template-columns: 1fr;
  }

  .intro-card {
    align-items: flex-start;
  }
}
</style>
