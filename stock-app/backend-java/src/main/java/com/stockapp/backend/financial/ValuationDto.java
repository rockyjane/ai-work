package com.stockapp.backend.financial;

/**
 * 評價指標 API 回傳格式，對應 Python 的 schemas.ValuationOut。
 *
 * 用 Java record：一行定義不可變資料類（自動有建構子/getter/equals）。
 * 欄位名 dividendYield 靠全域 SNAKE_CASE 設定輸出成 dividend_yield，對齊 Python。
 */
public record ValuationDto(
        String date,
        Double per,
        Double pbr,
        Double dividendYield) {
}
