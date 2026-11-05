package com.stockapp.backend.financial;

/**
 * 月營收回傳格式，對應 Python schemas.RevenueOut。
 * yoy/mom 是即時算出的衍生值（可能為 null）。
 */
public record RevenueDto(
        int year,
        int month,
        long revenue,
        Double yoy,
        Double mom) {
}
