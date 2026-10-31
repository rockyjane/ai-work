<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, StarFilled, Plus, Minus } from '@element-plus/icons-vue'
import { getStocks, getRankings, addWatchlist, getWatchlist, type Stock } from '../api'

const router = useRouter()
const keyword = ref('')
const stocks = ref<Stock[]>([])
const loading = ref(false)
const gainers = ref<any[]>([])
const losers = ref<any[]>([])

// 分頁：前端切片，每頁 10 筆，避免列表過長擋到下方排行榜
const pageSize = 10
const currentPage = ref(1)
const pagedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return stocks.value.slice(start, start + pageSize)
})

// 手機/平板（≤768px）：加自選改成代號前的星星 icon；桌面維持「加自選」按鈕
const isMobile = ref(window.innerWidth <= 768)
function onResize() { isMobile.value = window.innerWidth <= 768 }

// 已加入自選股的代號（供星星顯示「已加入」狀態）
const watchedIds = ref<Set<string>>(new Set())
async function loadWatched() {
  try {
    const list = await getWatchlist()
    watchedIds.value = new Set(list.map((w) => w.stock_id))
  } catch { /* 還沒資料時略過 */ }
}

// 排行榜可開合（初始展開）
const rankOpen = ref(true)

async function load() {
  loading.value = true
  try {
    stocks.value = await getStocks(keyword.value)
    currentPage.value = 1          // 每次搜尋回到第一頁
  } finally {
    loading.value = false
  }
}

async function loadRankings() {
  try {
    const r = await getRankings(5)
    gainers.value = r.gainers
    losers.value = r.losers
  } catch {
    /* 還沒匯入資料時略過 */
  }
}

function goDetail(id: string) {
  router.push(`/stock/${id}`)
}

async function addToWatch(id: string) {
  if (watchedIds.value.has(id)) {       // 已加入就不重複送
    ElMessage.info('這檔已在自選股')
    return
  }
  try {
    await addWatchlist(id)
    ElMessage.success('已加入自選股')
    watchedIds.value = new Set(watchedIds.value).add(id)   // 重新賦值觸發畫面更新（星星變實心）
  } catch (e: any) {
    ElMessage.warning(e?.response?.data?.detail || '加入失敗')
  }
}

onMounted(() => {
  load()
  loadRankings()
  loadWatched()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => window.removeEventListener('resize', onResize))
</script>

<template>
  <div class="page">
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="16" class="list-col">
        <el-card>
          <div class="search-bar">
            <el-input
              v-model="keyword"
              placeholder="輸入股票代號或名稱，例如 2330 或 台積電"
              clearable
              @keyup.enter="load"
              style="max-width: 360px"
            />
            <el-button type="primary" :loading="loading" @click="load">搜尋</el-button>
          </div>

          <el-table :data="pagedStocks" v-loading="loading" stripe @row-click="(r:any)=>goDetail(r.stock_id)" class="stock-table" style="cursor: pointer">
            <el-table-column v-if="isMobile" width="46" align="center">
              <template #default="{ row }">
                <el-icon
                  class="star-btn" :class="{ 'star-on': watchedIds.has(row.stock_id) }"
                  :title="watchedIds.has(row.stock_id) ? '已在自選股' : '加入自選股'"
                  @click.stop="addToWatch(row.stock_id)"
                >
                  <StarFilled v-if="watchedIds.has(row.stock_id)" /><Star v-else />
                </el-icon>
              </template>
            </el-table-column>
            <el-table-column prop="stock_id" label="代號" width="90" />
            <el-table-column prop="name" label="名稱" min-width="120" />
            <el-table-column prop="industry" label="產業" min-width="120" />
            <el-table-column prop="market" label="市場" width="80" />
            <el-table-column v-if="!isMobile" label="操作" width="110" fixed="right">
              <template #default="{ row }">
                <el-button v-if="watchedIds.has(row.stock_id)" size="small" type="warning" :icon="StarFilled" disabled>已加入</el-button>
                <el-button v-else size="small" type="warning" plain @click.stop="addToWatch(row.stock_id)">加自選</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="stocks.length > pageSize" class="pager">
            <el-pagination
              layout="prev, pager, next"
              :total="stocks.length"
              :page-size="pageSize"
              v-model:current-page="currentPage"
              small
              background
            />
          </div>
          <el-empty v-if="!loading && stocks.length === 0" description="沒有資料，請先在後端執行 python seed.py 匯入" />
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="8" class="rank-col">
        <el-card>
          <template #header>
            <div class="rank-head" @click="rankOpen = !rankOpen">
              <b>📊 漲跌幅排行（近一日）</b>
              <el-icon class="rank-toggle" :title="rankOpen ? '收合' : '展開'">
                <Minus v-if="rankOpen" /><Plus v-else />
              </el-icon>
            </div>
          </template>
          <div v-show="rankOpen">
            <div class="rank-title up">上漲</div>
            <div v-for="g in gainers" :key="g.stock_id" class="rank-row" @click="goDetail(g.stock_id)">
              <span>{{ g.stock_id }} {{ g.name }}</span>
              <span class="up">+{{ g.pct }}%</span>
            </div>
            <el-divider />
            <div class="rank-title down">下跌</div>
            <div v-for="l in losers" :key="l.stock_id" class="rank-row" @click="goDetail(l.stock_id)">
              <span>{{ l.stock_id }} {{ l.name }}</span>
              <span class="down">{{ l.pct }}%</span>
            </div>
            <el-empty v-if="gainers.length === 0" :image-size="60" description="尚無排行資料" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page { max-width: 1200px; margin: 0 auto; }
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.rank-title { font-weight: 700; margin: 6px 0; }
.rank-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 6px 0; cursor: pointer; border-bottom: 1px dashed #f0f0f0; }
.rank-row:hover { background: #fafafa; }
/* 股號名稱過長時以 … 省略，漲跌數字不被擠壞 */
.rank-row span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rank-row span:last-child { white-space: nowrap; flex-shrink: 0; }
.up { color: #e53935; }   /* 台股紅漲 */
.down { color: #43a047; }  /* 台股綠跌 */
/* 手機/平板：排行榜移到列表「上方」（調換位置），列表與其拉開間距 */
@media (max-width: 991px) {
  .rank-col { order: -1; margin-top: 0; }
  .list-col { margin-top: 16px; }
}
/* 排行榜開合標頭 */
.rank-head { display: flex; align-items: center; justify-content: space-between; cursor: pointer; user-select: none; }
.rank-toggle { font-size: 16px; color: #909399; }
/* 代號前的星星（手機/平板加自選用） */
.star-btn { cursor: pointer; color: #e6a23c; font-size: 20px; }
.star-btn:hover { color: #cf9236; }
.star-btn.star-on { color: #f5b301; }   /* 已加入：實心亮黃 */
/* 分頁置中 */
.pager { display: flex; justify-content: center; margin-top: 12px; }
/* 行高再寬些，較好點按 */
.stock-table :deep(.el-table__cell) { padding: 12px 0; }
</style>
