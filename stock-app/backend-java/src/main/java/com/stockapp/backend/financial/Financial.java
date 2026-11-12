package com.stockapp.backend.financial;

import java.math.BigDecimal;
import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 季度財報 EPS，對應 MySQL 的 financials 表。對照 Python models.Financial。
 */
@Entity
@Table(name = "financials")
public class Financial {

    @Id
    private Long id;

    @Column(name = "stock_id", length = 10)
    private String stockId;

    private LocalDate date;   // 季底日期
    private BigDecimal eps;   // 每股盈餘

    protected Financial() {
    }

    public LocalDate getDate() {
        return date;
    }

    public BigDecimal getEps() {
        return eps;
    }
}
