package com.stockapp.backend.financial;

import java.math.BigDecimal;
import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 每日評價指標（PER/PBR/殖利率），對應 MySQL 的 valuations 表。
 * 對照 Python models.Valuation。
 */
@Entity
@Table(name = "valuations")
public class Valuation {

    @Id
    private Long id;

    @Column(name = "stock_id", length = 10)
    private String stockId;

    private LocalDate date;
    private BigDecimal per;              // 本益比
    private BigDecimal pbr;              // 股價淨值比
    @Column(name = "dividend_yield")
    private BigDecimal dividendYield;    // 殖利率(%)

    protected Valuation() {
    }

    public LocalDate getDate() {
        return date;
    }

    public BigDecimal getPer() {
        return per;
    }

    public BigDecimal getPbr() {
        return pbr;
    }

    public BigDecimal getDividendYield() {
        return dividendYield;
    }
}
