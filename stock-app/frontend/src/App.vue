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
  border-bottom: 1px solid #eee;
  background: #fff;
}
.brand { font-size: 20px; font-weight: 700; }
.nav { border-bottom: none !important; }
</style>
