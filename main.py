from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    # Redirect root URL to your HTML file
    return JSONResponse(content={"message": "Welcome to the Stock Data App. Visit /static/index.html to use the frontend."})


@app.get("/stock/{ticker}")
async def get_stock_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get("longName", "N/A")

        if info.get("previousClose") is not None:
            previous_close = info.get("previousClose")
        else:
            previous_close = "N/A"

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

        if daily_change_percent != "N/A" and isinstance(daily_change_percent, (int, float)):
            ndaily_change_percent = daily_change_percent * 1000
        else:
            ndaily_change_percent = "N/A"

        if ndaily_change_percent != "N/A":
            daily_change_percent = f" or {'+' if daily_change_percent >= 0 else ''}{daily_change_percent}"

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

        if info.get("beta"):
            round_beta = round(info.get("beta"), 2)
        else:
            round_beta = "N/A"

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
