package com.stockapp.backend.financial;

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
 * 季度財報 EPS API，對應 Python 的 get_financials（預設近 12 季）。
 */
@RestController
@RequestMapping("/api")
public class FinancialController {

    private final FinancialRepository repo;

    public FinancialController(FinancialRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/stocks/{stockId}/financials")
    public List<FinancialDto> getFinancials(
            @PathVariable String stockId,
            @RequestParam(defaultValue = "12") int limit) {

        List<Financial> rows = repo.findByStockIdOrderByDateDesc(stockId, PageRequest.of(0, limit));
        if (rows.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "這檔股票還沒有財報資料，請先執行 seed.py 匯入");
        }
        return rows.stream().map(r -> new FinancialDto(
                r.getDate().toString(),
                r.getEps() == null ? null : r.getEps().doubleValue()
        )).toList();
    }
}
