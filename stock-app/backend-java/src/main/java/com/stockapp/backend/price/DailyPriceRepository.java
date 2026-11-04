package com.stockapp.backend.price;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 日線資料存取，對應 Python 版 router 裡的 db.query(DailyPrice)...。
 */
public interface DailyPriceRepository extends JpaRepository<DailyPrice, Long> {

    /**
     * 取某檔全部日線，依日期由舊到新排序（指標計算需要時間順序）。
     * 對照 Python：
     *   db.query(DailyPrice).filter(DailyPrice.stock_id == id).order_by(DailyPrice.date.asc())
     *
     * 方法名派生查詢：findBy[欄位]OrderBy[欄位][Asc/Desc]，Spring Data 自動生 SQL。
     */
    List<DailyPrice> findByStockIdOrderByDateAsc(String stockId);
}
