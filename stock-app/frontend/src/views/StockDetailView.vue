<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getStock, getPrices, getValuation, getFinancials, getRevenue, addWatchlist, type Stock, type PriceData, type Valuation, type Financial, type Revenue } from '../api'
import KLineChart from '../components/KLineChart.vue'

const route = useRoute()
const router = useRouter()

const stock = ref<Stock | null>(null)
const data = ref<PriceData | null>(null)
const valuation = ref<Valuation | null>(null)   // 最新一筆評價指標
const financials = ref<Financial[]>([])          // EPS 近幾季（由新到舊）
const revenues = ref<Revenue[]>([])              // 月營收近幾個月（由新到舊）
const loading = ref(false)
const sub = ref<'rsi' | 'macd' | 'kd'>('kd')

// EPS 趨勢小圖資料：轉成由舊到新、算出每根長條的相對高度(%)
const epsBars = computed(() => {
  const rows = [...financials.value].reverse()         // 後端由新到舊 → 反轉成由舊到新
  const vals = rows.map((r) => r.eps ?? 0)
  const max = Math.max(...vals, 0.01)                  // 避免除以 0
  return rows.map((r) => ({
    date: r.date.slice(0, 7),                          // 2026-06
    eps: r.eps,
    heightPct: Math.max(((r.eps ?? 0) / max) * 100, 2), // 最矮也給 2% 看得到
  }))
})

// 月營收 YoY 長條圖：由舊到新；高度用「絕對值 ÷ 最大絕對值」，正紅負綠
const revBars = computed(() => {
  const rows = [...revenues.value].reverse()           // 後端由新到舊 → 由舊到新
  const maxAbs = Math.max(...rows.map((r) => Math.abs(r.yoy ?? 0)), 0.01)
  return rows.map((r) => ({
    label: `${r.year}/${String(r.month).padStart(2, '0')}`,
    yoy: r.yoy,
    revenue: r.revenue,
    heightPct: Math.max((Math.abs(r.yoy ?? 0) / maxAbs) * 100, 2),
    up: (r.yoy ?? 0) >= 0,                              // 正成長=紅、衰退=綠（台股配色）
  }))
})

