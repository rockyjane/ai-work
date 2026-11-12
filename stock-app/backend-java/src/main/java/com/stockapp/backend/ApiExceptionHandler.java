package com.stockapp.backend;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

/**
 * 全域錯誤處理：把錯誤回傳格式對齊 Python FastAPI 的 {"detail": "..."}。
 *
 * ── 為什麼需要 ──
 * Spring Boot 預設錯誤回 {"status":404,"error":"Not Found","message":...}，沒有 detail 欄位；
 * 而前端讀的是 e.response.data.detail（FastAPI 格式）。兩後端要「同契約」，連錯誤格式都該一致，
 * 否則前端拿不到訊息、只能顯示「讀取失敗」。
 *
 * @RestControllerAdvice：全域攔截所有 Controller 丟出的例外，統一處理。
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<Map<String, String>> handle(ResponseStatusException ex) {
        String detail = ex.getReason() != null ? ex.getReason() : "錯誤";
        return ResponseEntity.status(ex.getStatusCode()).body(Map.of("detail", detail));
    }
}
