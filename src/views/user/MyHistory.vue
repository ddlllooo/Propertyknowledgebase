<template>
  <div class="page-shell history-page">
    <section class="filter-card soft-card">
      <div>
        <h2>我的咨询记录</h2>
        <p>按关键词、分类和命中状态快速回看历史咨询。</p>
      </div>
      <div class="filters">
        <el-input v-model="keyword" clearable placeholder="搜索问题或回答" :prefix-icon="Search" />
        <el-select v-model="category" placeholder="分类">
          <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="hitStatus" placeholder="命中状态">
          <el-option v-for="item in hitOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
    </section>

    <section class="timeline-card soft-card">
      <el-timeline>
        <el-timeline-item
          v-for="item in filteredHistory"
          :key="item.id"
          :timestamp="item.time"
          placement="top"
          :type="item.hit ? 'success' : 'warning'"
        >
          <article class="history-item">
            <div class="record-head">
              <h3>{{ item.question }}</h3>
              <div class="tag-row">
                <el-tag round>{{ item.category }}</el-tag>
                <el-tag :type="item.hit ? 'success' : 'warning'" round>
                  {{ item.hit ? '已命中' : '未命中' }}
                </el-tag>
                <el-tag :type="item.needManual ? 'danger' : 'info'" round>
                  {{ item.needManual ? '需要人工' : '自动回复' }}
                </el-tag>
              </div>
            </div>
            <p>{{ item.answer }}</p>
          </article>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="filteredHistory.length === 0" description="暂无匹配咨询记录" />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getMyHistory } from '../../api/chat'
import { getCategories } from '../../api/qa'

const keyword = ref('')
const category = ref('全部')
const hitStatus = ref('all')
const chatHistory = ref([])
const categoryList = ref([])

const categories = computed(() => ['全部', ...categoryList.value.map((item) => item.name)])
const hitOptions = [
  { label: '全部状态', value: 'all' },
  { label: '已命中', value: 'hit' },
  { label: '未命中', value: 'miss' }
]

const filteredHistory = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  return chatHistory.value.filter((item) => {
    const keywordMatched =
      !normalizedKeyword || `${item.question} ${item.answer}`.toLowerCase().includes(normalizedKeyword)
    const categoryMatched = category.value === '全部' || item.category === category.value
    const hitMatched =
      hitStatus.value === 'all' ||
      (hitStatus.value === 'hit' && item.hit) ||
      (hitStatus.value === 'miss' && !item.hit)
    return keywordMatched && categoryMatched && hitMatched
  })
})

const fetchData = async () => {
  const [historyResponse, categoryResponse] = await Promise.all([getMyHistory(), getCategories()])
  chatHistory.value = historyResponse.data || []
  categoryList.value = categoryResponse.data || []
}

onMounted(fetchData)
</script>

<style scoped>
.history-page {
  display: grid;
  gap: 20px;
}

.filter-card {
  display: grid;
  grid-template-columns: minmax(260px, 0.7fr) minmax(0, 1.3fr);
  gap: 24px;
  align-items: center;
  padding: 24px;
}

.filter-card h2,
.filter-card p {
  margin: 0;
}

.filter-card h2 {
  color: #172b4d;
  font-size: 26px;
}

.filter-card p {
  margin-top: 8px;
  color: #6b7c93;
}

.filters {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 160px 160px;
  gap: 12px;
}

.timeline-card {
  padding: 26px 26px 10px;
}

.history-item {
  padding: 18px;
  border: 1px solid #e0ebf4;
  border-radius: 18px;
  background: linear-gradient(120deg, #ffffff, #f7fbff);
}

.record-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.history-item h3 {
  margin: 0;
  color: #172b4d;
  font-size: 18px;
  line-height: 1.45;
}

.history-item p {
  margin: 12px 0 0;
  color: #5d7188;
  line-height: 1.75;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  min-width: 240px;
}

@media (max-width: 980px) {
  .filter-card,
  .filters {
    grid-template-columns: 1fr;
  }

  .record-head {
    display: block;
  }

  .tag-row {
    justify-content: flex-start;
    min-width: auto;
    margin-top: 12px;
  }
}
</style>
