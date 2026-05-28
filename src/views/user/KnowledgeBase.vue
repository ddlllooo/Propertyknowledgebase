<template>
  <div class="page-shell knowledge-page" ref="pageRef">
    <section class="search-hero">
      <div>
        <h2>在线知识库</h2>
        <p>输入关键词或选择分类，快速定位物业服务标准答案。</p>
      </div>
      <el-input
        v-model="keyword"
        class="search-input"
        size="large"
        clearable
        placeholder="请输入物业费、报修、停车、装修等关键词"
        :prefix-icon="Search"
      />
    </section>

    <section class="filter-row">
      <button
        v-for="category in categoryOptions"
        :key="category"
        :class="{ active: activeCategory === category }"
        @click="activeCategory = category"
      >
        {{ category }}
      </button>
    </section>

    <section v-loading="loading" class="knowledge-grid">
      <article v-for="item in filteredList" :key="item.id" class="knowledge-card" @click="openDetail(item)">
        <div class="card-top">
          <el-tag round>{{ item.category }}</el-tag>
          <span>
            <el-icon><View /></el-icon>
            {{ item.viewCount }}
          </span>
        </div>
        <h3>{{ item.question }}</h3>
        <p>{{ item.answer }}</p>
        <div class="keyword-row">
          <el-tag v-for="tag in item.keywords" :key="tag" size="small" effect="plain">
            {{ tag }}
          </el-tag>
        </div>
      </article>
    </section>

    <el-empty v-if="filteredList.length === 0" description="暂未找到匹配问题" />

    <el-drawer v-model="drawerVisible" size="520px" title="知识详情">
      <template v-if="selectedQuestion">
        <div class="detail-block">
          <span class="detail-label">标准问题</span>
          <h2>{{ selectedQuestion.question }}</h2>
        </div>
        <div class="detail-block">
          <span class="detail-label">标准答案</span>
          <p class="answer">{{ selectedQuestion.answer }}</p>
        </div>
        <div class="detail-meta">
          <div>
            <span>分类</span>
            <el-tag round>{{ selectedQuestion.category }}</el-tag>
          </div>
          <div>
            <span>关键词</span>
            <div class="keyword-row">
              <el-tag v-for="tag in selectedQuestion.keywords" :key="tag" size="small">
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="detail-actions">
          <el-button type="primary" :icon="DocumentCopy" @click="copyAnswer">复制答案</el-button>
          <el-button type="success" :icon="CircleCheck" @click="sendHelpful('有帮助')">有帮助</el-button>
          <el-button :icon="CircleClose" @click="sendHelpful('没帮助')">没帮助</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose, DocumentCopy, Search, View } from '@element-plus/icons-vue'
import { getCategories, getQaDetail, getQaList } from '../../api/qa'
import { createFeedback } from '../../api/feedback'

const pageRef = ref(null)
let ctx

const keyword = ref('')
const activeCategory = ref('全部')
const drawerVisible = ref(false)
const selectedQuestion = ref(null)
const qaRecords = ref([])
const categories = ref([])
const loading = ref(false)
const categoryOptions = computed(() => ['全部', ...categories.value.map((item) => item.name)])

const fetchCategories = async () => {
  const response = await getCategories()
  categories.value = response.data || []
}

const fetchQaList = async () => {
  loading.value = true
  try {
    const response = await getQaList({
      keyword: keyword.value.trim() || undefined,
      category: activeCategory.value === '全部' ? undefined : activeCategory.value,
      page: 1,
      pageSize: 100
    })
    qaRecords.value = response.data?.list || []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const savedKeyword = sessionStorage.getItem('knowledgeKeyword')
  const savedCategory = sessionStorage.getItem('knowledgeCategory')
  if (savedKeyword) {
    keyword.value = savedKeyword
    sessionStorage.removeItem('knowledgeKeyword')
  }
  if (savedCategory) {
    activeCategory.value = savedCategory
    sessionStorage.removeItem('knowledgeCategory')
  }
  await Promise.all([fetchCategories(), fetchQaList()])

  if (!pageRef.value) return
  ctx = gsap.context(() => {
    // 搜索区域入场
    gsap.from('.search-hero', { y: -30, opacity: 0, duration: 0.7, ease: 'power3.out', clearProps: 'all' })

    // 筛选按钮依次出现
    gsap.from('.filter-row button', { y: 20, opacity: 0, duration: 0.4, stagger: 0.06, delay: 0.3, ease: 'power2.out', clearProps: 'all' })

    // 知识卡片入场
    gsap.from('.knowledge-card', { y: 40, opacity: 0, duration: 0.5, stagger: 0.08, delay: 0.5, ease: 'power2.out', clearProps: 'all' })
  }, pageRef.value)
})

