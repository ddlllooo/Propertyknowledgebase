<template>
  <div class="page-shell home-page">
    <section class="hero">
      <div>
        <el-tag class="hero-tag" size="large" round>AI + 物业服务知识库</el-tag>
        <h1>欢迎使用智慧物业知识库咨询平台</h1>
        <p>支持物业缴费、报修服务、停车管理、装修管理等常见问题查询。</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" :icon="Search" @click="$router.push('/user/knowledge')">
            查询知识库
          </el-button>
          <el-button size="large" :icon="ChatDotRound" @click="$router.push('/user/chat')">
            发起咨询
          </el-button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="pulse-card">
          <el-icon><Service /></el-icon>
          <span>智能匹配标准答案</span>
        </div>
        <div class="ring">
          <strong>{{ homeSummary.helpfulRateText }}</strong>
          <small>回答有帮助率</small>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card soft-card">
        <div class="stat-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="entry-grid">
      <article v-for="entry in entries" :key="entry.title" class="entry-card" @click="$router.push(entry.path)">
        <div class="entry-icon">
          <el-icon><component :is="entry.icon" /></el-icon>
        </div>
        <h3>{{ entry.title }}</h3>
        <p>{{ entry.desc }}</p>
        <el-icon class="entry-arrow"><ArrowRight /></el-icon>
      </article>
    </section>

    <section class="home-bottom">
      <div class="soft-card panel">
        <div class="section-title">
          <h2>高频问题推荐</h2>
          <el-button text type="primary" @click="$router.push('/user/knowledge')">查看更多</el-button>
        </div>
        <div class="hot-list">
          <button v-for="(question, index) in hotQuestions" :key="question" @click="goQuestion(question)">
            <span>{{ index + 1 }}</span>
            {{ question }}
          </button>
        </div>
      </div>

      <div class="soft-card panel">
        <div class="section-title">
          <h2>问题分类快捷入口</h2>
        </div>
        <div class="category-cloud">
          <el-tag
            v-for="category in quickCategories"
            :key="category.name"
            round
            size="large"
            :type="category.type"
            @click="goCategory(category.name)"
          >
            {{ category.name }}
          </el-tag>
        </div>
        <div class="category-note">
          <el-icon><TrendCharts /></el-icon>
          {{ categoryNote }}
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, ChatDotRound, Search, Service } from '@element-plus/icons-vue'
import { getHomeSummary, getQaList } from '../../api/qa'

const qaRecords = ref([])
const homeSummary = ref({
  knowledgeCount: 0,
  todayConsultCount: 0,
  topCategory: '暂无',
  categories: [],
  consultCategories: [],
  hotQuestions: [],
  helpfulRate: 0,
  helpfulRateText: '暂无数据'
})

const stats = computed(() => [
  {
    label: '知识库问题总数',
    value: homeSummary.value.knowledgeCount,
    icon: 'Collection',
    color: 'linear-gradient(135deg, #1178ff, #54a7ff)'
  },
  {
    label: '今日咨询量',
    value: homeSummary.value.todayConsultCount,
    icon: 'ChatLineRound',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '热门分类',
    value: homeSummary.value.topCategory,
    icon: 'Grid',
    color: 'linear-gradient(135deg, #7c6cff, #9f94ff)'
  },
  {
    label: '回答有帮助率',
    value: homeSummary.value.helpfulRateText,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #ffb020, #ffd26f)'
  }
])

const entries = [
  { title: '在线知识库', desc: '按关键词和分类快速查找标准答案', icon: 'Collection', path: '/user/knowledge' },
  { title: '智能问答', desc: '输入自然语言问题，自动匹配知识库答案', icon: 'ChatDotRound', path: '/user/chat' },
  { title: '我的咨询记录', desc: '查看历史问题、命中状态和人工处理情况', icon: 'Clock', path: '/user/history' }
]

const tagTypes = ['primary', 'success', 'warning', 'info', 'success', 'danger']

const hotQuestions = computed(() =>
  homeSummary.value.hotQuestions.length
    ? homeSummary.value.hotQuestions.map((item) => item.question)
    : [...qaRecords.value].sort((a, b) => b.askCount - a.askCount).slice(0, 6).map((item) => item.question)
)

const quickCategories = computed(() =>
  homeSummary.value.categories.map((item, index) => ({
    name: item.name,
    type: tagTypes[index % tagTypes.length]
  }))
)

const categoryNote = computed(() => {
  const names = homeSummary.value.categories.slice(0, 3).map((item) => item.name)
  if (!names.length) return '当前知识库暂无可用问题分类。'
  return `当前知识库主要包含 ${names.join('、')} 等分类。`
})

