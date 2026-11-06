package com.stockapp.backend.watchlist;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 自選股存取。JpaRepository 已內建 save（新增）、deleteById、existsById…
 * 這裡只補兩個自訂查詢。
 */
public interface WatchlistRepository extends JpaRepository<Watchlist, Long> {

    // 由新到舊列出（對應 Python 的 order_by(created_at.desc())）
    List<Watchlist> findAllByOrderByCreatedAtDesc();

    // POST 前檢查是否已加過（對應 Python 的 filter(stock_id==).first()）
    boolean existsByStockId(String stockId);
}
