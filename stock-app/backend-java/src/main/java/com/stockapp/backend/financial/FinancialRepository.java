package com.stockapp.backend.financial;

import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 季度財報存取，對應 Python 的 db.query(Financial)...order_by(date.desc()).limit(n)。
 */
public interface FinancialRepository extends JpaRepository<Financial, Long> {

    List<Financial> findByStockIdOrderByDateDesc(String stockId, Pageable pageable);
}
