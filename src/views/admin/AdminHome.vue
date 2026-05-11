<template>
  <div class="admin-home">
    <section class="welcome-panel">
      <div>
        <el-tag class="welcome-tag" round>Knowledge Operation Center</el-tag>
        <h1>管理员工作台</h1>
        <p>实时掌握知识库运行状态，及时处理用户反馈与未命中问题。</p>
      </div>
      <div class="welcome-status">
        <span>RAG 服务</span>
        <strong>{{ vectorStatus.status }}</strong>
        <small>最近构建：{{ vectorStatus.lastBuildTime }}</small>
      </div>
    </section>

    <section class="metric-grid">
      <article v-for="item in metrics" :key="item.label" class="metric-card">
        <div class="metric-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="quick-grid">
      <article v-for="item in quickActions" :key="item.title" class="quick-card" @click="router.push(item.path)">
        <div class="quick-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </div>
        <el-icon class="quick-arrow"><ArrowRight /></el-icon>
      </article>
    </section>

    <section class="content-grid">
      <div class="list-card">
        <div class="section-head">
          <div>
            <h2>最近反馈</h2>
            <span>优先关注待处理和需要人工的问题</span>
          </div>
          <el-button text type="primary" @click="router.push('/admin/feedback')">处理反馈</el-button>
        </div>

        <div class="record-list">
          <article v-for="item in recentFeedback" :key="item.id" class="record-item">
            <div>
              <h3>{{ item.userQuestion }}</h3>
              <span>{{ item.createdAt }}</span>
            </div>
            <div class="record-tags">
              <el-tag :type="feedbackTypeMap[item.feedbackType]" round>{{ item.feedbackType }}</el-tag>
              <el-tag :type="statusTypeMap[item.status]" effect="light" round>{{ item.status }}</el-tag>
            </div>
          </article>
        </div>
      </div>

      <div class="chart-card">
        <div class="section-head">
          <div>
            <h2>近 7 日咨询量趋势</h2>
            <span>观察用户咨询热度变化</span>
          </div>
        </div>
        <div ref="trendChartRef" class="trend-chart"></div>
      </div>

      <div class="list-card consult-card">
        <div class="section-head">
          <div>
            <h2>最近咨询记录</h2>
            <span>查看命中分类与未命中问题</span>
          </div>
          <el-button text type="primary" @click="router.push('/admin/logs')">查看日志</el-button>
        </div>

        <div class="record-list">
          <article v-for="item in recentLogs" :key="item.id" class="record-item">
            <div>
              <h3>{{ item.question }}</h3>
              <span>{{ item.createdAt }}</span>
            </div>
            <div class="record-tags">
              <el-tag round>{{ item.category }}</el-tag>
              <el-tag :type="item.hitStatus === '已命中' ? 'success' : 'warning'" round>
                {{ item.hitStatus }}
              </el-tag>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ArrowRight } from '@element-plus/icons-vue'
import { getCategoryList } from '../../api/adminCategory'
import { getFeedbackList } from '../../api/adminFeedback'
import { getChatLogs } from '../../api/adminLog'
import { getDailyTrend, getOverview, getUnmatched } from '../../api/dashboard'
import { getVectorStatus } from '../../api/vector'

const router = useRouter()
const trendChartRef = ref()
let trendChart = null
const overview = reactive({
  knowledgeCount: 0,
  todayConsultCount: 0,
  pendingFeedback: 0,
  needHumanCount: 0,
  helpfulRate: 0,
  helpfulRateText: '暂无数据'
})
const dailyTrend = ref([])
const unmatchedQuestions = ref([])
const categories = ref([])
const recentFeedbackRecords = ref([])
const recentLogRecords = ref([])
const vectorStatus = reactive({
  status: '运行中',
  lastBuildTime: ''
})

const metrics = computed(() => [
  {
    label: '知识库总数',
    value: overview.knowledgeCount,
    icon: 'Collection',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '今日咨询量',
    value: overview.todayConsultCount,
    icon: 'ChatLineRound',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: '待处理反馈',
    value: overview.pendingFeedback,
    icon: 'MessageBox',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  },
  {
    label: '未命中问题',
    value: overview.needHumanCount || unmatchedQuestions.value.length,
    icon: 'Warning',
    color: 'linear-gradient(135deg, #ff6b6b, #ff9b8a)'
  },
  {
    label: '答案有帮助率',
    value: overview.helpfulRateText,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #7c6cff, #9f94ff)'
  },
  {
    label: '启用分类',
    value: categories.value.filter((item) => item.status === '启用').length,
    icon: 'Grid',
    color: 'linear-gradient(135deg, #20b486, #74d3b4)'
  }
])

const quickActions = [
  {
    title: '新增问答',
    desc: '维护标准问题与答案',
    icon: 'Plus',
    path: '/admin/qa'
  },
  {
    title: '处理反馈',
    desc: '跟进用户评价和建议',
    icon: 'EditPen',
    path: '/admin/feedback'
  },
  {
    title: '查看数据看板',
    desc: '分析咨询趋势和命中率',
    icon: 'DataAnalysis',
    path: '/admin/dashboard'
  },
  {
    title: '重建向量库',
    desc: '同步知识切片和索引',
    icon: 'Connection',
    path: '/admin/vector'
  }
]

const recentFeedback = computed(() => recentFeedbackRecords.value.slice(0, 5))
const recentLogs = computed(() => recentLogRecords.value.slice(0, 5))

