# 📊 NIFTY 50 - Complete Data Collection Script (2014 to Yesterday)

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Create necessary folders
os.makedirs("data/price", exist_ok=True)
os.makedirs("data/info", exist_ok=True)
os.makedirs("data/events", exist_ok=True)

# Automatically set end date to yesterday
start_date = "2014-01-01"
end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

# NIFTY 50 symbols list (with .NS)
nifty_50_symbols = [
    "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
    "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "INDUSINDBK.NS", "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS", "LT.NS", "M&M.NS", "MARUTI.NS",
    "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
    "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "UPL.NS", "WIPRO.NS"
]

# Storage lists
all_price_data = []
combined_info = pd.DataFrame()
combined_events = pd.DataFrame()

# Loop through each symbol
for symbol in nifty_50_symbols:
    print(f"🔄 Processing: {symbol}")
    try:
        ticker = yf.Ticker(symbol)

        # 1. Price Data
        price_df = ticker.history(start=start_date, end=end_date).reset_index()
        price_df["Symbol"] = symbol.replace(".NS", "")
        price_df.to_csv(f"data/price/{symbol.replace('.NS','')}_price.csv", index=False)
        all_price_data.append(price_df)

        # 2. Company Info
        info = ticker.info
        info_row = {
            "Symbol": symbol.replace(".NS", ""),
            "Company Name": info.get("longName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "Business Summary": info.get("longBusinessSummary")
        }
        combined_info = pd.concat([combined_info, pd.DataFrame([info_row])], ignore_index=True)

        # 3. Events (Dividends + Splits)
        for event_type, event_df in {"Dividend": ticker.dividends, "Split": ticker.splits}.items():
            if not event_df.empty:
                df = event_df.reset_index()
                df.rename(columns={df.columns[0]: "Date", df.columns[1]: "Value"}, inplace=True)
                df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)  # Remove timezone
                df["Event"] = event_type
                df["Symbol"] = symbol.replace(".NS", "")
                combined_events = pd.concat([combined_events, df], ignore_index=True)

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")

# 4. Save to Excel
output_excel = "data/NIFTY50_Master_Info_Events.xlsx"
with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
    combined_info.to_excel(writer, sheet_name="Company_Info", index=False)
    combined_events.to_excel(writer, sheet_name="Corporate_Events", index=False)

# 5. Save Combined Price CSV
master_price_df = pd.concat(all_price_data, ignore_index=True)
master_price_df.to_csv("data/NIFTY50_Master_Price.csv", index=False)

print(f"\n✅ Done! All stock data (till {end_date}) saved in 'data/' folder.")

