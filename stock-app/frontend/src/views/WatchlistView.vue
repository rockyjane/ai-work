<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCloseFilled } from '@element-plus/icons-vue'
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
      <el-table :data="items" v-loading="loading" stripe class="watch-table" style="cursor: pointer"
        @row-click="(r:any)=>router.push(`/stock/${r.stock_id}`)">
        <el-table-column width="46" align="center">
          <template #default="{ row }">
            <el-icon class="del-btn" title="移除自選股" @click.stop="remove(row)"><CircleCloseFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="stock_id" label="代號" width="100" />
        <el-table-column prop="name" label="名稱" min-width="140" />
        <el-table-column prop="note" label="備註" min-width="120" />
      </el-table>
      <el-empty v-if="!loading && items.length === 0" description="還沒有自選股，到股票總覽加入吧" />
    </el-card>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }
/* 移除用紅叉 icon，放每列最前 */
.del-btn { color: #f56c6c; font-size: 22px; cursor: pointer; vertical-align: middle; }
.del-btn:hover { color: #dd4c4c; }
/* 行高再寬些，較好點按 */
.watch-table :deep(.el-table__cell) { padding: 12px 0; }
</style>
