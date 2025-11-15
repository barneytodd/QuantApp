from .portfolios.fully_optimised_seed import seed_data as full_optim_seed
from .portfolios.params_optimised_seed import seed_data as param_optim_seed
from .portfolios.strategy_select_seed import seed_data as strat_select_seed

portfolio_seed_data = full_optim_seed + param_optim_seed + strat_select_seed
