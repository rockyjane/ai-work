package com.stockapp.backend.watchlist;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * 自選股，對應 MySQL 的 watchlist 表。對照 Python models.Watchlist。
 *
 * 和前面「只讀」的表不同：這張要「寫入」（新增/刪除），所以 id 用
 * @GeneratedValue(IDENTITY) 讓 MySQL 自動遞增產生（對應 autoincrement）。
 */
@Entity
@Table(name = "watchlist")
public class Watchlist {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // 交給 DB 自增；只讀表不需要、寫入表才要
    private Long id;

    @Column(name = "stock_id", length = 10)
    private String stockId;

    private String note;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;   // 由 DB 的 server_default=now() 產生，Java 不寫

    protected Watchlist() {
    }

    public Watchlist(String stockId, String note) {
        this.stockId = stockId;
        this.note = note;
    }

    public Long getId() {
        return id;
    }

    public String getStockId() {
        return stockId;
    }

    public String getNote() {
        return note;
    }
}
