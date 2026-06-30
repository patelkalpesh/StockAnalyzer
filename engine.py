"""
Stock Analysis Engine - Scoring & Recommendation System
Scores any stock from 0-100 and gives BUY/SELL/HOLD recommendation
"""
import yfinance as yf


def get_stock_data(symbol):
    """Fetch complete stock data from Yahoo Finance with fresh prices"""
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        symbol = symbol.upper() + '.NS'
    
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    if not info or info.get('regularMarketPrice') is None:
        return None
    
    # Get the most recent price - try multiple methods
    cmp = info.get('currentPrice') or info.get('regularMarketPrice') or 0
    
    # If market is closed, get last close from history for most accurate
    if cmp == 0:
        hist = ticker.history(period='1d')
        if not hist.empty:
            cmp = hist['Close'].iloc[-1]
    
    return {
        'symbol': symbol,
        'name': info.get('shortName', symbol),
        'cmp': cmp,
        'previous_close': info.get('previousClose', 0),
        'market_cap': info.get('marketCap', 0),
        'pe_ratio': info.get('trailingPE'),
        'forward_pe': info.get('forwardPE'),
        'pb_ratio': info.get('priceToBook'),
        'eps': info.get('trailingEps'),
        'book_value': info.get('bookValue'),
        'roe': info.get('returnOnEquity'),
        'roce': info.get('returnOnAssets'),
        'debt_to_equity': info.get('debtToEquity'),
        'profit_margin': info.get('profitMargins'),
        'revenue_growth': info.get('revenueGrowth'),
        'earnings_growth': info.get('earningsGrowth'),
        'dividend_yield': info.get('dividendYield'),
        'high_52w': info.get('fiftyTwoWeekHigh'),
        'low_52w': info.get('fiftyTwoWeekLow'),
        'target_high': info.get('targetHighPrice'),
        'target_low': info.get('targetLowPrice'),
        'target_mean': info.get('targetMeanPrice'),
        'recommendation': info.get('recommendationKey', 'none'),
        'num_analysts': info.get('numberOfAnalystOpinions', 0),
        'sector': info.get('sector', ''),
        'industry': info.get('industry', ''),
        'day_high': info.get('dayHigh'),
        'day_low': info.get('dayLow'),
        'volume': info.get('volume'),
        'avg_volume': info.get('averageVolume'),
        'beta': info.get('beta'),
        'peg_ratio': info.get('pegRatio'),
    }


def score_stock(data):
    """
    Score a stock from 0-100 based on multiple factors.
    Returns score, breakdown, and recommendation.
    """
    if not data or not data.get('cmp'):
        return {'score': 0, 'recommendation': 'NO DATA', 'breakdown': {}}
    
    scores = {}
    weights = {}
    
    # 1. VALUATION (25 points)
    val_score = 0
    pe = data.get('pe_ratio')
    if pe:
        if pe < 0:
            val_score = 0  # Loss-making
        elif pe < 10:
            val_score = 25  # Very cheap
        elif pe < 15:
            val_score = 22
        elif pe < 20:
            val_score = 18
        elif pe < 25:
            val_score = 14
        elif pe < 35:
            val_score = 10
        elif pe < 50:
            val_score = 5
        else:
            val_score = 2  # Very expensive
    
    # Bonus for forward PE < trailing PE (earnings improving)
    fwd_pe = data.get('forward_pe')
    if pe and fwd_pe and fwd_pe < pe:
        val_score = min(25, val_score + 3)
    
    scores['Valuation (P/E)'] = val_score
    weights['Valuation (P/E)'] = 25
    
    # 2. PROFITABILITY (20 points)
    prof_score = 0
    roe = data.get('roe')
    if roe:
        if roe < 0:
            prof_score = 0
        elif roe > 0.25:
            prof_score = 20
        elif roe > 0.20:
            prof_score = 17
        elif roe > 0.15:
            prof_score = 14
        elif roe > 0.10:
            prof_score = 10
        elif roe > 0.05:
            prof_score = 6
        else:
            prof_score = 3
    
    scores['Profitability (ROE)'] = prof_score
    weights['Profitability (ROE)'] = 20
    
    # 3. GROWTH (20 points)
    growth_score = 0
    rev_growth = data.get('revenue_growth')
    earn_growth = data.get('earnings_growth')
    
    if rev_growth:
        if rev_growth > 0.30:
            growth_score += 10
        elif rev_growth > 0.15:
            growth_score += 8
        elif rev_growth > 0.05:
            growth_score += 5
        elif rev_growth > 0:
            growth_score += 3
        else:
            growth_score += 0
    
    if earn_growth:
        if earn_growth > 0.30:
            growth_score += 10
        elif earn_growth > 0.15:
            growth_score += 8
        elif earn_growth > 0.05:
            growth_score += 5
        elif earn_growth > 0:
            growth_score += 3
        else:
            growth_score += 0
    
    scores['Growth'] = min(20, growth_score)
    weights['Growth'] = 20
    
    # 4. FINANCIAL HEALTH (15 points)
    health_score = 0
    debt_eq = data.get('debt_to_equity')
    if debt_eq is not None:
        if debt_eq < 10:
            health_score = 15
        elif debt_eq < 30:
            health_score = 12
        elif debt_eq < 50:
            health_score = 10
        elif debt_eq < 100:
            health_score = 7
        elif debt_eq < 200:
            health_score = 4
        else:
            health_score = 2
    else:
        health_score = 8  # Unknown, give average
    
    # Profit margin bonus
    pm = data.get('profit_margin')
    if pm and pm > 0.15:
        health_score = min(15, health_score + 2)
    
    scores['Financial Health'] = health_score
    weights['Financial Health'] = 15
    
    # 5. ANALYST SENTIMENT (10 points)
    analyst_score = 0
    rec = data.get('recommendation', 'none')
    if rec == 'strong_buy':
        analyst_score = 10
    elif rec == 'buy':
        analyst_score = 8
    elif rec == 'hold':
        analyst_score = 5
    elif rec == 'sell':
        analyst_score = 2
    elif rec == 'strong_sell':
        analyst_score = 0
    else:
        analyst_score = 5  # No coverage, neutral
    
    # Upside to target
    target = data.get('target_mean')
    cmp = data.get('cmp')
    if target and cmp and target > cmp:
        upside = (target - cmp) / cmp * 100
        if upside > 30:
            analyst_score = min(10, analyst_score + 2)
    
    scores['Analyst Sentiment'] = analyst_score
    weights['Analyst Sentiment'] = 10
    
    # 6. TECHNICAL POSITION (10 points)
    tech_score = 5  # Default neutral
    high52 = data.get('high_52w')
    low52 = data.get('low_52w')
    if high52 and low52 and cmp:
        # Where is price in 52W range? (0% = at low, 100% = at high)
        range_position = (cmp - low52) / (high52 - low52) * 100 if (high52 - low52) > 0 else 50
        
        if range_position < 20:
            tech_score = 9  # Near 52W low = potential value
        elif range_position < 40:
            tech_score = 8
        elif range_position < 60:
            tech_score = 6
        elif range_position < 80:
            tech_score = 4
        else:
            tech_score = 2  # Near 52W high = risky entry
    
    scores['Technical Position'] = tech_score
    weights['Technical Position'] = 10
    
    # TOTAL SCORE
    total_score = sum(scores.values())
    
    # RECOMMENDATION
    if total_score >= 75:
        recommendation = 'STRONG BUY'
    elif total_score >= 60:
        recommendation = 'BUY'
    elif total_score >= 45:
        recommendation = 'HOLD'
    elif total_score >= 30:
        recommendation = 'SELL'
    else:
        recommendation = 'STRONG SELL'
    
    # Override: loss-making company can't be above HOLD
    if pe and pe < 0:
        recommendation = 'SELL' if total_score > 30 else 'STRONG SELL'
    if roe and roe < 0:
        if recommendation in ('STRONG BUY', 'BUY'):
            recommendation = 'HOLD'
    
    return {
        'score': total_score,
        'max_score': 100,
        'recommendation': recommendation,
        'breakdown': scores,
        'weights': weights,
    }


