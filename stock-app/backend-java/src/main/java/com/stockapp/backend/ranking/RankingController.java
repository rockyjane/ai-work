package com.stockapp.backend.ranking;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.stockapp.backend.price.DailyPrice;
import com.stockapp.backend.price.DailyPriceRepository;
import com.stockapp.backend.stock.Stock;
import com.stockapp.backend.stock.StockRepository;

/**
 * 漲跌幅排行 API，對應 Python 的 rankings（已優化版：只遍歷有日線的股票）。
 */
@RestController
@RequestMapping("/api")
public class RankingController {

    private final DailyPriceRepository priceRepo;
    private final StockRepository stockRepo;

    public RankingController(DailyPriceRepository priceRepo, StockRepository stockRepo) {
        this.priceRepo = priceRepo;
        this.stockRepo = stockRepo;
    }

    @GetMapping("/rankings")
    public Map<String, Object> rankings(@RequestParam(defaultValue = "10") int top) {
        // 只看有日線的股票（約 50 檔），不掃全台 3088 檔（對應 Python 的效能優化）
        List<String> ids = priceRepo.findDistinctStockIds();

        List<RankItem> results = new ArrayList<>();
        for (String sid : ids) {
            // 取最近 2 個交易日
            List<DailyPrice> last2 = priceRepo.findByStockIdOrderByDateDesc(sid, PageRequest.of(0, 2));
            if (last2.size() < 2) continue;
            double cur = last2.get(0).getClose().doubleValue();
            double prev = last2.get(1).getClose().doubleValue();
            if (prev == 0) continue;
            double change = cur - prev;
            double pct = Math.round(change / prev * 100 * 100) / 100.0;
            String name = stockRepo.findById(sid).map(Stock::getName).orElse("");
            results.add(new RankItem(sid, name, cur, Math.round(change * 100) / 100.0, pct));
        }

        // 依漲跌幅由大到小排序
        results.sort(Comparator.comparingDouble(RankItem::pct).reversed());

        int n = results.size();
        List<RankItem> gainers = results.subList(0, Math.min(top, n));
        // 跌幅榜：取尾端 top 筆、再反轉成「跌最多在前」（對應 Python results[-top:][::-1]）
        List<RankItem> losersTail = results.subList(Math.max(0, n - top), n);
        List<RankItem> losers = new ArrayList<>(losersTail);
        java.util.Collections.reverse(losers);

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("gainers", new ArrayList<>(gainers));
        out.put("losers", losers);
        return out;
    }
}
