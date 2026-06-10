<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getStock, getPrices, addWatchlist, type Stock, type PriceData } from '../api'
import KLineChart from '../components/KLineChart.vue'

const route = useRoute()
const router = useRouter()

const stock = ref<Stock | null>(null)
const data = ref<PriceData | null>(null)
const loading = ref(false)
const sub = ref<'rsi' | 'macd' | 'kd'>('kd')

// 用白話解釋給零基礎的人看
const indicatorHint: Record<string, string> = {
  rsi: 'RSI：一支 0~100 的溫度計。超過 70 代表漲太多、過熱（可能要回檔）；低於 30 代表跌太多、過冷（可能要反彈）。',
  macd: 'MACD：看上漲/下跌的「力道」在變強還是變弱。下方柱子由綠翻紅（負轉正）代表上漲力道增強。',
  kd: 'KD：看今天股價站在最近 9 天高低範圍的哪個位置。K 線由下往上穿過 D 線，常被當作短期轉強、可買進的參考。',
}

async function load(id: string) {
  loading.value = true
  try {
    stock.value = await getStock(id)
    data.value = await getPrices(id)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '讀取失敗')
  } finally {
    loading.value = false
  }
}

async function addToWatch() {
  if (!stock.value) return
  try {
    await addWatchlist(stock.value.stock_id)
    ElMessage.success('已加入自選股')
  } catch (e: any) {
    ElMessage.warning(e?.response?.data?.detail || '加入失敗')
  }
}

onMounted(() => load(route.params.id as string))
watch(() => route.params.id, (id) => id && load(id as string))
</script>

<template>
  <div class="page" v-loading="loading">
    <el-page-header @back="router.push('/')" class="ph">
      <template #content>
        <span v-if="stock" class="title">
          {{ stock.stock_id }} {{ stock.name }}
          <el-tag size="small" type="info">{{ stock.market }}</el-tag>
          <el-tag size="small" v-if="stock.industry">{{ stock.industry }}</el-tag>
        </span>
      </template>
      <template #extra>
        <el-button type="warning" plain @click="addToWatch">加入自選股</el-button>
      </template>
    </el-page-header>

    <el-collapse v-if="data" class="help">
      <el-collapse-item title="📖 看不懂這張圖？點我（白話說明）">
        <ul class="help-list">
          <li><b>每一根 K 棒</b>＝某一天的股價。<span class="up">紅色</span>＝那天收盤比開盤高(上漲)，<span class="down">綠色</span>＝下跌（台股配色）。棒子上下的細線是那天的最高與最低價。</li>
          <li><b>三條彩色線（MA）</b>＝最近幾天的平均收盤價連起來，看趨勢。<b>MA5</b> 像「這一週的心情」(反應快)、<b>MA60</b> 像「這一季的狀態」(反應慢)。短線往上穿過長線，代表最近買氣變強。</li>
          <li><b>中間那排柱子</b>＝成交量，就是那天總共買賣了多少。柱子高＝很多人在交易。</li>
          <li><b>最下面那格</b>＝可切換的指標（KD / MACD / RSI），把滑鼠移到上方按鈕會看到各自的白話說明。</li>
        </ul>
      </el-collapse-item>
    </el-collapse>

    <el-card class="chart-card" v-if="data">
      <div class="toolbar">
        <span class="label">下方指標：</span>
        <el-radio-group v-model="sub" size="small">
          <el-radio-button value="kd">KD</el-radio-button>
          <el-radio-button value="macd">MACD</el-radio-button>
          <el-radio-button value="rsi">RSI</el-radio-button>
        </el-radio-group>
        <span class="hint">{{ indicatorHint[sub] }}</span>
      </div>
      <KLineChart :data="data" :sub="sub" />
    </el-card>
  </div>
</template>

<style scoped>
.page { max-width: 1200px; margin: 0 auto; }
.ph { margin-bottom: 16px; }
.title { font-size: 18px; font-weight: 700; display: inline-flex; gap: 8px; align-items: center; }
.chart-card { margin-top: 8px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.label { font-weight: 600; }
.hint { color: #909399; font-size: 13px; }
.help { margin-bottom: 12px; }
.help-list { margin: 0; padding-left: 18px; line-height: 1.9; color: #555; }
.up { color: #e53935; font-weight: 600; }
.down { color: #43a047; font-weight: 600; }
</style>