def analyze_stock(symbol):
    """Complete analysis of a stock - data + score + recommendation"""
    data = get_stock_data(symbol)
    if not data:
        return None
    
    scoring = score_stock(data)
    data['scoring'] = scoring
    return data


def compare_stocks(symbols):
    """Compare multiple stocks side by side"""
    results = []
    for sym in symbols:
        analysis = analyze_stock(sym)
        if analysis:
            results.append(analysis)
    return sorted(results, key=lambda x: x['scoring']['score'], reverse=True)


def format_analysis(data):
    """Format analysis result as readable text"""
    if not data:
        return "No data found for this stock."
    
    scoring = data['scoring']
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  {data['name']} ({data['symbol'].replace('.NS','')})")
    lines.append(f"{'='*60}")
    lines.append(f"  CMP: Rs {data['cmp']:.2f}")
    lines.append(f"  52W Range: Rs {data.get('low_52w','N/A')} - Rs {data.get('high_52w','N/A')}")
    lines.append(f"  Market Cap: Rs {data['market_cap']/10000000:,.0f} Cr")
    lines.append(f"")
    pe_str = f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else 'N/A'
    roe_str = f"{data['roe']*100:.1f}%" if data['roe'] else 'N/A'
    de_str = str(data.get('debt_to_equity', 'N/A'))
    lines.append(f"  P/E: {pe_str} | ROE: {roe_str} | D/E: {de_str}")
    rev_str = f"{data['revenue_growth']*100:.1f}%" if data['revenue_growth'] else 'N/A'
    earn_str = f"{data['earnings_growth']*100:.1f}%" if data['earnings_growth'] else 'N/A'
    lines.append(f"  Rev Growth: {rev_str} | Earn Growth: {earn_str}")
    lines.append(f"  Analyst Target: Rs {data.get('target_mean','N/A')} | Rating: {data.get('recommendation','N/A')}")
    lines.append(f"")
    lines.append(f"  {'─'*40}")
    lines.append(f"  SCORE: {scoring['score']}/100  |  {scoring['recommendation']}")
    lines.append(f"  {'─'*40}")
    lines.append(f"  Breakdown:")
    for factor, score in scoring['breakdown'].items():
        max_s = scoring['weights'][factor]
        bar = '█' * int(score/max_s * 10) + '░' * (10 - int(score/max_s * 10))
        lines.append(f"    {factor:<25} {bar} {score}/{max_s}")
    lines.append(f"{'='*60}")
    
    return '\n'.join(lines)
