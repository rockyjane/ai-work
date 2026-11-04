package com.stockapp.backend.price;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
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
 * K 線 + 技術指標 API，對應 Python 版 routers/stocks.py 的 get_prices。
 * 回傳格式刻意對齊 Python，直接給前端 ECharts 用。
 */
@RestController
@RequestMapping("/api")
public class PriceController {

    private final DailyPriceRepository repo;
    private final IndicatorService indicators;

    public PriceController(DailyPriceRepository repo, IndicatorService indicators) {
        this.repo = repo;
        this.indicators = indicators;
    }

    @GetMapping("/stocks/{stockId}/prices")
    public Map<String, Object> getPrices(
            @PathVariable String stockId,
            @RequestParam(defaultValue = "ma,rsi,macd,kd") String indicatorsParam,
            @RequestParam(defaultValue = "250") int limit) {

        List<DailyPrice> rows = repo.findByStockIdOrderByDateAsc(stockId);
        if (rows.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "這檔股票還沒有行情資料，請先執行 seed.py 匯入");
        }

        List<String> which = Arrays.stream(indicatorsParam.split(","))
                .map(String::trim).filter(s -> !s.isEmpty()).toList();

        // 指標用「完整資料」算好，再裁切最近 limit 筆（避免邊界失真），對齊 Python 做法
        Map<String, List<Double>> ind = indicators.compute(rows, which);

        int total = rows.size();
        int from = (limit > 0 && total > limit) ? total - limit : 0;

        List<String> dates = new ArrayList<>();
        List<double[]> kline = new ArrayList<>();   // ECharts 順序 [open, close, low, high]
        List<Long> volumes = new ArrayList<>();
        for (int i = from; i < total; i++) {
            DailyPrice r = rows.get(i);
            dates.add(r.getDate().toString());
            kline.add(new double[]{
                    r.getOpen().doubleValue(), r.getClose().doubleValue(),
                    r.getLow().doubleValue(), r.getHigh().doubleValue()
            });
            volumes.add(r.getVolume());
        }
        // 指標同步裁切成最近 limit 筆
        Map<String, List<Double>> indTrimmed = new LinkedHashMap<>();
        ind.forEach((k, v) -> indTrimmed.put(k, v.subList(from, v.size())));

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("stock_id", stockId);
        out.put("dates", dates);
        out.put("kline", kline);
        out.put("volumes", volumes);
        out.put("indicators", indTrimmed);
        return out;
    }
}
