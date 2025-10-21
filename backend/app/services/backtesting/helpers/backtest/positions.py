from .advanced_params import check_holding_period
from .pricing import calc_effective_price, commission
from app.strategies.signal_registry import generators

def check_signal(position, date_idx, date, entry_date, data, params, strategy, lookback):
	"""
	Check the signal for a given position on a specific date.

	---params---
	position: int 0=no position, >0=long,<0=short
	data: list [{"date":..., "close":...}, ...]
	entry_date: dict {"idx": idx, "date": date} where idx is the date's index in the overall list of dates
	params: strategy parameters
	strategy: str

	---return---
	signal: str indicating trading signal
	index: int 
	"""
	if strategy == "pairs_trading":
		if data.empty:
			return "hold"
	elif not data or len(data) == 0:
		return "hold"

	if date_idx < lookback:
		return "hold"

	chp = check_holding_period(params["minHoldingPeriod"], position, entry_date, date_idx, date)
	if not chp:
		return "hold"

	dates = data["date"].tolist() if strategy == "pairs_trading" else [row["date"] for row in data]
	
	try:
		i = dates.index(date)
	except ValueError:
		return "hold"

	signal = generators[strategy](data, i, params)

	if position <= 0 and signal in ["sell"]:
		return "hold"

	elif position != 0 and signal in ["buy", "long", "short"]:
		return "hold"

	elif position == 0 and signal == "exit":
		return "hold"

	return signal


def open_position(signal, prices, capital, slippage_pct, transaction_pct, transaction_fixed):
	"""
	Open a position (buy, long, short) at given price.
	Returns new position size, updated capital, entry price, entry date
	"""
	action = []
	if signal == "buy":
		action.append("buy")
	elif signal == "short":
		action.extend(["sell", "buy"])
	else:
		action.extend(["buy", "sell"])

	new_positions = []
	cap = capital
	entry_prices = []

	for i, price in enumerate(prices):
		if action[i] == "buy":
			effective_price = calc_effective_price(price, slippage_pct, "buy")
			if signal == "buy":
				position = (cap - commission("buy", cap, effective_price, 0, transaction_pct, transaction_fixed)) / effective_price
			else: 
				position = cap / effective_price
		else:
			effective_price = calc_effective_price(price, slippage_pct, "sell")
			position = -1 * cap / effective_price
		
		new_positions.append(position)	
		cap -= position * effective_price + commission(action[i], cap, effective_price, abs(position), transaction_pct, transaction_fixed)
		

		entry_prices.append(price)
    
	return new_positions, cap, entry_prices


def close_position(symbols, prices, capital, entry_prices, positions, date, entry_date, slippage_pct, transaction_pct, transaction_fixed):
	"""
	Close an existing position (sell, exit) at given price.
	Returns new position size (0), updated capital, trade records, entry price, entry date
	"""
	new_capital = capital
	trades = []
	for i, symbol in enumerate(symbols):
		position = positions[i]
		if position == 0:
			continue

		price = prices[i]
		entry_price = entry_prices[i]
		action = "sell" if position > 0 else "buy"
		entry_action = "buy" if position > 0 else "sell"
		direction = "Long" if position > 0 else "Short"

		effective_exit = calc_effective_price(price, slippage_pct, action)
		effective_entry = calc_effective_price(entry_price, slippage_pct, entry_action)
		pnl = position * (effective_exit - effective_entry)
		if direction == "Long":
			return_pct = (effective_exit - effective_entry) / effective_entry * 100
		else:
			return_pct = (effective_entry - effective_exit) / effective_entry * 100
		
		trades.append({
			"symbol": symbol,
			"direction": direction,
			"entryDate": entry_date,
			"exitDate": date,
			"entryPrice": entry_price,
			"exitPrice": price,
			"pnl": pnl,
			"returnPct": return_pct
		})
		
		new_capital += position * effective_exit
		if action == "sell":
			new_capital -= commission("sell", 0, effective_exit, position, transaction_pct, transaction_fixed)
		else:
			new_capital -= commission("buy", -1*position*effective_exit, effective_exit, position, transaction_pct, transaction_fixed)
    
	return new_capital, trades