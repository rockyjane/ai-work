<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getStocks, getRankings, addWatchlist, type Stock } from '../api'

const router = useRouter()
const keyword = ref('')
const stocks = ref<Stock[]>([])
const loading = ref(false)
const gainers = ref<any[]>([])
const losers = ref<any[]>([])

async function load() {
  loading.value = true
  try {
    stocks.value = await getStocks(keyword.value)
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
  try {
    await addWatchlist(id)
    ElMessage.success('已加入自選股')
  } catch (e: any) {
    ElMessage.warning(e?.response?.data?.detail || '加入失敗')
  }
}

onMounted(() => {
  load()
  loadRankings()
})
</script>

<template>
  <div class="page">
    <el-row :gutter="16">
      <el-col :span="16">
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

          <el-table :data="stocks" v-loading="loading" stripe @row-click="(r:any)=>goDetail(r.stock_id)" style="cursor: pointer">
            <el-table-column prop="stock_id" label="代號" width="90" />
            <el-table-column prop="name" label="名稱" width="120" />
            <el-table-column prop="industry" label="產業" />
            <el-table-column prop="market" label="市場" width="80" />
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button size="small" @click.stop="goDetail(row.stock_id)">看圖</el-button>
                <el-button size="small" type="warning" plain @click.stop="addToWatch(row.stock_id)">加自選</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && stocks.length === 0" description="沒有資料，請先在後端執行 python seed.py 匯入" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header><b>📊 漲跌幅排行（近一日）</b></template>
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page { max-width: 1200px; margin: 0 auto; }
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.rank-title { font-weight: 700; margin: 6px 0; }
.rank-row { display: flex; justify-content: space-between; padding: 6px 0; cursor: pointer; border-bottom: 1px dashed #f0f0f0; }
.rank-row:hover { background: #fafafa; }
.up { color: #e53935; }   /* 台股紅漲 */
.down { color: #43a047; }  /* 台股綠跌 */
</style>
