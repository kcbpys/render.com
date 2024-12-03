from fastapi import FastAPI
from fastapi.responses import JSONResponse
import yfinance as yf

app = FastAPI()

@app.get("/stock/{ticker}")
async def get_stock_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract company name
        company_name = info.get('longName', "N/A")

        # Extract and handle regular market price
        regular_market_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
            or "N/A"
        )

        # Extract previous close
        previous_close = info.get("previousClose", "N/A")

        # Calculate daily change percentage
        if regular_market_price != "N/A" and previous_close != "N/A":
            daily_change_percent = round(((regular_market_price - previous_close) / previous_close) * 100, 2)
        else:
            daily_change_percent = "N/A"

        # Calculate daily change
        if regular_market_price != "N/A" and previous_close != "N/A":
            day_change = round(regular_market_price - previous_close, 2)
        else:
            day_change = "N/A"

        # Format market cap
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

        # Extract 52-week high/low
        year_low = info.get("fiftyTwoWeekLow", "N/A")
        year_high = info.get("fiftyTwoWeekHigh", "N/A")

        # Format volume and average volume
        def format_volume(value):
            if value is None:
                return "N/A"
            elif value >= 1e9:
                return f"{round(value / 1e9, 2)}B"
            elif value >= 1e6:
                return f"{round(value / 1e6, 2)}M"
            elif value >= 1e3:
                return f"{round(value / 1e3, 2)}K"
            return str(value)

        volume = format_volume(info.get("volume"))
        avg_volume = format_volume(info.get("averageVolume"))
        all_volume = f"{volume} / {avg_volume}" if volume != "N/A" and avg_volume != "N/A" else "N/A"

        # Format P/E ratios
        pe_trailing = info.get("trailingPE", "N/A")
        pe_forward = info.get("forwardPE", "N/A")
        pe_total = f"{pe_trailing} / {pe_forward}"

        # Extract beta
        beta = info.get("beta")
        beta = round(beta, 2) if isinstance(beta, (int, float)) else "N/A"

        # Prepare response data
        data = {
            "company_name": company_name,
            "price": f"{regular_market_price:.2f}" if isinstance(regular_market_price, (int, float)) else "N/A",
            "daily_change": f"{day_change:+.2f}" if isinstance(day_change, (int, float)) else "N/A",
            "daily_change_percent": f"{daily_change_percent:+.2f}%" if isinstance(daily_change_percent, (int, float)) else "N/A",
            "market_cap": market_cap,
            "volume": all_volume,
            "pe_ratio_total": pe_total,
            "beta": beta,
            "year_low": f"{year_low:.2f}" if isinstance(year_low, (int, float)) else "N/A",
            "year_high": f"{year_high:.2f}" if isinstance(year_high, (int, float)) else "N/A",
        }

        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
