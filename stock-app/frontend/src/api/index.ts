import axios from 'axios'

// baseURL = /api，會被 Vite proxy 轉到後端 http://127.0.0.1:8000
const api = axios.create({ baseURL: '/api' })

export interface Stock {
  stock_id: string
  name: string
  industry?: string
  market?: string
}

export interface PriceData {
  stock_id: string
  dates: string[]
  kline: number[][] // [open, close, low, high]
  volumes: number[]
  indicators: Record<string, (number | null)[]>
}

export interface WatchItem {
  id: number
  stock_id: string
  name?: string
  note?: string
}

export const getStocks = (q = '') =>
  api.get<Stock[]>('/stocks', { params: { q } }).then((r) => r.data)

export const getStock = (id: string) =>
  api.get<Stock>(`/stocks/${id}`).then((r) => r.data)

export const getPrices = (id: string, indicators = 'ma,rsi,macd,kd', limit = 250) =>
  api.get<PriceData>(`/stocks/${id}/prices`, { params: { indicators, limit } }).then((r) => r.data)

export const getRankings = (top = 10) =>
  api.get('/rankings', { params: { top } }).then((r) => r.data)

export const getWatchlist = () =>
  api.get<WatchItem[]>('/watchlist').then((r) => r.data)

export const addWatchlist = (stock_id: string, note = '') =>
  api.post('/watchlist', { stock_id, note }).then((r) => r.data)

export const removeWatchlist = (id: number) =>
  api.delete(`/watchlist/${id}`).then((r) => r.data)

export default api
