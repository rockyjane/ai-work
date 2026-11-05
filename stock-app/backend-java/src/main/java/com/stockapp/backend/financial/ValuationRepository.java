package com.stockapp.backend.financial;

import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 評價指標存取，對應 Python 的 db.query(Valuation).filter(...).order_by(date.desc()).limit(n)。
 */
public interface ValuationRepository extends JpaRepository<Valuation, Long> {

    // 某檔、由新到舊、取前 N 筆（N 用 Pageable 控制，對應 .limit）
    List<Valuation> findByStockIdOrderByDateDesc(String stockId, Pageable pageable);
}
