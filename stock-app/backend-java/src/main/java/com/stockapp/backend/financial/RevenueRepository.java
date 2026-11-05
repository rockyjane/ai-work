package com.stockapp.backend.financial;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 月營收存取。取某檔全部、由舊到新（算 YoY/MoM 需要完整時序），
 * 對照 Python 的 order_by(year.asc(), month.asc())。
 */
public interface RevenueRepository extends JpaRepository<Revenue, Long> {

    List<Revenue> findByStockIdOrderByYearAscMonthAsc(String stockId);
}
