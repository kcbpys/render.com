from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware to allow requests from any origin (update for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

        # Get company name
        company_name = info.get("longName") or "N/A"

        # Retrieve numeric values for price calculations
        previous_close = info.get("previousClose")
        regular_market_price = (
            info.get("currentPrice")
            or info.get("navPrice")
            or info.get("regularMarketPrice")
            or previous_close
        )

        # Calculate daily change percentage if possible (and prevent division by zero)
        if (
            isinstance(regular_market_price, (int, float)) and 
            isinstance(previous_close, (int, float)) and 
            previous_close != 0
        ):
            daily_change_percent = round(
                ((regular_market_price - previous_close) / previous_close) * 100, 2
            )
        else:
            daily_change_percent = "N/A"

        # Calculate market capitalization with proper formatting
        raw_market_cap = info.get("marketCap")
        if isinstance(raw_market_cap, (int, float)):
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

        # Fix beta handling: allow beta value 0 to be valid
        beta_value = info.get("beta")
        if beta_value is not None:
            round_beta = round(beta_value, 2)
        else:
            round_beta = "N/A"

        # Combine volume and average volume
        volume = info.get("volume", "N/A")
        average_volume = info.get("averageVolume", "N/A")
        all_volume = f"{volume} / {average_volume}"

        # Additional data fields
        year_high = info.get("fiftyTwoWeekHigh", "N/A")
        year_low = info.get("fiftyTwoWeekLow", "N/A")
        pe_ratio_total = info.get("trailingPE", "N/A")

        data = {
            "company_name": company_name,
            "price": f"{regular_market_price:.2f}" if isinstance(regular_market_price, (int, float)) else "N/A",
            "daily_change": daily_change_percent,
            "market_cap": market_cap,
            "volume": all_volume,
            "beta": f"{round_beta:.2f}" if isinstance(round_beta, (int, float)) else "N/A",
            "year_high": year_high,
            "year_low": year_low,
            "pe_ratio_total": pe_ratio_total,
        }

        return JSONResponse(content=data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