let searchTimer = null
watch([keyword, activeCategory], () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchQaList, 250)
})

// 搜索结果变化时重新动画卡片
watch(
  () => qaRecords.value,
  async () => {
    await nextTick()
    gsap.from('.knowledge-card', { y: 30, opacity: 0, duration: 0.4, stagger: 0.06, ease: 'power2.out', clearProps: 'all' })
  }
)

onUnmounted(() => {
  clearTimeout(searchTimer)
})

const filteredList = computed(() => qaRecords.value)

const openDetail = async (item) => {
  const response = await getQaDetail(item.id)
  selectedQuestion.value = response.data
  drawerVisible.value = true
}

const copyAnswer = async () => {
  if (!selectedQuestion.value) return
  await navigator.clipboard.writeText(selectedQuestion.value.answer)
  ElMessage.success('复制成功')
}

const sendHelpful = async (type) => {
  if (!selectedQuestion.value) return
  await createFeedback({
    qaId: selectedQuestion.value.id,
    feedbackType: type,
    suggestion: type === '有帮助' ? '回答比较清楚' : '希望进一步完善答案'
  })
  ElMessage.success(`已提交“${type}”反馈`)
}
</script>

<style scoped>
.knowledge-page {
  display: grid;
  gap: 22px;
}

.search-hero {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1.1fr);
  gap: 24px;
  align-items: center;
  padding: 34px;
  border-radius: 26px;
  color: #fff;
  background:
    linear-gradient(125deg, rgba(17, 120, 255, 0.94), rgba(19, 190, 167, 0.84)),
    url("/images/bg-building.jpg")
      center/cover;
  background-blend-mode: multiply;
  box-shadow: 0 22px 52px rgba(17, 105, 205, 0.2);
}

.search-hero h2 {
  margin: 0 0 10px;
  font-size: 34px;
}

.search-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
}

.search-input {
  border-radius: 16px;
  box-shadow: 0 18px 32px rgba(11, 67, 130, 0.16);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-row button {
  min-width: 82px;
  height: 38px;
  padding: 0 18px;
  border: 1px solid #d9e8f4;
  border-radius: 999px;
  color: #4e6680;
  background: #fff;
  cursor: pointer;
  transition: all 0.18s ease;
}

.filter-row button.active,
.filter-row button:hover {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(120deg, #1178ff, #13bea7);
  box-shadow: 0 10px 24px rgba(17, 120, 255, 0.18);
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.knowledge-card {
  min-height: 230px;
  padding: 22px;
  border: 1px solid rgba(211, 226, 238, 0.9);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(21, 56, 98, 0.07);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(21, 56, 98, 0.12);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-top span {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #7a8fa6;
  font-size: 13px;
}

.knowledge-card h3 {
  margin: 18px 0 10px;
  color: #172b4d;
  font-size: 19px;
  line-height: 1.45;
}

.knowledge-card p {
  display: -webkit-box;
  min-height: 64px;
  margin: 0;
  color: #5d7188;
  line-height: 1.75;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.keyword-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.detail-block {
  margin-bottom: 26px;
}

.detail-label {
  color: #7890a8;
  font-size: 13px;
}

.detail-block h2 {
  margin: 8px 0 0;
  color: #172b4d;
  line-height: 1.4;
}

.answer {
  padding: 18px;
  border-radius: 16px;
  color: #354b63;
  line-height: 1.9;
  background: linear-gradient(120deg, #f0f7ff, #effbf8);
}

.detail-meta {
  display: grid;
  gap: 18px;
  margin-bottom: 28px;
}

.detail-meta > div > span {
  display: block;
  margin-bottom: 8px;
  color: #7890a8;
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

@media (max-width: 1120px) {
  .knowledge-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .search-hero {
    grid-template-columns: 1fr;
  }

  .knowledge-grid {
    grid-template-columns: 1fr;
  }

  .filter-row button {
    min-height: 44px;
  }
}
</style>
