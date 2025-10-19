from fastapi import APIRouter, HTTPException    
import pandas as pd


from app.services.portfolio.helpers.input_calcs import compute_expected_returns, compute_risk_matrix
from app.services.portfolio.helpers.hrp_calcs import hrp_allocation
from app.services.portfolio.helpers.optimisation_calcs import optimise_portfolio
from app.schemas import PortfolioInputsPayload, HrpPayload, OptimisePayload


router = APIRouter()



@router.post("/inputs")
async def compute_portfolio_inputs(payload: PortfolioInputsPayload):
    """
    Compute expected returns and risk matrix for portfolio construction.
    Expects payload like:
    {
        "returns": {
            "AAPL": [0.01, -0.002, 0.005, ...],
            "MSFT": [0.007, 0.004, -0.003, ...]
        }
        "ewma_decay": 0.94
    }
    """
    returns = payload.returns
    if not returns:
        raise HTTPException(status_code=404, detail="No returns provided")

    expected_returns = compute_expected_returns(returns, payload.ewma_decay)
    risk_matrix = compute_risk_matrix(returns)

    return {
        "expected_returns": expected_returns,
        "risk_matrix": risk_matrix
    }


@router.post("/hrp")
async def compute_hrp(payload: HrpPayload):
    if not payload.riskMatrix:
        raise HTTPException(status_code=404, detail="No risk_matrix provided")

    risk_matrix_data = payload.riskMatrix
    symbols = risk_matrix_data.get("symbols", [])
    cov_matrix = risk_matrix_data.get("cov_matrix", [])
    
    if not symbols or not cov_matrix:   
        raise HTTPException(status_code=404, detail="Invalid risk_matrix")
    
    cov_df = pd.DataFrame(cov_matrix, index=symbols, columns=symbols)
    
    # Compute HRP weights using helper function
    weights = hrp_allocation(cov_df)
    
    return {"weights": weights.to_dict()}


@router.post("/optimise")
async def compute_optimized_portfolio(payload: OptimisePayload):
    try:
        weights = optimise_portfolio(
            mu_dict=payload.expected_returns,
            cov_dict=payload.risk_matrix,
            w_baseline_dict=payload.baseline_weights,
            risk_aversion=payload.params["risk_aversion"]["value"],
            baseline_reg=payload.params["baseline_reg"]["value"],
            min_weight=payload.params["min_weight"]["value"],
            max_weight=payload.params["max_weight"]["value"]
        )
        print("done")
        return {"weights": weights}
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=404, detail=str(e))