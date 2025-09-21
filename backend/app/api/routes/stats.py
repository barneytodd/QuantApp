from fastapi import APIRouter
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from app.schemas import CointegrationRequest

router = APIRouter()

# Endpoint for Engle-Granger cointegration test
@router.post("/engle-granger")
def engle_granger_endpoint(req: CointegrationRequest):
    y = np.array(req.y)
    x = np.array(req.x)
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    residuals = model.resid
    adf_result = adfuller(residuals)
    
    return {
        "alpha": float(model.params[0]),
        "beta": float(model.params[1]),
        "cointegrated": adf_result[1] < 0.05,  # True if p-value < 0.05
        "p_value": float(adf_result[1])
    }
