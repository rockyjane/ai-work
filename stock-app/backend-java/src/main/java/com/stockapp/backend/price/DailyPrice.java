package com.stockapp.backend.price;

import java.math.BigDecimal;
import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 每日 K 線（日線），對應 MySQL 的 daily_prices 表（Python 版建好、灌好）。
 *
 * 對照 Python（SQLAlchemy）：
 *   class DailyPrice(Base):
 *       __tablename__ = "daily_prices"
 *       id, stock_id, date, open, high, low, close, volume
 *
 * 注意：價格用 BigDecimal（對應 Numeric），不用 double——金融數字忌浮點誤差。
 */
@Entity
@Table(name = "daily_prices")
public class DailyPrice {

    @Id
    private Long id;

    @Column(name = "stock_id", length = 10)
    private String stockId;

    private LocalDate date;
    private BigDecimal open;
    private BigDecimal high;
    private BigDecimal low;
    private BigDecimal close;
    private Long volume;

    protected DailyPrice() {
    }

    public Long getId() {
        return id;
    }

    public String getStockId() {
        return stockId;
    }

    public LocalDate getDate() {
        return date;
    }

    public BigDecimal getOpen() {
        return open;
    }

    public BigDecimal getHigh() {
        return high;
    }

    public BigDecimal getLow() {
        return low;
    }

    public BigDecimal getClose() {
        return close;
    }

    public Long getVolume() {
        return volume;
    }
}