const statusTypeMap = {
  待处理: 'warning',
  处理中: 'primary',
  已处理: 'success',
  已忽略: 'info'
}

const feedbackTypeMap = {
  有帮助: 'success',
  没帮助: 'danger',
  需要人工: 'warning'
}

const renderTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    grid: {
      top: 28,
      left: 34,
      right: 18,
      bottom: 30
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(23, 43, 77, 0.9)',
      borderWidth: 0,
      textStyle: {
        color: '#fff'
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dailyTrend.value.map((item) => item.date),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d9e6f0' } },
      axisLabel: { color: '#6b7c93' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: { color: '#6b7c93' }
    },
    series: [
      {
        name: '咨询量',
        type: 'line',
        smooth: true,
        data: dailyTrend.value.map((item) => item.consultCount),
        symbolSize: 8,
        lineStyle: {
          width: 4,
          color: '#1178ff'
        },
        itemStyle: {
          color: '#13bea7',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(17, 120, 255, 0.24)' },
            { offset: 1, color: 'rgba(19, 190, 167, 0.03)' }
          ])
        }
      }
    ]
  })
}

const resizeChart = () => {
  trendChart?.resize()
}

const loadAdminHome = async () => {
  const [overviewResponse, trendResponse, unmatchedResponse, categoryResponse, feedbackResponse, logResponse, vectorResponse] =
    await Promise.all([
      getOverview(),
      getDailyTrend(),
      getUnmatched(),
      getCategoryList(),
      getFeedbackList({ page: 1, pageSize: 5 }),
      getChatLogs({ page: 1, pageSize: 5 }),
      getVectorStatus()
    ])

  Object.assign(overview, overviewResponse.data || {})
  dailyTrend.value = trendResponse.data || []
  unmatchedQuestions.value = unmatchedResponse.data || []
  categories.value = categoryResponse.data || []
  recentFeedbackRecords.value = feedbackResponse.data?.list || []
  recentLogRecords.value = logResponse.data?.list || []
  Object.assign(vectorStatus, vectorResponse.data || {})
}

onMounted(async () => {
  await loadAdminHome()
  await renderTrendChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  trendChart?.dispose()
})
</script>

<style scoped>
.admin-home {
  display: grid;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
}

.welcome-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  min-height: 210px;
  padding: 34px;
  border-radius: 28px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(17, 120, 255, 0.96), rgba(19, 190, 167, 0.88)),
    url("/images/bg-building.jpg")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 24px 58px rgba(16, 108, 191, 0.2);
}

.welcome-tag {
  border: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
}

.welcome-panel h1 {
  margin: 24px 0 12px;
  font-size: clamp(32px, 4vw, 48px);
  line-height: 1.15;
}

.welcome-panel p {
  max-width: 640px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 17px;
}

.welcome-status {
  align-self: flex-end;
  min-width: 220px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(14px);
}

.welcome-status span,
.welcome-status small {
  display: block;
  color: rgba(255, 255, 255, 0.78);
}

.welcome-status strong {
  display: block;
  margin: 8px 0;
  font-size: 30px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
}

.metric-card,
.quick-card,
.list-card,
.chart-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.93);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.08);
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 13px;
  min-height: 116px;
  padding: 18px;
  border-radius: 20px;
}

.metric-icon,
.quick-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  color: #fff;
}

.metric-icon {
  width: 46px;
  height: 46px;
  border-radius: 15px;
  font-size: 22px;
}

.metric-card strong {
  display: block;
  color: #172b4d;
  font-size: 28px;
  line-height: 1.1;
}

.metric-card span {
  display: block;
  margin-top: 6px;
  color: #6b7c93;
  font-size: 13px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.quick-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 122px;
  padding: 22px;
  border-radius: 20px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(21, 56, 98, 0.13);
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1178ff, #13bea7);
  font-size: 22px;
}

.quick-card h3 {
  margin: 0 0 6px;
  color: #172b4d;
  font-size: 18px;
}

.quick-card p {
  margin: 0;
  color: #6b7c93;
}

.quick-arrow {
  position: absolute;
  right: 18px;
  bottom: 18px;
  color: #9badbf;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.95fr);
  gap: 18px;
}

.list-card,
.chart-card {
  padding: 24px;
  border-radius: 22px;
}

.consult-card {
  grid-column: 1 / -1;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  color: #172b4d;
  font-size: 22px;
}

.section-head span {
  display: block;
  margin-top: 6px;
  color: #7b8fa6;
  font-size: 13px;
}

.record-list {
  display: grid;
  gap: 12px;
}

.record-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  padding: 15px;
  border: 1px solid #e2edf6;
  border-radius: 16px;
  background: linear-gradient(120deg, #ffffff, #f8fbff);
}

.record-item h3 {
  margin: 0;
  color: #263c54;
  font-size: 15px;
  line-height: 1.5;
}

.record-item span {
  display: block;
  margin-top: 5px;
  color: #8a9db1;
  font-size: 12px;
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.trend-chart {
  width: 100%;
  height: 310px;
}

@media (max-width: 1180px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .quick-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .welcome-panel {
    flex-direction: column;
  }

  .welcome-status {
    align-self: stretch;
  }

  .metric-grid,
  .quick-grid {
    grid-template-columns: 1fr;
  }

  .record-item {
    grid-template-columns: 1fr;
  }

  .record-tags {
    justify-content: flex-start;
  }
}

@media (max-width: 767px) {
  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
