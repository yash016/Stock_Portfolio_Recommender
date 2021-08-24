import pandas as pd
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import json
from database import SessionLocal, engine

# from models import Stock
from yahoo_fin import stock_info as si
from starlette.responses import Response
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices


app = FastAPI()

class PortfolioValue(BaseModel):
    portfolio_val: int


@app.post("/recommendation")
async def get_recommendation(data: PortfolioValue):
    
    t = si.tickers_sp500()
    tickers = []
    t.remove('ALL')
    for x in t:
        tickers.append(x.replace('-', ''))

    adjclose = []
    for ticker in tickers:
        col = pd.read_sql('SELECT `Adj Close` AS {} FROM {}'.format(ticker,ticker), engine)
        adjclose.append(col)
        
    df = pd.concat(adjclose, sort=True, axis=1)
    # Calculate the expected annnualized returns and the annualized sample covariance matrix of the daily asset returns
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    
    # Optimize for the miximal Sharpe ratio
    ef = EfficientFrontier(mu, S) # Create the Efficient Frontier Object
    weights = ef.max_sharpe()

    cleaned_weights = ef.clean_weights()
    
    latest_prices = get_latest_prices(df)
    weights = cleaned_weights
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value = data.portfolio_val)
    allocation, leftover = da.lp_portfolio()
    
    for key in allocation:
        allocation[key] = int(allocation[key])
        
    json_obj = json.dumps(allocation)
    
        
    return Response(json_obj)

if __name__ == '__main__':
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
    