package com.stockapp.backend.financial;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * 月營收 API，對應 Python 的 get_revenue：即時計算 YoY（年增率）/ MoM（月增率）。
 *
 * ── 對照 Python ──
 * Python 用 dict：rev_map = {(year, month): revenue}；查「去年同月」「上個月」。
 * Java 用 Map<String, Long>，key 以 "year-month" 字串組合（等同 Python 的 tuple key）。
 */
@RestController
@RequestMapping("/api")
public class RevenueController {

    private final RevenueRepository repo;

    public RevenueController(RevenueRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/stocks/{stockId}/revenue")
    public List<RevenueDto> getRevenue(
            @PathVariable String stockId,
            @RequestParam(defaultValue = "12") int limit) {

        List<Revenue> rows = repo.findByStockIdOrderByYearAscMonthAsc(stockId);  // 由舊到新
        if (rows.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "這檔股票還沒有營收資料，請先執行 seed.py 匯入");
        }

        // 查表：(年,月) -> 營收，方便找「去年同月」「上個月」
        Map<String, Long> revMap = new HashMap<>();
        for (Revenue r : rows) {
            revMap.put(key(r.getYear(), r.getMonth()), r.getRevenue());
        }

        List<RevenueDto> out = new ArrayList<>();
        for (Revenue r : rows) {
            int y = r.getYear(), m = r.getMonth();
            Double yoy = pct(r.getRevenue(), revMap.get(key(y - 1, m)));          // 去年同月
            // 上個月：1 月的上月是「去年 12 月」（跨年特判，對齊 Python）
            String prevKey = m > 1 ? key(y, m - 1) : key(y - 1, 12);
            Double mom = pct(r.getRevenue(), revMap.get(prevKey));
            out.add(new RevenueDto(y, m, r.getRevenue(), yoy, mom));
        }

        // 由新到舊，取最近 limit 筆（對應 Python 的 out.reverse()[:limit]）
        Collections.reverse(out);
        return out.size() > limit ? out.subList(0, limit) : out;
    }

    private static String key(int year, int month) {
        return year + "-" + month;
    }

    // 成長率 = (本期 - 基準) / 基準 * 100；基準為 null 或 0 回 null（避免除以 0）
    private static Double pct(long cur, Long base) {
        if (base == null || base == 0) return null;
        return Math.round((cur - base) / (double) base * 100 * 100) / 100.0;
    }
}
