import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'stocks', component: () => import('../views/StockListView.vue') },
    { path: '/stock/:id', name: 'detail', component: () => import('../views/StockDetailView.vue') },
    { path: '/watchlist', name: 'watchlist', component: () => import('../views/WatchlistView.vue') },
  ],
})

export default router
