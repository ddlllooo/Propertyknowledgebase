<template>
  <div class="dashboard-page">
    <section class="title-panel">
      <div>
        <el-tag class="title-tag" round>Analytics Dashboard</el-tag>
        <h1>数据看板</h1>
        <p>通过咨询数据、命中情况和反馈结果，持续优化物业知识库服务质量。</p>
      </div>
      <div class="quality-card">
        <span>当前服务质量</span>
        <strong>{{ dashboardData.overview.hitRate }}%</strong>
        <small>RAG 命中率保持稳定</small>
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

    <section class="chart-grid">
      <article class="chart-card wide">
        <div class="section-head">
          <h2>每日咨询量趋势</h2>
          <span>近 7 日咨询热度变化</span>
        </div>
        <div ref="dailyTrendRef" class="chart"></div>
      </article>

      <article class="chart-card">
        <div class="section-head">
          <h2>高频问题 TOP10</h2>
          <span>识别用户最关注事项</span>
        </div>
        <div ref="hotQuestionRef" class="chart"></div>
      </article>

      <article class="chart-card">
        <div class="section-head">
          <h2>问题分类占比</h2>
          <span>观察服务类型分布</span>
        </div>
        <div ref="categoryRatioRef" class="chart"></div>
      </article>

      <article class="chart-card">
        <div class="section-head">
          <h2>反馈状态分布</h2>
          <span>跟踪反馈处理闭环</span>
        </div>
        <div ref="feedbackStatusRef" class="chart"></div>
      </article>

      <article class="chart-card">
        <div class="section-head">
          <h2>命中率变化趋势</h2>
          <span>衡量知识库覆盖效果</span>
        </div>
        <div ref="hitRateRef" class="chart"></div>
      </article>
    </section>

    <section class="unmatched-card">
      <div class="section-head">
        <h2>未命中问题列表</h2>
        <span>将低相似度问题转化为知识库优化任务</span>
      </div>

      <el-table :data="unmatchedList" row-key="id" stripe>
        <el-table-column prop="question" label="用户问题" min-width="260" />
        <el-table-column prop="createdAt" label="咨询时间" width="160" />
        <el-table-column label="相似度" width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.similarity * 100)"
              :stroke-width="8"
              color="#ff6b6b"
            />
          </template>
        </el-table-column>
        <el-table-column prop="suggestion" label="建议处理方式" min-width="260">
          <template #default="{ row }">
            <el-tag type="warning" effect="light" round>{{ row.suggestion }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import {
  getCategoryRatio,
  getDailyTrend,
  getFeedbackStatus,
  getHitRateTrend,
  getHotQuestions,
  getOverview,
  getUnmatched
} from '../../api/dashboard'

const dailyTrendRef = ref()
const hotQuestionRef = ref()
const categoryRatioRef = ref()
const feedbackStatusRef = ref()
const hitRateRef = ref()
const chartInstances = []
const dashboardData = reactive({
  overview: {
    totalConsultCount: 0,
    todayConsultCount: 0,
    hitRate: 0,
    helpfulRate: 0,
    helpfulRateText: '暂无数据',
    pendingFeedback: 0
  },
  dailyTrend: [],
  hotQuestions: [],
  categoryRatio: [],
  feedbackStatus: [],
  hitRateTrend: [],
  unmatchedQuestions: []
})

const palette = ['#1178ff', '#13bea7', '#7c6cff', '#ffb020', '#ff6b6b', '#20b486', '#56a9ff']

const metrics = computed(() => [
  {
    label: '总咨询量',
    value: dashboardData.overview.totalConsultCount,
    icon: 'ChatLineRound',
    color: 'linear-gradient(135deg, #1178ff, #56a9ff)'
  },
  {
    label: '今日咨询量',
    value: dashboardData.overview.todayConsultCount,
    icon: 'Calendar',
    color: 'linear-gradient(135deg, #13bea7, #5fd8c9)'
  },
  {
    label: 'RAG 命中率',
    value: `${dashboardData.overview.hitRate}%`,
    icon: 'Aim',
    color: 'linear-gradient(135deg, #20b486, #74d3b4)'
  },
  {
    label: '答案有帮助率',
    value: dashboardData.overview.helpfulRateText,
    icon: 'CircleCheck',
    color: 'linear-gradient(135deg, #7c6cff, #9f94ff)'
  },
  {
    label: '待处理反馈',
    value: dashboardData.overview.pendingFeedback,
    icon: 'MessageBox',
    color: 'linear-gradient(135deg, #ffb020, #ffd36e)'
  },
  {
    label: '未命中问题',
    value: dashboardData.unmatchedQuestions.length,
    icon: 'Warning',
    color: 'linear-gradient(135deg, #ff6b6b, #ff9b8a)'
  }
])

const unmatchedList = computed(() => {
  return dashboardData.unmatchedQuestions.map((item, index) => ({
    id: `u-${index}`,
    question: item.question,
    createdAt: '-',
    similarity: 0.42,
    suggestion: item.category ? `建议补充“${item.category}”知识点并重建向量库` : `出现 ${item.count} 次，建议补充标准问答`
  }))
})

const baseTooltip = {
  trigger: 'axis',
  backgroundColor: 'rgba(23, 43, 77, 0.9)',
  borderWidth: 0,
  textStyle: { color: '#fff' }
}

const createLineOption = ({ name, data, color, yFormatter, xData, yMin, yMax }) => ({
  color: [color],
  grid: { top: 32, left: 18, right: 24, bottom: 28, containLabel: true },
  tooltip: baseTooltip,
  xAxis: {
    type: 'category',
    boundaryGap: true,
    data: xData || dashboardData.dailyTrend.map((item) => item.date),
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#d9e6f0' } },
    axisLabel: { color: '#6b7c93' }
  },
  yAxis: {
    type: 'value',
    min: yMin,
    max: yMax,
    axisLabel: {
      color: '#6b7c93',
      formatter: yFormatter || '{value}'
    },
    splitLine: { lineStyle: { color: '#edf2f7' } }
  },
  series: [
    {
      name,
      type: 'line',
      smooth: true,
      symbolSize: 8,
      data,
      clip: true,
      lineStyle: { width: 4 },
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: `${color}36` },
          { offset: 1, color: `${color}05` }
        ])
      }
    }
  ]
})

