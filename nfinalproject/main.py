from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf

app = FastAPI()

# Mount the static directory (ensure the "static" folder exists)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware to allow requests from any origin (update for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production if possible
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_volume(val):
    """
    Format the volume value:
      - If the volume is 1,000,000 or greater, display as millions with 2 decimals (e.g., "2.50M").
      - If less than 1,000,000, display as thousands (rounded to whole number, e.g., "250K").
    """
    if isinstance(val, (int, float)):
        if val >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        else:
            return f"{val / 1_000:.0f}K"
    return "N/A"

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

        # Format price to 2 decimal places if numeric
        if isinstance(regular_market_price, (int, float)):
            price_formatted = f"{regular_market_price:.2f}"
        else:
            price_formatted = "N/A"

        # Calculate daily change percentage (if possible and avoid division by zero)
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

        # Handle beta value (accept beta = 0 as valid)
        beta_value = info.get("beta")
        round_beta = round(beta_value, 2) if beta_value is not None else "N/A"

        # Format volume and average volume using our helper
        volume = info.get("volume")
        average_volume = info.get("averageVolume")
        formatted_volume = format_volume(volume)
        formatted_avg_volume = format_volume(average_volume)
        all_volume = f"{formatted_volume} / {formatted_avg_volume}"

        # Additional data fields: Format 52 Week High and Low as dollar values with 2 decimals
        year_high = info.get("fiftyTwoWeekHigh", "N/A")
        if isinstance(year_high, (int, float)):
            year_high = f"{year_high:.2f}"
        year_low = info.get("fiftyTwoWeekLow", "N/A")
        if isinstance(year_low, (int, float)):
            year_low = f"{year_low:.2f}"

        if info.get("trailingPE") is not None:
            pe_trailing = str(round(info.get("trailingPE"), 2))
        else:
            pe_trailing = "N/A"
        pe_forward = info.get("forwardPE")
        if pe_forward <0:
            pe_forward = "N/A"
        if pe_forward != "N/A":
            pe_forward = str(round(pe_forward, 2))
        else:
            pe_forward = "N/A"
        pe_total = pe_trailing + " / " + pe_forward


        data = {
            "company_name": company_name,
            "price": price_formatted,
            "daily_change": daily_change_percent,
            "market_cap": market_cap,
            "volume": all_volume,
            "beta": f"{round_beta:.2f}" if isinstance(round_beta, (int, float)) else "N/A",
            "year_high": year_high,
            "year_low": year_low,
            "pe_ratio_total": pe_ratio_total,
            "forward_pe": forward_pe,
        }

        return JSONResponse(content=data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
