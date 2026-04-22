# STG3 Strategy — README

## 📌 Overview

STG3 is a **range breakout trading strategy** designed for both:

* **CSV backtesting (virtual mode)**
* **Live market paper trading (Kite Connect)**

The strategy:

1. Builds an initial price range
2. Waits for breakout
3. Enters trade (CE / PE logic)
4. Tracks **PnL, RR, R1/R2/S1/S2 levels**
5. Logs results for analysis

---

## ⚙️ Features

* ✅ Dual mode support (CSV + LIVE)
* ✅ Automatic range detection (High / Low)
* ✅ Breakout-based entry logic
* ✅ Risk-based levels:

  * R1, R2 (targets)
  * S1, S2 (support / SL zones)
* ✅ Real-time PnL tracking
* ✅ RR (Risk-Reward) calculation
* ✅ Excel/CSV logging (minute-wise)
* ✅ Clean terminal output (horizontal format)

---

## 🧠 Strategy Logic

### 1. Range Building

* Collects price data for a defined time (`initial_wait_time`)
* Calculates:

  * **HIGH = max price**
  * **LOW = min price**

---

### 2. Breakout Detection

| Condition    | Action    |
| ------------ | --------- |
| Price > HIGH | CE (Buy)  |
| Price < LOW  | PE (Sell) |

---

### 3. Entry & Risk

* Entry = breakout price

* Stoploss (SL):

  * CE → LOW
  * PE → HIGH

* Risk:

```text
risk = |entry - SL|
```

---

### 4. Target Levels

#### CE Trade

```text
R1 = entry + risk
R2 = entry + 2 × risk
S1 = entry - risk
S2 = entry - 2 × risk
```

#### PE Trade

```text
R1 = entry - risk
R2 = entry - 2 × risk
S1 = entry + risk
S2 = entry + 2 × risk
```

---

### 5. Exit Conditions

* 🎯 Target hit → `RR >= hard_rr_exit`
* ❌ Stoploss hit
* ⏱️ Loop termination (CSV end / manual stop)

---

## 🧾 Configuration (stg3.cfg)

```ini
[GENERAL]
mode = csv        # csv / live
symbol = NIFTY 50
qty = 50

[DATA]
csv_file = data.csv

[STRATEGY]
initial_wait_time = 60
max_range = 50
breakout_type = dynamic
rr_activate = 2
hard_rr_exit = 2

[LOGGING]
enable_minute_log = true
enable_summary_log = true
```

---

## ▶️ How to Run

### 🔹 Virtual Mode (Backtest)

```ini
mode = csv
```

```bash
python stg3.py
```

✔ Uses historical CSV
✔ No real market connection

---

### 🔹 Live Mode (Paper Trading)

```ini
mode = live
```

```bash
python stg3.py
```

✔ Uses Kite Connect API
✔ Real-time prices
❌ No real orders placed

---

## 📊 Terminal Output

Example:

```text
10:25 | M:2 | E:410 | P:413 | R1:430 | R2:450 | S1:390 | S2:370 | PnL:600 | RR:0.3
```

Where:

* `M` → Mode (1 = waiting, 2 = trade)
* `E` → Entry
* `P` → Current Price
* `PnL` → Profit/Loss
* `RR` → Risk-Reward

---

## 📁 Output Files

* `stg3_log.csv` → minute-wise trade logs
* Can be converted to Excel

---

## ⚠️ Important Notes

* LIVE mode = **paper trading only**
* No real trades are placed unless explicitly added
* Ensure correct symbol format:

  * `NIFTY 50` (not just NIFTY)

---

## 🧪 Testing Tips

* Reduce wait time:

```ini
initial_wait_time = 2
```

* Faster loop testing:

```python
time.sleep(2)
```

* Use controlled CSV for predictable breakout

---

## 🚀 Future Improvements

* CE/PE option tracking (like STG2)
* Auto expiry selection
* Partial booking at R1
* Trailing SL after R1
* GUI dashboard
* Alerts (sound / popup)

---

## 💯 Summary

STG3 is a **clean breakout + RR-based system** that:

* Works in both backtest and live modes
* Provides clear entry, risk, and targets
* Helps validate trading logic safely before real execution

---

**Status:** ✅ Fully functional
**Modes:** CSV + LIVE
**Risk:** Safe (no real trades)

---
