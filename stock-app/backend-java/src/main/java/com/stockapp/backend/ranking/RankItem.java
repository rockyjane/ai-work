package com.stockapp.backend.ranking;

/**
 * 排行榜單一項目，對應 Python rankings 回傳的每筆 dict。
 * stockId→stock_id 靠全域 SNAKE_CASE 設定輸出。
 */
public record RankItem(
        String stockId,
        String name,
        double close,
        double change,
        double pct) {
}