const initChart = (el, option) => {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption(option)
  chartInstances.push(chart)
}

const renderCharts = async () => {
  await nextTick()
  chartInstances.splice(0).forEach((chart) => chart.dispose())

  initChart(
    dailyTrendRef.value,
    createLineOption({
      name: '咨询量',
      data: dashboardData.dailyTrend.map((item) => item.consultCount),
      color: '#1178ff'
    })
  )

  initChart(hotQuestionRef.value, {
    color: ['#13bea7'],
    grid: { top: 18, left: 120, right: 18, bottom: 24 },
    tooltip: baseTooltip,
    xAxis: {
      type: 'value',
      axisLabel: { color: '#6b7c93' },
      splitLine: { lineStyle: { color: '#edf2f7' } }
    },
    yAxis: {
      type: 'category',
      data: dashboardData.hotQuestions.slice(0, 10).map((item) => item.question),
      axisTick: { show: false },
      axisLabel: {
        color: '#5d7188',
        width: 96,
        overflow: 'truncate'
      }
    },
    series: [
      {
        name: '咨询次数',
        type: 'bar',
        data: dashboardData.hotQuestions.slice(0, 10).map((item) => item.count),
        barWidth: 12,
        itemStyle: { borderRadius: [0, 8, 8, 0] }
      }
    ]
  })

  initChart(categoryRatioRef.value, {
    color: palette,
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, icon: 'circle', textStyle: { color: '#6b7c93' } },
    series: [
      {
        name: '分类占比',
        type: 'pie',
        radius: ['46%', '70%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        data: dashboardData.categoryRatio
      }
    ]
  })

  initChart(feedbackStatusRef.value, {
    color: ['#ffb020', '#1178ff', '#13bea7', '#7c8da5'],
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, icon: 'circle', textStyle: { color: '#6b7c93' } },
    series: [
      {
        name: '反馈状态',
        type: 'pie',
        radius: ['0%', '68%'],
        center: ['50%', '44%'],
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        data: dashboardData.feedbackStatus.map((item) => ({ name: item.status, value: item.count }))
      }
    ]
  })

  initChart(
    hitRateRef.value,
    createLineOption({
      name: '命中率',
      xData: dashboardData.hitRateTrend.map((item) => item.date),
      data: dashboardData.hitRateTrend.map((item) => item.hitRate),
      color: '#13bea7',
      yFormatter: '{value}%',
      yMin: 0,
      yMax: 100
    })
  )
}

