# ==============================
# STG3 REQ FILE
# ==============================


# ==============================
# OPTION SELECTION
# ==============================
def select_option(cfg, breakout_side):
    """
    Decide CE / PE based on config
    """

    mode = cfg.get("breakout_type", "dynamic")

    if mode == "fixed_ce":
        return "CE"

    elif mode == "fixed_pe":
        return "PE"

    elif mode == "dynamic":
        return breakout_side

    # fallback
    return breakout_side


# ==============================
# ATM STRIKE CALCULATION
# ==============================
def get_atm(price, step=50):
    return round(price / step) * step


# ==============================
# OPTION SYMBOL BUILDER
# ==============================
def get_option_symbol(symbol, price, opt_type):
    """
    Example:
    NIFTY + 22500 + CE → NIFTY25APR22500CE
    """

    strike = get_atm(price)

    # TODO: later auto expiry
    expiry = "25APR"

    return f"{symbol}{expiry}{strike}{opt_type}"