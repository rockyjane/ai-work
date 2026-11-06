package com.stockapp.backend.watchlist;

import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.stockapp.backend.stock.Stock;
import com.stockapp.backend.stock.StockRepository;
import com.stockapp.backend.watchlist.WatchlistDtos.CreateReq;
import com.stockapp.backend.watchlist.WatchlistDtos.WatchItem;

/**
 * 自選股 CRUD API，對應 Python 的 routers/watchlist.py。
 * 這是唯一「有寫入」的 API：POST 新增、DELETE 刪除。
 */
@RestController
@RequestMapping("/api")
public class WatchlistController {

    private final WatchlistRepository repo;
    private final StockRepository stockRepo;

    public WatchlistController(WatchlistRepository repo, StockRepository stockRepo) {
        this.repo = repo;
        this.stockRepo = stockRepo;
    }

    // 查詢：由新到舊，補上股票名稱
    @GetMapping("/watchlist")
    public List<WatchItem> list() {
        return repo.findAllByOrderByCreatedAtDesc().stream().map(w -> {
            String name = stockRepo.findById(w.getStockId()).map(Stock::getName).orElse(null);
            return new WatchItem(w.getId(), w.getStockId(), name, w.getNote());
        }).toList();
    }

    // 新增：已存在回 400（對應 Python 的 HTTPException 400）
    @PostMapping("/watchlist")
    public Map<String, Object> add(@RequestBody CreateReq body) {
        if (repo.existsByStockId(body.stockId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "已在自選股中");
        }
        Watchlist w = repo.save(new Watchlist(body.stockId(), body.note() == null ? "" : body.note()));
        return Map.of("id", w.getId(), "stock_id", w.getStockId(), "note", w.getNote());
    }

    // 刪除：找不到回 404
    @DeleteMapping("/watchlist/{itemId}")
    public Map<String, Object> remove(@PathVariable Long itemId) {
        if (!repo.existsById(itemId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "找不到此自選股");
        }
        repo.deleteById(itemId);
        return Map.of("ok", true);
    }
}