const goQuestion = (question) => {
  sessionStorage.setItem('knowledgeKeyword', question)
  window.location.href = '/user/knowledge'
}

const goCategory = (category) => {
  sessionStorage.setItem('knowledgeCategory', category)
  window.location.href = '/user/knowledge'
}

onMounted(async () => {
  const [qaResponse, summaryResponse] = await Promise.all([
    getQaList({ page: 1, pageSize: 100 }),
    getHomeSummary()
  ])
  qaRecords.value = qaResponse.data?.list || []
  homeSummary.value = {
    ...homeSummary.value,
    ...(summaryResponse.data || {})
  }
})
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 24px;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.55fr);
  gap: 32px;
  min-height: 330px;
  padding: clamp(30px, 5vw, 56px);
  border-radius: 28px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(9, 94, 219, 0.94), rgba(17, 188, 173, 0.86)),
    url("https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1400&q=80")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 24px 58px rgba(16, 108, 191, 0.24);
  overflow: hidden;
}

.hero > div:first-child {
  position: relative;
  z-index: 2;
}

.hero h1 {
  max-width: 760px;
  margin: 26px 0 18px;
  font-size: clamp(32px, 4.8vw, 54px);
  line-height: 1.18;
}

.hero p {
  max-width: 680px;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
}

.hero-tag {
  border: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 34px;
}

.hero-visual {
  position: relative;
  min-height: 230px;
  z-index: 1;
}

.pulse-card,
.ring {
  border: 1px solid rgba(255, 255, 255, 0.26);
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(14px);
}

.pulse-card {
  position: absolute;
  top: 18px;
  right: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 16px;
  border-radius: 16px;
}

.ring {
  position: absolute;
  right: 26px;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 190px;
  height: 190px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 18px rgba(255, 255, 255, 0.12);
}

.ring strong {
  max-width: 82%;
  font-size: clamp(30px, 3.8vw, 40px);
  line-height: 1;
  text-align: center;
  white-space: nowrap;
}

.ring small {
  max-width: 82%;
  line-height: 1.35;
  text-align: center;
}

.stats-grid,
.entry-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px;
}

.stat-icon,
.entry-icon {
  display: grid;
  place-items: center;
  color: #fff;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  font-size: 22px;
}

.stat-card strong {
  display: block;
  color: #172b4d;
  font-size: 30px;
}

.stat-card span {
  color: #6b7c93;
}

.entry-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.entry-card {
  position: relative;
  min-height: 188px;
  padding: 26px;
  border-radius: 22px;
  color: #fff;
  cursor: pointer;
  overflow: hidden;
  background: linear-gradient(135deg, #1178ff, #15b8b0);
  box-shadow: 0 18px 38px rgba(16, 108, 191, 0.18);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.entry-card:nth-child(2) {
  background: linear-gradient(135deg, #13bea7, #35a3ff);
}

.entry-card:nth-child(3) {
  background: linear-gradient(135deg, #7c6cff, #18b6a8);
}

.entry-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 46px rgba(16, 108, 191, 0.24);
}

.entry-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.18);
}

.entry-card h3 {
  margin: 24px 0 8px;
  font-size: 22px;
}

.entry-card p {
  max-width: 320px;
  margin: 0;
  color: rgba(255, 255, 255, 0.86);
}

.entry-arrow {
  position: absolute;
  right: 24px;
  bottom: 24px;
}

.home-bottom {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 18px;
}

.panel {
  padding: 24px;
}

.hot-list {
  display: grid;
  gap: 12px;
}

.hot-list button {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px;
  border: 1px solid #e3edf6;
  border-radius: 14px;
  color: #243b53;
  background: #f8fbfe;
  cursor: pointer;
  text-align: left;
}

.hot-list span {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  color: #1178ff;
  background: #eaf4ff;
  font-weight: 800;
}

.category-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.category-cloud :deep(.el-tag) {
  height: 38px;
  padding: 0 16px;
  cursor: pointer;
}

.category-note {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  padding: 16px;
  border-radius: 16px;
  color: #45627f;
  background: linear-gradient(120deg, #edf7ff, #ecfbf8);
}

@media (max-width: 1100px) {
  .hero,
  .home-bottom {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    position: absolute;
    right: clamp(18px, 5vw, 48px);
    bottom: 24px;
    width: 330px;
    height: 230px;
    min-height: 230px;
  }

  .pulse-card {
    top: 0;
    right: 0;
  }

  .ring {
    right: 16px;
    bottom: 0;
    width: 170px;
    height: 170px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 760px) {
  .hero {
    padding-bottom: 250px;
  }

  .hero-visual {
    right: 22px;
    bottom: 24px;
    width: min(330px, calc(100% - 44px));
  }

  .entry-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
