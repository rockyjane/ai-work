<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { PriceData } from '../api'

const props = defineProps<{
  data: PriceData
  sub: 'rsi' | 'macd' | 'kd'
}>()

const el = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const UP = '#e53935'   // 台股：紅漲
const DOWN = '#43a047' // 台股：綠跌

function buildOption(): echarts.EChartsOption {
  const d = props.data
  const ind = d.indicators || {}

  // 下方副圖（依選擇切換）
  const subSeries: any[] = []
  if (props.sub === 'rsi') {
    subSeries.push({ name: 'RSI14', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: ind.rsi14 || [], showSymbol: false, lineStyle: { width: 1 } })
  } else if (props.sub === 'macd') {
    subSeries.push(
      { name: 'MACD柱', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: ind.macd_diff || [],
        itemStyle: { color: (p: any) => (p.value >= 0 ? UP : DOWN) } },
      { name: 'DIF', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: ind.macd || [], showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MACD', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: ind.macd_signal || [], showSymbol: false, lineStyle: { width: 1 } },
    )
  } else {
    subSeries.push(
      { name: 'K', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: ind.k || [], showSymbol: false, lineStyle: { width: 1 } },
      { name: 'D', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: ind.d || [], showSymbol: false, lineStyle: { width: 1 } },
    )
  }

  return {
    animation: false,
    legend: { top: 0, data: ['K線', 'MA5', 'MA20', 'MA60'] },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: [
      { left: 50, right: 20, top: 40, height: '48%' },
      { left: 50, right: 20, top: '60%', height: '12%' },
      { left: 50, right: 20, top: '76%', height: '16%' },
    ],
    xAxis: [
      { type: 'category', data: d.dates, boundaryGap: true, axisLabel: { show: false } },
      { type: 'category', data: d.dates, gridIndex: 1, axisLabel: { show: false } },
      { type: 'category', data: d.dates, gridIndex: 2 },
    ],
    yAxis: [
      { scale: true, splitArea: { show: true } },
      { gridIndex: 1, name: '量', splitLine: { show: false } },
      { gridIndex: 2, name: props.sub.toUpperCase(), scale: true },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1, 2], start: 60, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1, 2], bottom: 0, start: 60, end: 100 },
    ],
    series: [
      {
        name: 'K線', type: 'candlestick', data: d.kline,
        itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN },
      },
      { name: 'MA5', type: 'line', data: ind.ma5 || [], showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MA20', type: 'line', data: ind.ma20 || [], showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MA60', type: 'line', data: ind.ma60 || [], showSymbol: false, lineStyle: { width: 1 } },
      {
        name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: d.volumes,
        itemStyle: {
          color: (p: any) => {
            const k = d.kline[p.dataIndex]
            return k && k[1] >= k[0] ? UP : DOWN // 收 >= 開 為紅
          },
        },
      },
      ...subSeries,
    ],
  }
}

function render() {
  if (!chart) return
  chart.setOption(buildOption(), true)
}

function onResize() {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  if (el.value) {
    chart = echarts.init(el.value)
    render()
    window.addEventListener('resize', onResize)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
})

watch(() => [props.data, props.sub], render, { deep: true })
</script>

<template>
  <div ref="el" class="kline"></div>
</template>

<style scoped>
.kline { width: 100%; height: 560px; }
</style>
