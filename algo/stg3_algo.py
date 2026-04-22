
import os
import time
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import configparser

TZ = ZoneInfo("Asia/Kolkata")


# =========================================================
# LIVE PRICE FUNCTION (USED ONLY IN LIVE MODE)
# =========================================================
def get_live_price(kite, symbol):

    try:
        instrument = f"NSE:{symbol}"

        data = kite.ltp([instrument])

        if not data or instrument not in data:
            print(f"⚠️ No data from Kite for {instrument}")
            return None

        return data[instrument]["last_price"]

    except Exception as e:
        print(f"❌ Kite Error: {e}")
        return None
# =========================================================
# LOAD CONFIG FILE (INI FORMAT)
# =========================================================
def load_cfg(file="stg3.cfg"):

    print("\n📂 LOADING CONFIG FILE...")

    config = configparser.ConfigParser()
    config.read(file)

    cfg = {}

    cfg["symbol"] = config["GENERAL"]["symbol"]
    cfg["mode"] = config["GENERAL"]["mode"]
    cfg["qty"] = int(config["GENERAL"]["qty"])

    cfg["csv_file"] = config["DATA"]["csv_file"]

    cfg["initial_wait"] = int(config["STRATEGY"]["initial_wait_time"])
    cfg["max_range"] = float(config["STRATEGY"]["max_range"])
    cfg["breakout_type"] = config["STRATEGY"]["breakout_type"]
    cfg["rr_activate"] = float(config["STRATEGY"]["rr_activate"])
    cfg["hard_rr_exit"] = float(config["STRATEGY"]["hard_rr_exit"])

    cfg["minute_log"] = config["LOGGING"]["enable_minute_log"] == "true"
    cfg["summary_log"] = config["LOGGING"]["enable_summary_log"] == "true"

    print("✅ CONFIG LOADED SUCCESSFULLY\n")

    return cfg


# =========================================================
# RANGE CALCULATION FUNCTION
# =========================================================
def calculate_range(df):

    high = df["High"].max()
    low = df["Low"].min()
    range_val = high - low

    return high, low, range_val


# =========================================================
# MAIN STRATEGY FUNCTION
# =========================================================
def run():

    cfg = load_cfg()

    print("====================================================")
    print("🚀 STG3 STRATEGY STARTED (FULL DETAILED VERSION)")
    print("====================================================\n")

    # =====================================================
    # MODE CHECK
    # =====================================================
    if cfg["mode"] == "live":

        print("📡 MODE SELECTED → LIVE DATA (NO REAL TRADES)\n")

        from kiteconnect import KiteConnect
        from key import api_k, access_token

        kite = KiteConnect(api_key=api_k)
        kite.set_access_token(access_token)

    elif cfg["mode"] == "csv":

        print("📊 MODE SELECTED → CSV BACKTEST\n")

    else:
        print("❌ Invalid mode in config")
        return

    # =====================================================
    # DATA LOADING (ONLY FOR CSV MODE)
    # =====================================================
    if cfg["mode"] == "csv":

        print("📥 Loading CSV data...")

        df = pd.read_csv(cfg["csv_file"])

        # CLEAN DATE
        df["Date"] = df["Date"].astype(str)
        df["Date"] = df["Date"].str.replace("GMT+0530 (India Standard Time)", "", regex=False)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        df = df.dropna(subset=["Date"])

        print(f"✅ Data Loaded → {len(df)} rows\n")

    # =====================================================
    # RANGE BUILDING
    # =====================================================
    print("⏳ BUILDING INITIAL RANGE...\n")

    if cfg["mode"] == "csv":

        candles = cfg["initial_wait"] // 5

        print(f"📊 Using first {candles} candles for range\n")

        range_df = df.head(candles)

        high, low, rng = calculate_range(range_df)

    else:

        prices = []
        start_time = datetime.now(TZ)

        print("⏳ Collecting LIVE prices...\n")

        while (datetime.now(TZ) - start_time).seconds < cfg["initial_wait"] * 60:

            price = get_live_price(kite, cfg["symbol"])

            if price is None:
                time.sleep(1)
                continue

            prices.append(price)

            current_high = max(prices)
            current_low = min(prices)

            print(
        f"⏳ PRICE: {price} | "
        f"HIGH: {round(current_high,2)} | "
        f"LOW: {round(current_low,2)}"
    )

            time.sleep(60)   # ✅ INSIDE LOOP


