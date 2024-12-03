// Fetch and display stock data
async function fetchStockData() {
    const ticker = document.getElementById("ticker").value.trim();
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "Loading...";
    if (!ticker) {
        resultsDiv.innerHTML = "Enter a stock ticker.";
        return;
    }
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/stock/${ticker}`);
        if (!response.ok) {
            throw new Error("Ticker not found");
        }
        const data = await response.json();
        if (data.error) {
            resultsDiv.innerHTML = `Error: ${data.error}`;
        } else {
            // Determine color based on daily change percentage
            let priceColor = "black"; // Default color
            if (data.ndaily_change_percent !== null && !isNaN(data.ndaily_change_percent)) {
                if (data.ndaily_change_percent > 0) {
                    priceColor = "green"; // Positive change
                } else if (data.ndaily_change_percent < 0) {
                    priceColor = "red"; // Negative change
                }
            }
            // Establishing of the data dictionary below using HTML as style parameters 
        const companyName = data.company_name || "N/A"; 
            resultsDiv.innerHTML = `
                <b style="text-align: center;"><u>${data.company_name || "N/A"}</u></b>
                <p><strong>Price:</strong> <span style="color:${priceColor};">$${data.price || "N/A"}</span></p>
                <p><strong>Daily Change:</strong> ${data.daily_change || "N/A"}%</p>
                <p><strong>Market Cap:</strong> ${data.market_cap || "N/A"}</p>
                <p><strong>Vol/Avg:</strong> ${data.volume || "N/A"}</p>
                <p><strong>52 Week High:</strong> ${data.year_high || "N/A"}</p>
                <p><strong>52 Week Low:</strong> ${data.year_low || "N/A"}</p>
                <p><strong>PE Ratio (TTM/FTM):</strong> ${data.pe_ratio_total || "N/A"}</p>
                <p><strong>Beta(5Y):</strong> ${data.beta || "N/A"}</p>
            `;
        }
    } catch (err) {
        resultsDiv.innerHTML = `Error:= ${err.message}`;
    }
}

// Event listener for the "Get Data" button
document.getElementById("fetchData").addEventListener("click", () => {
    fetchStockData();
});

// Event listener for pressing Enter in the input field
document.getElementById("ticker").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        fetchStockData();
    }
});
