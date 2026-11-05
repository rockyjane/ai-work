package com.stockapp.backend.financial;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 每月營收，對應 MySQL 的 revenues 表。對照 Python models.Revenue。
 * 只存原始營收；YoY/MoM 在 Controller 即時算（對齊 Python）。
 */
@Entity
@Table(name = "revenues")
public class Revenue {

    @Id
    private Long id;

    @Column(name = "stock_id", length = 10)
    private String stockId;

    private Integer year;
    private Integer month;
    private Long revenue;     // 當月營收（元）

    protected Revenue() {
    }

    public Integer getYear() {
        return year;
    }

    public Integer getMonth() {
        return month;
    }

    public Long getRevenue() {
        return revenue;
    }
}
