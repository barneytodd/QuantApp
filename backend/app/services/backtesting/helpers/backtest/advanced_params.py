from datetime import datetime
import numpy as np

def check_holding_period(min_holding_period, position, entry_date, date):
	"""
	checks if position has been open longer than the min holding period
	min_holding_period: int
	position: int = 0 => no open position
	entry_date: date position was opened
	date: current date for which a signal is being generated	
	"""
	if min_holding_period == 0 or position == 0:
		return True
	else:
		fmt = "%Y-%m-%d"
		d1 = datetime.strptime(entry_date, fmt)
		d2 = datetime.strptime(date, fmt)
		diff = (d2-d1).days
		if diff >= min_holding_period:
			return True
		else:
			return False


def rebalance(equity_curves, positions, prices, target_vol, lookback):
	"""
	rebalances portfolio based on a target volatility
	"""
	returns = np.array([
		np.diff(np.log([e["value"] for e in equity_curves[s]]))
		for s in equity_curves if s != "overall"
	]).T
	window = returns[-lookback:, :]
	cov = np.cov(window.T, bias=False)
	cov_annual = cov * 252  

	total_exposure = sum(positions[s]*prices[s] for s in positions)
	if total_exposure == 0:
		return positions
	weights = np.array([positions[s]*prices[s]/total_exposure for s in positions])

	port_var = np.dot(weights, np.dot(cov_annual, weights))
	port_vol = np.sqrt(port_var)

	if port_vol == 0:
		return positions
	print(target_vol, port_vol)
	k = target_vol / port_vol

	return {s:k*p for s,p in positions.items()}
