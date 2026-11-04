package com.stockapp.backend.price;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

/**
 * 技術指標計算（純 Java 手刻，對照 Python 版 indicators.py 的 pandas 寫法）。
 *
 * ── Python vs Java 的核心差異 ──
 * Python 用 pandas 向量化：close.rolling(5).mean() 一行算完整條 MA5。
 * Java 沒 pandas，要用「迴圈逐筆算」。概念一樣、只是手動展開。
 * 算不出值的位置（資料不足）回 null，和 Python 的 NaN→None 對齊。
 *
 * 指標白話見 Python 版 indicators.py 開頭；這裡專注「怎麼算」。
 */
@Service
public class IndicatorService {

    /** 依 which（如 ["ma","rsi","macd","kd"]）算出各指標，回傳給 ECharts 用的 list。 */
    public Map<String, List<Double>> compute(List<DailyPrice> rows, List<String> which) {
        int n = rows.size();
        double[] close = new double[n];
        double[] high = new double[n];
        double[] low = new double[n];
        for (int i = 0; i < n; i++) {
            close[i] = rows.get(i).getClose().doubleValue();
            high[i] = rows.get(i).getHigh().doubleValue();
            low[i] = rows.get(i).getLow().doubleValue();
        }

        Map<String, List<Double>> out = new LinkedHashMap<>();

        if (which.contains("ma")) {
            out.put("ma5", sma(close, 5));
            out.put("ma20", sma(close, 20));
            out.put("ma60", sma(close, 60));
        }
        if (which.contains("rsi")) {
            out.put("rsi14", rsi(close, 14));
        }
        if (which.contains("macd")) {
            double[] ema12 = ema(close, 12);
            double[] ema26 = ema(close, 26);
            double[] dif = sub(ema12, ema26);              // 快線
            double[] dea = emaOf(dif, 9);                  // 慢線/訊號線（對 dif 再做 EMA9）
            out.put("macd", round(dif, 3));
            out.put("macd_signal", round(dea, 3));
            out.put("macd_diff", round(sub(dif, dea), 3)); // 柱狀體（動能）
        }
        if (which.contains("kd")) {
            double[][] kd = kd(close, high, low);
            out.put("k", round(kd[0], 2));
            out.put("d", round(kd[1], 2));
        }
        return out;
    }

    // ── MA：簡單移動平均，對應 close.rolling(period).mean() ──
    private List<Double> sma(double[] v, int period) {
        List<Double> r = new ArrayList<>(v.length);
        double sum = 0;
        for (int i = 0; i < v.length; i++) {
            sum += v[i];
            if (i >= period) sum -= v[i - period];         // 滑動視窗：減掉離開視窗的那筆
            r.add(i >= period - 1 ? round2(sum / period) : null);  // 不足 period 筆回 null（對應 NaN）
        }
        return r;
    }

    // ── EMA：指數移動平均，對應 pandas 的 ewm(span=N, adjust=False) ──
    // 公式：alpha = 2/(span+1)；ema[i] = alpha*v[i] + (1-alpha)*ema[i-1]；種子用第一筆值
    private double[] ema(double[] v, int span) {
        double alpha = 2.0 / (span + 1);
        return ewm(v, alpha);
    }

    private double[] emaOf(double[] v, int span) {
        return ema(v, span);
    }

    private double[] ewm(double[] v, double alpha) {
        double[] r = new double[v.length];
        if (v.length == 0) return r;
        r[0] = v[0];
        for (int i = 1; i < v.length; i++) {
            r[i] = alpha * v[i] + (1 - alpha) * r[i - 1];
        }
        return r;
    }

    // ── RSI：對應 Wilder 平滑（alpha=1/period 的 EMA），不足 period 回 null ──
    private List<Double> rsi(double[] close, int period) {
        int n = close.length;
        List<Double> r = new ArrayList<>(n);
        if (n == 0) return r;
        double[] gain = new double[n];
        double[] loss = new double[n];
        for (int i = 1; i < n; i++) {
            double delta = close[i] - close[i - 1];
            gain[i] = Math.max(delta, 0);
            loss[i] = Math.max(-delta, 0);
        }
        double alpha = 1.0 / period;
        double avgGain = 0, avgLoss = 0;
        for (int i = 0; i < n; i++) {
            if (i == 0) {
                r.add(null);
                continue;
            }
            // Wilder 平滑（adjust=False 的遞迴式）
            avgGain = alpha * gain[i] + (1 - alpha) * avgGain;
            avgLoss = alpha * loss[i] + (1 - alpha) * avgLoss;
            if (i < period) {                 // 前 period 筆不夠穩定，對齊 Python 的 min_periods=period
                r.add(null);
            } else {
                double rs = avgLoss == 0 ? Double.POSITIVE_INFINITY : avgGain / avgLoss;
                double val = 100 - 100 / (1 + rs);
                r.add(round2(val));
            }
        }
        return r;
    }

    // ── KD：台股慣用 9,3,3 ──
    private double[][] kd(double[] close, double[] high, double[] low) {
        int n = close.length;
        double[] rsv = new double[n];
        for (int i = 0; i < n; i++) {
            if (i < 8) {                      // 不足 9 天：區間無意義，給中性 50（對應 Python fillna(50)）
                rsv[i] = 50;
                continue;
            }
            double hi = Double.NEGATIVE_INFINITY, lo = Double.POSITIVE_INFINITY;
            for (int j = i - 8; j <= i; j++) { // 最近 9 天高低
                hi = Math.max(hi, high[j]);
                lo = Math.min(lo, low[j]);
            }
            rsv[i] = (hi - lo) == 0 ? 50 : (close[i] - lo) / (hi - lo) * 100;
        }
        double[] k = ewm(rsv, 1.0 / 3);        // K = RSV 的 EMA(1/3)
        double[] d = ewm(k, 1.0 / 3);          // D = K 的 EMA(1/3)
        return new double[][]{k, d};
    }

    // ── 小工具 ──
    private double[] sub(double[] a, double[] b) {
        double[] r = new double[a.length];
        for (int i = 0; i < a.length; i++) r[i] = a[i] - b[i];
        return r;
    }

    private List<Double> round(double[] v, int digits) {
        double f = Math.pow(10, digits);
        List<Double> r = new ArrayList<>(v.length);
        for (double x : v) r.add(Math.round(x * f) / f);
        return r;
    }

    private Double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }
}
