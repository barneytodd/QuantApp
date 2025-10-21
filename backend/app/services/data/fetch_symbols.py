import time
from yfinance import EquityQuery, screen

# === Yahoo Finance Symbol Fetch Engine ===
def fetch_symbols(
    page_size=250, 
    pause=0.3, 
    regions=['us'], 
    exchanges=['NMS','NYQ'], 
    sectors=[],
    industries=[],
    min_market_cap=1_000_000_000, 
    min_daily_vol=500_000, 
    min_eps_growth=0, 
    max_price_earnings_ratio=50,
):
    """
    Fetch a list of stock symbols from Yahoo Finance matching specified criteria.
    
    Args:
        page_size: number of results per request (max ~250)
        pause: seconds to wait between paginated requests
        regions: list of regions (e.g., ['us'])
        exchanges: list of exchanges (e.g., ['NMS', 'NYQ'])
        sectors: list of sectors to filter
        industries: list of industries to filter (currently disabled)
        min_market_cap: minimum market capitalization
        min_daily_vol: minimum average daily volume
        min_eps_growth: minimum EPS growth over last 12 months
        max_price_earnings_ratio: maximum P/E ratio
    
    Returns:
        Sorted list of symbols meeting the criteria
    """
    all_symbols = []
    offset = 0

    # --- Build query filters ---
    sub_queries = []

    if regions:
        sub_queries.append(EquityQuery('is-in', ['region'] + regions))

    if exchanges:
        sub_queries.append(EquityQuery('is-in', ['exchange'] + exchanges))

    if sectors:
        sub_queries.append(EquityQuery('is-in', ['sector'] + sectors))

    # Industries filter is currently disabled
    # if industries:
    #     sub_queries.append(EquityQuery('is-in', ['industry'] + industries))

    if min_market_cap:
        sub_queries.append(EquityQuery('gt', ['lastclosemarketcap.lasttwelvemonths', min_market_cap]))

    if min_daily_vol:
        sub_queries.append(EquityQuery('gt', ['avgdailyvol3m', min_daily_vol]))

    if min_eps_growth or min_eps_growth == 0:
        sub_queries.append(EquityQuery('gt', ['epsgrowth.lasttwelvemonths', min_eps_growth]))

    if max_price_earnings_ratio:
        sub_queries.append(EquityQuery('lt', ['lastclosepriceearnings.lasttwelvemonths', max_price_earnings_ratio]))

    query = EquityQuery('and', sub_queries)
    print(f"Constructed Query: {query}")

    # --- Fetch paginated results from Yahoo Finance ---
    while True:
        results = screen(query=query, size=page_size, offset=offset)
        quotes = results.get("quotes", [])

        if not quotes:
            print("No more results returned.")
            break

        symbols = [q["symbol"] for q in quotes if "symbol" in q]
        all_symbols.extend(symbols)
        print(f"Fetched {len(symbols)} symbols (total so far: {len(all_symbols)})")

        offset += page_size
        time.sleep(pause)  # --- Pause to respect rate limits ---

    # --- Return sorted list of symbols ---
    all_symbols.sort()
    return all_symbols
