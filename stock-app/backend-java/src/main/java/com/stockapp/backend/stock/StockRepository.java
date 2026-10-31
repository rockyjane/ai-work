package com.stockapp.backend.stock;

import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

/**
 * 股票資料存取層，對應 Python 版在 router 裡寫的 db.query(Stock)...。
 *
 * 繼承 JpaRepository<Stock, String> 後，Spring Data 自動幫你生出
 * findAll / findById / save / count 等一堆方法，不用自己寫 SQL
 * ——這就像 SQLAlchemy 的 session.query，只是更「自動」。
 */
public interface StockRepository extends JpaRepository<Stock, String> {

    /**
     * 搜尋：代號或名稱包含 q。q 傳空字串時 LIKE %% 會匹配全部。
     * 搭配 Pageable 限制回傳筆數（對應 Python 版的 .limit(50)）。
     *
     * 對照 Python：
     *   query.filter(or_(Stock.stock_id.contains(q), Stock.name.contains(q))).limit(50)
     */
    @Query("SELECT s FROM Stock s WHERE s.stockId LIKE %:q% OR s.name LIKE %:q%")
    List<Stock> search(@Param("q") String q, Pageable pageable);
}
