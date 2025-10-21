import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas import HrpPayload, OptimisePayload, PortfolioInputsPayload
from app.services.portfolio.stages.portfolio_weight_allocation.helpers import (
    hrp_allocation,
    compute_expected_returns,
    compute_risk_matrix,
    optimise_portfolio
)

router = APIRouter()


# === Compute expected returns and risk matrix ===
@router.post("/inputs")
async def compute_portfolio_inputs(payload: PortfolioInputsPayload):
    """
    Compute expected returns and risk (covariance) matrix for portfolio construction.
    
    Args:
        payload: PortfolioInputsPayload containing:
            - returns: dict of historical returns per symbol
            - ewma_decay: decay factor for EWMA expected returns calculation

    Returns:
        Dict containing:
            - expected_returns: dict of symbol -> expected return
            - risk_matrix: dict with "symbols" and "cov_matrix"
    
    Raises:
        HTTPException: if no returns are provided.
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


# === Hierarchical Risk Parity (HRP) allocation ===
@router.post("/hrp")
async def compute_hrp(payload: HrpPayload):
    """
    Compute HRP portfolio weights given a risk (covariance) matrix.

    Args:
        payload: HrpPayload containing a risk_matrix dict:
            - symbols: list of symbols
            - cov_matrix: 2D list representing the covariance matrix

    Returns:
        Dict of symbol -> HRP weight
    
    Raises:
        HTTPException: if risk_matrix is missing or invalid
    """
    risk_matrix_data = payload.riskMatrix
    if not risk_matrix_data:
        raise HTTPException(status_code=404, detail="No risk_matrix provided")

    symbols = risk_matrix_data.get("symbols", [])
    cov_matrix = risk_matrix_data.get("cov_matrix", [])

    if not symbols or not cov_matrix:
        raise HTTPException(status_code=404, detail="Invalid risk_matrix")

    cov_df = pd.DataFrame(cov_matrix, index=symbols, columns=symbols)

    weights = hrp_allocation(cov_df)
    return {"weights": weights.to_dict()}


# === Optimized portfolio allocation ===
@router.post("/optimise")
async def compute_optimized_portfolio(payload: OptimisePayload):
    """
    Compute an optimized portfolio allocation using mean-variance and baseline regularization.

    Args:
        payload: OptimisePayload containing:
            - expected_returns: dict of symbol -> expected return
            - risk_matrix: dict with covariance matrix
            - baseline_weights: dict of baseline weights
            - params: dict containing risk_aversion, baseline_reg, min_weight, max_weight

    Returns:
        Dict of symbol -> optimized weight
    
    Raises:
        HTTPException: if optimization fails
    """
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
        return {"weights": weights}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