const resizeCharts = () => {
  chartInstances.forEach((chart) => chart.resize())
}

const loadDashboardData = async () => {
  const [overview, dailyTrend, hotQuestions, hitRateTrend, categoryRatio, feedbackStatus, unmatched] = await Promise.all([
    getOverview(),
    getDailyTrend(),
    getHotQuestions(),
    getHitRateTrend(),
    getCategoryRatio(),
    getFeedbackStatus(),
    getUnmatched()
  ])

  dashboardData.overview = overview.data || dashboardData.overview
  dashboardData.dailyTrend = dailyTrend.data || []
  dashboardData.hotQuestions = hotQuestions.data || []
  dashboardData.hitRateTrend = hitRateTrend.data || []
  dashboardData.categoryRatio = categoryRatio.data || []
  dashboardData.feedbackStatus = feedbackStatus.data || []
  dashboardData.unmatchedQuestions = unmatched.data || []
}

onMounted(async () => {
  await loadDashboardData()
  await renderCharts()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  chartInstances.forEach((chart) => chart.dispose())
})
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 22px;
  max-width: 1280px;
  margin: 0 auto;
}

.title-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 32px;
  border-radius: 26px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(17, 120, 255, 0.96), rgba(19, 190, 167, 0.86)),
    url("/images/bg-dashboard.jpg")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 22px 52px rgba(16, 108, 191, 0.2);
}

.title-tag {
  border: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
}

.title-panel h1 {
  margin: 22px 0 10px;
  font-size: clamp(30px, 4vw, 46px);
}

.title-panel p {
  max-width: 730px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.8;
}

.quality-card {
  min-width: 220px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(14px);
}

.quality-card span,
.quality-card small {
  display: block;
  color: rgba(255, 255, 255, 0.82);
}

.quality-card strong {
  display: block;
  margin: 8px 0;
  font-size: 42px;
  line-height: 1;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
}

.metric-card,
.chart-card,
.unmatched-card {
  border: 1px solid rgba(211, 226, 238, 0.86);
  background: rgba(255, 255, 255, 0.94);
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

.metric-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 46px;
  height: 46px;
  border-radius: 15px;
  color: #fff;
  font-size: 22px;
}

.metric-card strong {
  display: block;
  color: #172b4d;
  font-size: 27px;
  line-height: 1.1;
}

.metric-card span {
  display: block;
  margin-top: 7px;
  color: #6b7c93;
  font-size: 13px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.chart-card,
.unmatched-card {
  padding: 24px;
  border-radius: 22px;
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.section-head {
  margin-bottom: 14px;
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

.chart {
  width: 100%;
  height: 330px;
}

.chart-card.wide .chart {
  height: 300px;
}

.unmatched-card :deep(.el-table) {
  --el-table-border-color: #e4edf5;
  --el-table-header-bg-color: #f6faff;
  --el-table-row-hover-bg-color: #f1f8ff;
  border-radius: 16px;
}

.unmatched-card :deep(.el-table th.el-table__cell) {
  color: #4c627a;
  font-weight: 700;
}

@media (max-width: 1180px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 920px) {
  .title-panel {
    align-items: flex-start;
    flex-direction: column;
  }

  .metric-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
