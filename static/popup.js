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
      // Change the URL if testing locally (e.g., "http://127.0.0.1:8000/stock/" + ticker)
      const response = await fetch(`https://fastapi-publish.onrender.com/stock/${ticker}`);
      
      if (!response.ok) {
        throw new Error("Ticker not found");
      }
      
      const data = await response.json();
      
      if (data.error) {
        resultsDiv.innerHTML = `Error: ${data.error}`;
      } else {
        // Determine color based on daily change percentage
        let priceColor = "black"; // Default color
        if (data.daily_change !== "N/A" && !isNaN(data.daily_change)) {
          if (data.daily_change > 0) {
            priceColor = "green";
          } else if (data.daily_change < 0) {
            priceColor = "red";
          }
        }
        
        // Build the result HTML
        const companyName = data.company_name || "N/A"; 
        resultsDiv.innerHTML = `
          <b style="text-align: center;"><u>${companyName}</u></b>
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
      resultsDiv.innerHTML = `Error: ${err.message}`;
    }
  }
  
  // Event listeners for button click and Enter key
  document.getElementById("fetchData").addEventListener("click", fetchStockData);
  document.getElementById("ticker").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      fetchStockData();
    }
  });
  