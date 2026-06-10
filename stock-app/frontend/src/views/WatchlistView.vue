<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWatchlist, removeWatchlist, type WatchItem } from '../api'

const router = useRouter()
const items = ref<WatchItem[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    items.value = await getWatchlist()
  } finally {
    loading.value = false
  }
}

async function remove(item: WatchItem) {
  await ElMessageBox.confirm(`從自選股移除 ${item.stock_id} ${item.name || ''}？`, '確認', { type: 'warning' })
  await removeWatchlist(item.id)
  ElMessage.success('已移除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <el-card>
      <template #header><b>⭐ 我的自選股</b></template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="stock_id" label="代號" width="100" />
        <el-table-column prop="name" label="名稱" width="140" />
        <el-table-column prop="note" label="備註" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/stock/${row.stock_id}`)">看圖</el-button>
            <el-button size="small" type="danger" plain @click="remove(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && items.length === 0" description="還沒有自選股，到股票總覽加入吧" />
    </el-card>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }
</style>
