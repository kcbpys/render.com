from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf

app = FastAPI()

# Add CORS middleware to allow requests from your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fastapi-publish.onrender.com"],  # Allow only your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to the Stock Data App. Visit /static/hello.html to use the frontend."
        }
    )

@app.get("/stock/{ticker}")
async def get_stock_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get("longName", "N/A")

        previous_close = info.get("previousClose", "N/A")

        regular_market_price = (
            info.get("currentPrice")
            or info.get("navPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
            or "N/A"
        )

        if regular_market_price != "N/A" and previous_close != "N/A":
            daily_change_percent = round(
                ((regular_market_price - previous_close) / previous_close) * 100, 2
            )
        else:
            daily_change_percent = "N/A"

        raw_market_cap = info.get("marketCap", None)
        if raw_market_cap:
            if raw_market_cap >= 1e12:
                market_cap = f"{round(raw_market_cap / 1e12, 2)}T - Mega Cap"
            elif raw_market_cap >= 1e9:
                market_cap = f"{round(raw_market_cap / 1e9, 2)}B - Large Cap"
            elif raw_market_cap >= 1e6:
                market_cap = f"{round(raw_market_cap / 1e6, 2)}M - Small Cap"
            else:
                market_cap = f"{raw_market_cap} - Nano Cap"
        else:
            market_cap = "N/A"

        round_beta = round(info.get("beta", "N/A"), 2) if info.get("beta") else "N/A"

        all_volume = f"{info.get('volume', 'N/A')} / {info.get('averageVolume', 'N/A')}"

        data = {
            "company_name": company_name,
            "price": f"{regular_market_price:.2f}" if regular_market_price != "N/A" else "N/A",
            "daily_change": daily_change_percent,
            "market_cap": market_cap,
            "volume": all_volume,
            "beta": f"{round_beta:.2f}" if isinstance(round_beta, (int, float)) else "N/A",
        }
        return JSONResponse(content=data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