# ✅ OUTSIDE LOOP (correct)
    high = max(prices)
    low = min(prices)
    rng = high - low

    print("\n📊 RANGE DETAILS")
    print("--------------------------------")
    print(f"🔺 HIGH : {high}")
    print(f"🔻 LOW  : {low}")
    print(f"📏 RANGE: {round(rng,2)}")

    # =====================================================
    # RANGE VALIDATION
    # =====================================================
    if rng > cfg["max_range"]:
        print("❌ Range too large → TRADE CANCELLED")
        return

    print("✅ RANGE VALID → WAITING FOR BREAKOUT\n")

    # =====================================================
    # VARIABLES
    # =====================================================
    entry = None
    sl = None
    direction = None
    risk = None

    mode = 1   # 1 = waiting, 2 = trade

    qty = cfg["qty"]

    max_pnl = float("-inf")
    min_pnl = float("inf")

    print("🧠 MODE 1 → WAITING STATE\n")

    # =====================================================
    # LOOP SETUP
    # =====================================================
    if cfg["mode"] == "csv":
        loop_iter = range(candles, len(df))
    else:
        loop_iter = iter(int, 1)

    # =====================================================
    # MAIN LOOP
    # =====================================================
    for i in loop_iter:

        # ---------------------------------------------
        # DATA FETCH
        # ---------------------------------------------
        if cfg["mode"] == "csv":

            row = df.iloc[i]
            price = row["Close"]
            time_str = row["Date"].strftime("%H:%M")

        else:

            price = get_live_price(kite, cfg["symbol"])

            if price is None:
                time.sleep(1)
                continue
            time_str = datetime.now(TZ).strftime("%H:%M:%S")

        # ---------------------------------------------
        # WAITING MODE
        # ---------------------------------------------
        if direction is None:

            print(f"[{time_str}] MODE 1 → WAITING | PRICE: {price}")

            if price > high:

                direction = "CE"   # ✅ FIRST SET THIS

                entry = price
                sl = low
                risk = entry - sl
                mode = 2

    # ================= LEVELS =================
                r1 = entry + risk
                r2 = entry + 2 * risk
                s1 = entry - risk
                s2 = entry - 2 * risk

                print("\n🚀 BREAKOUT UP DETECTED")
                print("➡️ TYPE: CE")
                print(f"🎯 ENTRY: {entry} | SL: {sl}")
                print(f"📊 R1:{round(r1,2)} | R2:{round(r2,2)} | S1:{round(s1,2)} | S2:{round(s2,2)}\n")

                
                print("➡️ TYPE: CE")
                
                

            elif price < low:

                direction = "PE"   # ✅ SET FIRST

                entry = price
                sl = high
                risk = sl - entry
                mode = 2

        # ================= LEVELS =================
                r1 = entry - risk
                r2 = entry - 2 * risk
                s1 = entry + risk
                s2 = entry + 2 * risk

                print("\n🚀 BREAKOUT DOWN DETECTED")
                print(f"🎯 ENTRY: {entry} | SL: {sl}")
                print(f"📊 R1:{round(r1,2)} | R2:{round(r2,2)} | S1:{round(s1,2)} | S2:{round(s2,2)}\n")

        # ---------------------------------------------
        # TRADE MODE
        # ---------------------------------------------
        else:

            if direction == "CE":
                pnl = (price - entry) * qty
                rr = (price - entry) / risk
            else:
                pnl = (entry - price) * qty
                rr = (entry - price) / risk

            max_pnl = max(max_pnl, pnl)
            min_pnl = min(min_pnl, pnl)

            print("\n--------------------------------------------------")
            print(
    f"{time_str} | "
    f"M:{mode} | "
    f"P:{round(price,2)} | "
    f"E:{round(entry,2)} | "
    f"P:{round(price,2)} | "
    f"R1:{round(r1,2)} | "
    f"R2:{round(r2,2)} | "
    f"S1:{round(s1,2)} | "
    f"S2:{round(s2,2)} | "
    f"PnL:{round(pnl,2)} | "
    f"RR:{round(rr,2)} | "
    f"MAX:{round(max_pnl,2)} | "
    f"MIN:{round(min_pnl,2)}"
)
            print("--------------------------------------------------")

            # LOGGING
            if cfg["minute_log"]:

                log_row = {
                    "TIME": time_str,
                    "MODE": mode,
                    "PRICE": price,
                    "ENTRY": entry,
                    "SL": sl,
                    "RR": round(rr, 2),
                    "PNL": round(pnl, 2),
                    "MAX_PNL": round(max_pnl, 2),
                    "MIN_PNL": round(min_pnl, 2)
                }

                pd.DataFrame([log_row]).to_csv(
                    "stg3_log.csv",
                    mode="a",
                    index=False,
                    header=not os.path.exists("stg3_log.csv")
                )

            # EXIT CONDITIONS
            if rr >= cfg["hard_rr_exit"]:
                print("\n🎯 TARGET HIT → EXIT")
                break

            if (direction == "CE" and price <= sl) or (direction == "PE" and price >= sl):
                print("\n❌ STOPLOSS HIT → EXIT")
                break

        if cfg["mode"] == "live":
            time.sleep(1)

    # =====================================================
    # FINAL SUMMARY
    # =====================================================
    print("\n====================================================")
    print("📊 FINAL SUMMARY")
    print("====================================================")

    print(f"📈 MAX PnL: {round(max_pnl,2)}")
    print(f"📉 MIN PnL: {round(min_pnl,2)}")


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    run()
