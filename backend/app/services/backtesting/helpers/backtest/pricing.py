# Calculate commission costs
def commission(signal="buy", capital=0, effective_price=0, position=0, commission_pct=0.001, commission_fixed=0.0):
    if signal == "buy":
        return (capital * commission_pct + commission_fixed) / (1 + commission_pct)
    else:
        return position * effective_price * commission_pct + commission_fixed

# Calculate effective price considering slippage
def calc_effective_price(price, slippage_pct=0.001, signal="buy"):
    if signal == "buy":
        return price * (1 + slippage_pct)
    else:
        return price * (1 - slippage_pct)