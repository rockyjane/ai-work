package com.stockapp.backend.stock;

import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 股票 REST API，對應 Python 版的 routers/stocks.py。
 *
 * 對照：
 *   @RestController + @RequestMapping("/api")  ≈  FastAPI 的 APIRouter(prefix 由 main 掛)
 *   @GetMapping("/stocks")                      ≈  @router.get("/stocks")
 *   @RequestParam(defaultValue="") String q     ≈  def list_stocks(q: str = "")
 */
@RestController
@RequestMapping("/api")
public class StockController {

    private final StockRepository repo;

    // 建構子注入：Spring 啟動時自動把 StockRepository 的實作塞進來
    // （對應 FastAPI 的 Depends(get_db) 依賴注入，概念相通）
    public StockController(StockRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/stocks")
    public List<Stock> listStocks(@RequestParam(defaultValue = "") String q) {
        // PageRequest.of(0, 50) = 第 0 頁、每頁 50 筆，等同 Python 的 .limit(50)
        return repo.search(q, PageRequest.of(0, 50));
    }
}
