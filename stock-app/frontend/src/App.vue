<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const activeIndex = computed(() => {
  if (route.path.startsWith('/watchlist')) return '/watchlist'
  return '/'
})
</script>

<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand">📈 台股分析</div>
      <el-menu :default-active="activeIndex" mode="horizontal" router :ellipsis="false" class="nav">
        <el-menu-item index="/">股票總覽</el-menu-item>
        <el-menu-item index="/watchlist">我的自選股</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
body { margin: 0; }
.layout { min-height: 100vh; }
.header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 16px;
  border-bottom: 1px solid #eee;
  background: #fff;
}
.brand { font-size: 20px; font-weight: 700; white-space: nowrap; }
.nav { border-bottom: none !important; }
/* 手機版：縮小標題與間距，避免「台股分析」被擠到換行 */
@media (max-width: 600px) {
  .header { gap: 10px; padding: 0 8px; }
  .brand { font-size: 15px; }
}
</style>
