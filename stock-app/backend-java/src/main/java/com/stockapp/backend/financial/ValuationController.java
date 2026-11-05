package com.stockapp.backend.financial;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * 評價指標 API，對應 Python 的 get_valuation。
 */
@RestController
@RequestMapping("/api")
public class ValuationController {

    private final ValuationRepository repo;

    public ValuationController(ValuationRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/stocks/{stockId}/valuation")
    public List<ValuationDto> getValuation(
            @PathVariable String stockId,
            @RequestParam(defaultValue = "60") int limit) {

        List<Valuation> rows = repo.findByStockIdOrderByDateDesc(stockId, PageRequest.of(0, limit));
        if (rows.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "這檔股票還沒有評價資料，請先執行 seed.py 匯入");
        }
        return rows.stream().map(r -> new ValuationDto(
                r.getDate().toString(),
                d(r.getPer()), d(r.getPbr()), d(r.getDividendYield())
        )).toList();
    }

    // BigDecimal → Double（null 保持 null，對應 Python 的 Optional[float]）
    private static Double d(BigDecimal v) {
        return v == null ? null : v.doubleValue();
    }
}
