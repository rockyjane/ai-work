package com.stockapp.backend.financial;

/** EPS 財報回傳格式，對應 Python schemas.FinancialOut。 */
public record FinancialDto(String date, Double eps) {
}
