"""技術指標計算（純 pandas/numpy 手算，不依賴第三方指標庫）。

自己算的好處：① 沒有第三方相依衝突 ② 看得懂每個指標怎麼算出來，學股票更扎實。

────────────── 白話版：這些指標在看什麼？（給零基礎看的）──────────────

先講最基本的「K 棒」：一根 K 棒 = 某一天的股價故事，記了那天的
開盤價、收盤價、最高、最低。台股習慣：收盤比開盤高(上漲)畫紅色、下跌畫綠色。

  • MA 移動平均線
      把「最近 N 天的收盤價」平均，連成一條線，用來看「最近是往上還是往下」。
      MA5 = 最近 5 天平均（反應快，像你「這一週」的心情）
      MA60 = 最近 60 天平均（反應慢，像你「這一季」的整體狀態）
      當短期線(MA5)由下往上穿過長期線(MA60) → 最近買氣明顯變強，偏「看漲」訊號。

  • RSI 相對強弱
      一支 0~100 的「溫度計」，量最近是漲多還是跌多。
      >70 = 漲太多、過熱了，可能要休息回檔；<30 = 跌太多、過冷，可能要反彈。

  • MACD
      比較「短期均線」和「長期均線」拉開的距離，看上漲(或下跌)的「力道」在
      變強還是變弱。下方柱狀體由負轉正 → 下跌力道在消、上漲力道在增。

  • KD（台股最常被提到的指標）
      看「今天收盤價」站在「最近 9 天的高低範圍」的哪個位置：
      位置高(接近 80) = 強勢偏熱；位置低(接近 20) = 弱勢偏冷。
      K 線由下往上穿過 D 線 → 短期轉強，常被當買進參考。
─────────────────────────────────────────────────────────────
"""
import numpy as np
import pandas as pd


def _clean(series: pd.Series, ndigits: int = 2):
    """把 pandas Series 轉成可 JSON 化的 list，NaN/Inf 轉成 None。"""
    return [None if (pd.isna(x) or np.isinf(x)) else round(float(x), ndigits) for x in series]


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder 平滑（等同 alpha = 1/period 的 EMA）
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def compute_indicators(df: pd.DataFrame, which: list[str]) -> dict:
    """df 需含欄位 open/high/low/close/volume，依日期由舊到新排序。
    which 例如 ['ma', 'rsi', 'macd', 'kd']。
    """
    out: dict = {}
    close, high, low = df["close"], df["high"], df["low"]

    if "ma" in which:
        out["ma5"] = _clean(close.rolling(5).mean())
        out["ma20"] = _clean(close.rolling(20).mean())
        out["ma60"] = _clean(close.rolling(60).mean())

    if "rsi" in which:
        out["rsi14"] = _clean(_rsi(close, 14))

    if "macd" in which:
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        dif = ema12 - ema26                                  # 快線
        dea = dif.ewm(span=9, adjust=False).mean()           # 慢線 / 訊號線
        out["macd"] = _clean(dif, 3)
        out["macd_signal"] = _clean(dea, 3)
        out["macd_diff"] = _clean(dif - dea, 3)              # 柱狀體（動能）

    if "kd" in which:
        low9 = low.rolling(9).min()
        high9 = high.rolling(9).max()
        rsv = (close - low9) / (high9 - low9) * 100
        rsv = rsv.fillna(50)                                  # 區間無波動時給中性值
        k = rsv.ewm(alpha=1 / 3, adjust=False).mean()         # 台股慣用 9,3,3
        d = k.ewm(alpha=1 / 3, adjust=False).mean()
        out["k"] = _clean(k)
        out["d"] = _clean(d)

    return out
