package com.stockapp.backend.watchlist;

/**
 * 自選股相關 DTO（放一起，兩個小 record）。
 */
public class WatchlistDtos {

    /** POST 進來的 request body，對應 Python schemas.WatchlistCreate。note 可省略。 */
    public record CreateReq(String stockId, String note) {
    }

    /** GET 列表回傳的每筆，對應 Python list_watchlist 的 dict（含股票名稱）。 */
    public record WatchItem(Long id, String stockId, String name, String note) {
    }
}
