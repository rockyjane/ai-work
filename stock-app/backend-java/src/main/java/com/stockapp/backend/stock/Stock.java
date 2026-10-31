package com.stockapp.backend.stock;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 股票基本資料，對應 MySQL 的 stocks 表（由 Python 版建好、灌好）。
 *
 * 對照 Python 版（SQLAlchemy）：
 *   class Stock(Base):
 *       __tablename__ = "stocks"
 *       stock_id = Column(String(10), primary_key=True)
 *       name = Column(String(50)) ...
 */
@Entity
@Table(name = "stocks")
public class Stock {

    @Id
    @Column(name = "stock_id", length = 10)
    private String stockId;      // JSON 會輸出成 stock_id（見 application.properties 的 SNAKE_CASE）

    private String name;
    private String industry;
    private String market;

    // JPA 需要一個無參數建構子
    protected Stock() {
    }

    // --- getters（Jackson 靠 getter 序列化成 JSON；Java 慣例用欄位，JSON 轉 snake_case）---
    public String getStockId() {
        return stockId;
    }

    public String getName() {
        return name;
    }

    public String getIndustry() {
        return industry;
    }

    public String getMarket() {
        return market;
    }
}