// 評價指標白話（滑鼠移上去看）
const valuationHint: Record<string, string> = {
  per: '本益比(PER)＝股價 ÷ 每股盈餘。代表你付的價格是它一年獲利的幾倍，數字越低相對越「便宜」。',
  pbr: '股價淨值比(PBR)＝股價 ÷ 每股淨值。股價是公司「家底」的幾倍，低於 1 代表股價比帳面價值還低。',
  dividend_yield: '殖利率(%)＝一年配息 ÷ 股價。把錢放這檔一年大約領幾 % 股息，存股族最在意這個。',
}

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
  // 評價指標獨立抓：抓不到（例如該檔沒資料）只是不顯示這張卡，不影響 K 線
  try {
    const rows = await getValuation(id, 1)
    valuation.value = rows[0] ?? null
  } catch {
    valuation.value = null
  }
  // EPS 同樣獨立抓、獨立容錯
  try {
    financials.value = await getFinancials(id, 8)
  } catch {
    financials.value = []
  }
  // 月營收同樣獨立抓、獨立容錯
  try {
    revenues.value = await getRevenue(id, 12)
  } catch {
    revenues.value = []
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

    <el-card class="val-card" v-if="valuation">
      <div class="val-head">
        <span class="val-title">基本面（{{ valuation.date }}）</span>
        <span class="val-sub">看「體質／貴不貴」，和左邊 K 線的「行情」互補</span>
      </div>
      <div class="val-grid">
        <el-tooltip :content="valuationHint.per" placement="bottom">
          <div class="val-item">
            <div class="val-label">本益比 PER</div>
            <div class="val-num">{{ valuation.per ?? '—' }}</div>
          </div>
        </el-tooltip>
        <el-tooltip :content="valuationHint.pbr" placement="bottom">
          <div class="val-item">
            <div class="val-label">股價淨值比 PBR</div>
            <div class="val-num">{{ valuation.pbr ?? '—' }}</div>
          </div>
        </el-tooltip>
        <el-tooltip :content="valuationHint.dividend_yield" placement="bottom">
          <div class="val-item">
            <div class="val-label">殖利率</div>
            <div class="val-num">{{ valuation.dividend_yield != null ? valuation.dividend_yield + '%' : '—' }}</div>
          </div>
        </el-tooltip>
      </div>

      <div class="eps-block" v-if="epsBars.length">
        <div class="eps-title">
          EPS 每股盈餘（近 {{ epsBars.length }} 季，單位：元）
          <span class="val-sub">每股幫你賺多少錢，長條越高越賺；看趨勢是成長還是衰退</span>
        </div>
        <div class="eps-bars">
          <el-tooltip
            v-for="b in epsBars" :key="b.date"
            :content="`${b.date}　EPS ${b.eps ?? '—'} 元`" placement="top"
          >
            <div class="eps-col">
              <div class="eps-bar-wrap">
                <div class="eps-bar" :style="{ height: b.heightPct + '%' }"></div>
              </div>
              <div class="eps-val">{{ b.eps ?? '—' }}</div>
              <div class="eps-date">{{ b.date.slice(5) }}</div>
            </div>
          </el-tooltip>
        </div>
      </div>

      <div class="eps-block" v-if="revBars.length">
        <div class="eps-title">
          月營收年增率 YoY（近 {{ revBars.length }} 月）
          <span class="val-sub">跟「去年同月」比成長幾 %，排除淡旺季看真實成長；<span class="up">紅</span>=成長、<span class="down">綠</span>=衰退</span>
        </div>
        <div class="eps-bars">
          <el-tooltip
            v-for="b in revBars" :key="b.label"
            :content="`${b.label}　YoY ${b.yoy ?? '—'}%　營收 ${(b.revenue / 1e8).toFixed(0)} 億`" placement="top"
          >
            <div class="eps-col">
              <div class="eps-bar-wrap">
                <div class="eps-bar" :class="b.up ? 'bar-up' : 'bar-down'" :style="{ height: b.heightPct + '%' }"></div>
              </div>
              <div class="eps-val" :class="b.up ? 'up' : 'down'">{{ b.yoy != null ? b.yoy + '%' : '—' }}</div>
              <div class="eps-date">{{ b.label.slice(5) }}</div>
            </div>
          </el-tooltip>
        </div>
      </div>
    </el-card>

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
.title { font-size: 18px; font-weight: 700; display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap; }
/* 手機版：縮小標題與基本面數字，避免 header 與卡片過擠 */
@media (max-width: 600px) {
  .title { font-size: 15px; gap: 4px; }
  .val-grid { gap: 8px; }
  .val-item { min-width: 90px; padding: 10px; }
  .val-num { font-size: 18px; }
}
.chart-card { margin-top: 8px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.label { font-weight: 600; }
.hint { color: #909399; font-size: 13px; }
.val-card { margin-bottom: 12px; }
.val-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.val-title { font-weight: 700; font-size: 15px; }
.val-sub { color: #909399; font-size: 12px; }
.val-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.val-item { flex: 1; min-width: 120px; background: #f7f8fa; border-radius: 8px; padding: 12px 14px; cursor: help; }
.val-label { color: #606266; font-size: 13px; margin-bottom: 4px; }
.val-num { font-size: 22px; font-weight: 700; color: #303133; }
.eps-block { margin-top: 16px; border-top: 1px dashed #e4e7ed; padding-top: 12px; }
.eps-title { font-weight: 600; font-size: 14px; margin-bottom: 10px; }
/* 長條列：寬螢幕平分撐滿；窄螢幕放不下就「在卡片內橫向捲動」，不撐爆整頁 */
.eps-bars { display: flex; align-items: flex-end; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.eps-col { flex: 1 0 38px; min-width: 38px; display: flex; flex-direction: column; align-items: center; cursor: help; }
.eps-bar-wrap { height: 80px; width: 100%; display: flex; align-items: flex-end; justify-content: center; }
.eps-bar { width: 60%; min-height: 2px; background: linear-gradient(to top, #e53935, #ff8a80); border-radius: 3px 3px 0 0; transition: height .3s; }
.eps-bar.bar-up { background: linear-gradient(to top, #e53935, #ff8a80); }
.eps-bar.bar-down { background: linear-gradient(to top, #43a047, #a5d6a7); }
.eps-val { font-size: 12px; font-weight: 600; color: #303133; margin-top: 4px; white-space: nowrap; }
.eps-date { font-size: 11px; color: #909399; white-space: nowrap; }
.help { margin-bottom: 12px; }
.help-list { margin: 0; padding-left: 18px; line-height: 1.9; color: #555; }
.up { color: #e53935; font-weight: 600; }
.down { color: #43a047; font-weight: 600; }
</style>
