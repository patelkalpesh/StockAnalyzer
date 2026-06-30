"""
Kalpesh Stock Portfolio Analyzer
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import get_stock_data, score_stock, analyze_stock, compare_stocks

# ============================================================
# CONFIG
# ============================================================
PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio.json')

st.set_page_config(
    page_title="Stock Portfolio Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD/SAVE PORTFOLIO
# ============================================================
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"stocks": {}, "mutual_funds": {}}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("📈 Stock Analyzer")
page = st.sidebar.radio("Navigate", [
    "🏠 Portfolio Dashboard",
    "🔍 Analyze Stock (BUY/SELL?)",
    "⚔️ Compare Stocks",
    "➕ Add/Remove Holdings",
    "📊 Mutual Funds",
    "🔔 Alerts & Export",
])

# ============================================================
# PAGE: PORTFOLIO DASHBOARD
# ============================================================
if page == "🏠 Portfolio Dashboard":
    st.title("🏠 Portfolio Dashboard")
    
    portfolio = load_portfolio()
    stocks = portfolio.get('stocks', {})
    
    if not stocks:
        st.warning("No stocks in portfolio. Go to 'Add/Remove Holdings' to add.")
    else:
        # Fetch live data
        with st.spinner("Fetching live prices..."):
            data_rows = []
            total_invested = 0
            total_current = 0
            
            for symbol, pos in stocks.items():
                try:
                    stock_data = get_stock_data(symbol)
                    if stock_data and stock_data['cmp']:
                        cmp = stock_data['cmp']
                        invested = pos['avg_cost'] * pos['shares']
                        current = cmp * pos['shares']
                        pnl = current - invested
                        pnl_pct = (pnl / invested * 100) if invested > 0 else 0
                        total_invested += invested
                        total_current += current
                        
                        scoring = score_stock(stock_data)
                        
                        data_rows.append({
                            'Stock': pos['name'],
                            'Shares': pos['shares'],
                            'Avg Cost': pos['avg_cost'],
                            'CMP': round(cmp, 2),
                            'Invested': round(invested, 0),
                            'Current': round(current, 0),
                            'P&L (Rs)': round(pnl, 0),
                            'P&L %': round(pnl_pct, 1),
                            'Score': scoring['score'],
                            'Rating': scoring['recommendation'],
                            'P/E': round(stock_data['pe_ratio'], 1) if stock_data['pe_ratio'] else None,
                            'ROE %': round(stock_data['roe'] * 100, 1) if stock_data['roe'] else None,
                        })
                except Exception as e:
                    st.error(f"Error fetching {pos['name']}: {e}")
            
            # Summary metrics
            total_pnl = total_current - total_invested
            total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invested", f"₹{total_invested:,.0f}")
            col2.metric("Current Value", f"₹{total_current:,.0f}")
            col3.metric("Total P&L", f"₹{total_pnl:,.0f}", f"{total_pnl_pct:+.2f}%")
            col4.metric("Holdings", len(data_rows))
            
            # Table
            if data_rows:
                df = pd.DataFrame(data_rows)
                
                # Color P&L
                st.subheader("Holdings")
                st.dataframe(
                    df.style.map(
                        lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                        subset=['P&L (Rs)', 'P&L %']
                    ),
                    use_container_width=True,
                    height=450
                )
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Allocation (by Current Value)")
                    fig = px.pie(df, values='Current', names='Stock', hole=0.4)
                    fig.update_traces(textposition='inside', textinfo='label+percent')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("P&L by Stock")
                    fig = px.bar(df.sort_values('P&L (Rs)'), x='P&L (Rs)', y='Stock', 
                                orientation='h', color='P&L (Rs)',
                                color_continuous_scale=['red', 'gray', 'green'])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Score chart
                st.subheader("Stock Scores (0-100)")
                fig = px.bar(df.sort_values('Score', ascending=True), x='Score', y='Stock',
                            orientation='h', color='Rating',
                            color_discrete_map={
                                'STRONG BUY': 'darkgreen', 'BUY': 'green',
                                'HOLD': 'orange', 'SELL': 'red', 'STRONG SELL': 'darkred'
                            })
                fig.add_vline(x=60, line_dash="dash", line_color="green", annotation_text="BUY threshold")
                fig.add_vline(x=45, line_dash="dash", line_color="orange", annotation_text="HOLD threshold")
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.download_button(
                    "📥 Download as Excel (CSV)",
                    df.to_csv(index=False),
                    "portfolio_analysis.csv",
                    "text/csv"
                )

# ============================================================
# PAGE: ANALYZE STOCK
# ============================================================
elif page == "🔍 Analyze Stock (BUY/SELL?)":
    st.title("🔍 Should You BUY This Stock?")
    st.write("Enter any NSE stock symbol to get a full analysis with BUY/SELL recommendation.")
    
    symbol = st.text_input("Stock Symbol (e.g., TCS, RELIANCE, TATAMOTORS)", "").strip().upper()
    
    if st.button("🔍 Analyze", type="primary") and symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            data = analyze_stock(symbol)
            
            if not data:
                st.error(f"Could not find data for '{symbol}'. Try adding .NS suffix or check the symbol.")
            else:
                scoring = data['scoring']
                score = scoring['score']
                rec = scoring['recommendation']
                
                # Color based on recommendation
                color_map = {
                    'STRONG BUY': '🟢🟢', 'BUY': '🟢', 
                    'HOLD': '🟡', 'SELL': '🔴', 'STRONG SELL': '🔴🔴'
                }
                
                st.markdown(f"## {data['name']}")
                
                # Score display
                col1, col2, col3 = st.columns(3)
                col1.metric("Score", f"{score}/100")
                col2.metric("Recommendation", f"{color_map.get(rec, '')} {rec}")
                col3.metric("CMP", f"₹{data['cmp']:.2f}")
                
                # Key metrics
                st.subheader("Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("P/E Ratio", f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else "N/A")
                col2.metric("ROE", f"{data['roe']*100:.1f}%" if data['roe'] else "N/A")
                col3.metric("Revenue Growth", f"{data['revenue_growth']*100:.1f}%" if data['revenue_growth'] else "N/A")
                col4.metric("Debt/Equity", f"{data['debt_to_equity']:.0f}" if data['debt_to_equity'] else "N/A")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("52W High", f"₹{data['high_52w']:.2f}" if data['high_52w'] else "N/A")
                col2.metric("52W Low", f"₹{data['low_52w']:.2f}" if data['low_52w'] else "N/A")
                col3.metric("Analyst Target", f"₹{data['target_mean']:.2f}" if data['target_mean'] else "N/A")
                
                if data['target_mean'] and data['cmp']:
                    upside = (data['target_mean'] - data['cmp']) / data['cmp'] * 100
                    col4.metric("Upside", f"{upside:+.1f}%")
                
                # Score breakdown
                st.subheader("Score Breakdown")
                breakdown_df = pd.DataFrame([
                    {'Factor': k, 'Score': v, 'Max': scoring['weights'][k]}
                    for k, v in scoring['breakdown'].items()
                ])
                breakdown_df['Percentage'] = (breakdown_df['Score'] / breakdown_df['Max'] * 100).round(0)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=breakdown_df['Factor'], x=breakdown_df['Score'],
                    orientation='h', name='Score',
                    marker_color=['green' if p >= 70 else 'orange' if p >= 50 else 'red' 
                                  for p in breakdown_df['Percentage']]
                ))
                fig.add_trace(go.Bar(
                    y=breakdown_df['Factor'], x=breakdown_df['Max'] - breakdown_df['Score'],
                    orientation='h', name='Remaining',
                    marker_color='lightgray'
                ))
                fig.update_layout(barmode='stack', height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Verdict
                st.subheader("Verdict")
                if rec == 'STRONG BUY':
                    st.success(f"✅ STRONG BUY — {data['name']} scores {score}/100. Strong fundamentals, good growth, attractive valuation.")
                elif rec == 'BUY':
                    st.success(f"✅ BUY — {data['name']} scores {score}/100. Good overall with some areas to watch.")
                elif rec == 'HOLD':
                    st.warning(f"⚠️ HOLD — {data['name']} scores {score}/100. Not the best time to enter. Wait for better price.")
                elif rec == 'SELL':
                    st.error(f"❌ SELL — {data['name']} scores {score}/100. Weak fundamentals or overvalued.")
                else:
                    st.error(f"🚫 STRONG SELL — {data['name']} scores {score}/100. Avoid this stock.")

# ============================================================
# PAGE: COMPARE STOCKS
# ============================================================
elif page == "⚔️ Compare Stocks":
    st.title("⚔️ Compare Stocks")
    st.write("Compare up to 3 stocks to decide which one to buy.")
    
    col1, col2, col3 = st.columns(3)
    s1 = col1.text_input("Stock 1", "HDFCBANK").strip().upper()
    s2 = col2.text_input("Stock 2", "ICICIBANK").strip().upper()
    s3 = col3.text_input("Stock 3 (optional)", "").strip().upper()
    
    symbols = [s for s in [s1, s2, s3] if s]
    
    if st.button("⚔️ Compare", type="primary") and len(symbols) >= 2:
        with st.spinner("Fetching data..."):
            results = compare_stocks(symbols)
            
            if results:
                # Winner
                winner = results[0]
                st.success(f"🏆 Winner: **{winner['name']}** — Score {winner['scoring']['score']}/100 ({winner['scoring']['recommendation']})")
                
                # Comparison table
                compare_data = []
                for r in results:
                    s = r['scoring']
                    compare_data.append({
                        'Stock': r['name'],
                        'CMP': f"₹{r['cmp']:.2f}",
                        'Score': f"{s['score']}/100",
                        'Recommendation': s['recommendation'],
                        'P/E': f"{r['pe_ratio']:.1f}" if r['pe_ratio'] else 'N/A',
                        'ROE': f"{r['roe']*100:.1f}%" if r['roe'] else 'N/A',
                        'Revenue Growth': f"{r['revenue_growth']*100:.1f}%" if r['revenue_growth'] else 'N/A',
                        'Debt/Equity': f"{r['debt_to_equity']:.0f}" if r['debt_to_equity'] else 'N/A',
                        'Analyst Target': f"₹{r['target_mean']:.0f}" if r['target_mean'] else 'N/A',
                        'Analyst Rating': r['recommendation'],
                    })
                
                st.dataframe(pd.DataFrame(compare_data), use_container_width=True)
                
                # Score comparison chart
                fig = go.Figure()
                for r in results:
                    breakdown = r['scoring']['breakdown']
                    fig.add_trace(go.Scatterpolar(
                        r=list(breakdown.values()),
                        theta=list(breakdown.keys()),
                        fill='toself',
                        name=r['name']
                    ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 25])), height=400)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE: ADD/REMOVE HOLDINGS
# ============================================================
elif page == "➕ Add/Remove Holdings":
    st.title("➕ Manage Portfolio")
    
    portfolio = load_portfolio()
    
    tab1, tab2 = st.tabs(["Add Stock", "Remove Stock"])
    
    with tab1:
        st.subheader("Add New Stock")
        col1, col2, col3 = st.columns(3)
        new_symbol = col1.text_input("Symbol (e.g., TCS, INFY)", "").strip().upper()
        new_shares = col2.number_input("Shares", min_value=1, value=10)
        new_avg = col3.number_input("Average Buy Price (₹)", min_value=0.01, value=100.0)
        
        if st.button("➕ Add to Portfolio", type="primary") and new_symbol:
            symbol_key = new_symbol + '.NS' if not new_symbol.endswith('.NS') else new_symbol
            
            # Verify stock exists
            with st.spinner("Verifying..."):
                data = get_stock_data(symbol_key)
                if data:
                    portfolio['stocks'][symbol_key] = {
                        'name': data['name'],
                        'shares': new_shares,
                        'avg_cost': new_avg
                    }
                    save_portfolio(portfolio)
                    st.success(f"✅ Added {data['name']} ({new_shares} shares @ ₹{new_avg})")
                    st.rerun()
                else:
                    st.error(f"Could not find '{new_symbol}'. Check the symbol.")
    
    with tab2:
        st.subheader("Remove Stock")
        stocks = portfolio.get('stocks', {})
        if stocks:
            stock_to_remove = st.selectbox(
                "Select stock to remove",
                options=list(stocks.keys()),
                format_func=lambda x: f"{stocks[x]['name']} ({stocks[x]['shares']} shares)"
            )
            if st.button("🗑️ Remove", type="secondary"):
                del portfolio['stocks'][stock_to_remove]
                save_portfolio(portfolio)
                st.success("Removed!")
                st.rerun()
        else:
            st.info("No stocks to remove.")
    
    # Current holdings
    st.subheader("Current Holdings")
    if portfolio.get('stocks'):
        df = pd.DataFrame([
            {'Symbol': k.replace('.NS',''), 'Name': v['name'], 'Shares': v['shares'], 'Avg Cost': v['avg_cost']}
            for k, v in portfolio['stocks'].items()
        ])
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: MUTUAL FUNDS
# ============================================================
elif page == "📊 Mutual Funds":
    st.title("📊 Mutual Funds")
    
    portfolio = load_portfolio()
    mf = portfolio.get('mutual_funds', {})
    
    if mf:
        mf_data = []
        total_invested = 0
        total_current = 0
        
        for name, details in mf.items():
            invested = details['invested']
            current = details.get('current', invested)
            pnl = current - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0
            total_invested += invested
            total_current += current
            
            mf_data.append({
                'Fund': name,
                'Invested': invested,
                'Current': current,
                'P&L (Rs)': pnl,
                'P&L %': round(pnl_pct, 2),
            })
        
        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("MF Invested", f"₹{total_invested:,}")
        col2.metric("MF Current", f"₹{total_current:,}")
        col3.metric("MF P&L", f"₹{total_current-total_invested:,}", f"{((total_current-total_invested)/total_invested)*100:+.2f}%")
        
        st.dataframe(pd.DataFrame(mf_data), use_container_width=True)
        
        # Pie chart
        fig = px.pie(pd.DataFrame(mf_data), values='Current', names='Fund', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mutual fund data.")

# ============================================================
# PAGE: ALERTS & EXPORT
# ============================================================
elif page == "🔔 Alerts & Export":
    st.title("🔔 Price Alerts & Export")
    
    portfolio = load_portfolio()
    alerts = portfolio.get('alerts', {})
    
    tab1, tab2, tab3 = st.tabs(["Set Alerts", "Check Alerts", "Export Portfolio"])
    
    with tab1:
        st.subheader("Set Price Alert")
        st.write("Get notified when a stock reaches your target price.")
        
        col1, col2, col3 = st.columns(3)
        alert_symbol = col1.text_input("Stock Symbol", "HDFCBANK").strip().upper()
        alert_type = col2.selectbox("Alert Type", ["Above (Target)", "Below (Stop Loss)"])
        alert_price = col3.number_input("Alert Price (₹)", min_value=0.01, value=100.0)
        
        if st.button("🔔 Set Alert", type="primary") and alert_symbol:
            key = alert_symbol + '.NS' if not alert_symbol.endswith('.NS') else alert_symbol
            if 'alerts' not in portfolio:
                portfolio['alerts'] = {}
            
            portfolio['alerts'][key] = {
                'symbol': alert_symbol,
                'type': 'above' if 'Above' in alert_type else 'below',
                'price': alert_price,
                'active': True
            }
            save_portfolio(portfolio)
            st.success(f"✅ Alert set: {alert_symbol} {'above' if 'Above' in alert_type else 'below'} ₹{alert_price}")
        
        # Show existing alerts
        if alerts:
            st.subheader("Active Alerts")
            alert_rows = []
            for sym, alert in alerts.items():
                alert_rows.append({
                    'Stock': alert['symbol'],
                    'Type': '📈 Above' if alert['type'] == 'above' else '📉 Below',
                    'Target Price': f"₹{alert['price']}",
                    'Active': '✅' if alert.get('active', True) else '❌'
                })
            st.dataframe(pd.DataFrame(alert_rows), use_container_width=True)
            
            # Delete alert
            del_alert = st.selectbox("Remove alert:", list(alerts.keys()), format_func=lambda x: alerts[x]['symbol'])
            if st.button("🗑️ Remove Alert"):
                del portfolio['alerts'][del_alert]
                save_portfolio(portfolio)
                st.success("Alert removed!")
                st.rerun()
    
    with tab2:
        st.subheader("🔍 Check Alerts Now")
        st.write("Check if any of your alerts have been triggered.")
        
        if st.button("🔍 Check All Alerts", type="primary"):
            alerts = portfolio.get('alerts', {})
            if not alerts:
                st.info("No alerts set. Go to 'Set Alerts' tab to create one.")
            else:
                triggered = []
                not_triggered = []
                
                with st.spinner("Checking prices..."):
                    for sym, alert in alerts.items():
                        try:
                            data = get_stock_data(sym)
                            if data and data['cmp']:
                                cmp = data['cmp']
                                if alert['type'] == 'above' and cmp >= alert['price']:
                                    triggered.append({
                                        'Stock': alert['symbol'],
                                        'CMP': f"₹{cmp:.2f}",
                                        'Target': f"₹{alert['price']}",
                                        'Status': '🚨 TRIGGERED! Price is ABOVE target'
                                    })
                                elif alert['type'] == 'below' and cmp <= alert['price']:
                                    triggered.append({
                                        'Stock': alert['symbol'],
                                        'CMP': f"₹{cmp:.2f}",
                                        'Target': f"₹{alert['price']}",
                                        'Status': '🚨 TRIGGERED! Price is BELOW stop loss'
                                    })
                                else:
                                    diff = cmp - alert['price']
                                    pct = (diff / alert['price']) * 100
                                    not_triggered.append({
                                        'Stock': alert['symbol'],
                                        'CMP': f"₹{cmp:.2f}",
                                        'Target': f"₹{alert['price']}",
                                        'Distance': f"₹{abs(diff):.2f} ({abs(pct):.1f}%)",
                                        'Status': '⏳ Waiting'
                                    })
                        except Exception as e:
                            st.error(f"Error checking {alert['symbol']}: {e}")
                
                if triggered:
                    st.error(f"🚨 {len(triggered)} ALERT(S) TRIGGERED!")
                    st.dataframe(pd.DataFrame(triggered), use_container_width=True)
                
                if not_triggered:
                    st.info(f"⏳ {len(not_triggered)} alert(s) not yet triggered")
                    st.dataframe(pd.DataFrame(not_triggered), use_container_width=True)
        
        # Quick portfolio check against analyst targets
        st.subheader("📊 Portfolio vs Analyst Targets")
        if st.button("Check Analyst Targets for All Holdings"):
            stocks = portfolio.get('stocks', {})
            target_rows = []
            with st.spinner("Fetching targets..."):
                for sym, pos in stocks.items():
                    try:
                        data = get_stock_data(sym)
                        if data and data['cmp']:
                            target = data.get('target_mean')
                            if target:
                                upside = (target - data['cmp']) / data['cmp'] * 100
                                target_rows.append({
                                    'Stock': pos['name'],
                                    'CMP': f"₹{data['cmp']:.2f}",
                                    'Analyst Target': f"₹{target:.2f}",
                                    'Upside/Downside': f"{upside:+.1f}%",
                                    'Action': '🟢 BUY MORE' if upside > 20 else ('🟡 HOLD' if upside > 0 else '🔴 EXIT')
                                })
                            else:
                                target_rows.append({
                                    'Stock': pos['name'],
                                    'CMP': f"₹{data['cmp']:.2f}",
                                    'Analyst Target': 'No coverage',
                                    'Upside/Downside': 'N/A',
                                    'Action': '⚠️ No data'
                                })
                    except:
                        pass
            
            if target_rows:
                st.dataframe(pd.DataFrame(target_rows), use_container_width=True)
    
    with tab3:
        st.subheader("📥 Export Portfolio")
        
        portfolio = load_portfolio()
        stocks = portfolio.get('stocks', {})
        
        if st.button("📥 Generate Export", type="primary"):
            with st.spinner("Fetching latest data..."):
                export_rows = []
                for sym, pos in stocks.items():
                    try:
                        data = get_stock_data(sym)
                        if data and data['cmp']:
                            cmp = data['cmp']
                            invested = pos['avg_cost'] * pos['shares']
                            current = cmp * pos['shares']
                            pnl = current - invested
                            scoring = score_stock(data)
                            
                            export_rows.append({
                                'Stock': pos['name'],
                                'Symbol': sym.replace('.NS', ''),
                                'Shares': pos['shares'],
                                'Avg Cost': pos['avg_cost'],
                                'CMP': cmp,
                                'Invested': round(invested, 2),
                                'Current Value': round(current, 2),
                                'P&L (Rs)': round(pnl, 2),
                                'P&L (%)': round((pnl/invested)*100, 2) if invested else 0,
                                'Score': scoring['score'],
                                'Recommendation': scoring['recommendation'],
                                'P/E': data.get('pe_ratio'),
                                'ROE (%)': round(data['roe']*100, 2) if data.get('roe') else None,
                                'Revenue Growth (%)': round(data['revenue_growth']*100, 2) if data.get('revenue_growth') else None,
                                'Debt/Equity': data.get('debt_to_equity'),
                                'Analyst Target': data.get('target_mean'),
                                '52W High': data.get('high_52w'),
                                '52W Low': data.get('low_52w'),
                                'Sector': data.get('sector'),
                            })
                    except:
                        pass
                
                if export_rows:
                    df_export = pd.DataFrame(export_rows)
                    st.dataframe(df_export, use_container_width=True)
                    
                    # CSV download
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv",
                        type="primary"
                    )
                    
                    # Excel download
                    try:
                        from io import BytesIO
                        buffer = BytesIO()
                        df_export.to_excel(buffer, index=False, engine='openpyxl')
                        st.download_button(
                            "📥 Download Excel",
                            buffer.getvalue(),
                            f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except ImportError:
                        st.info("Install openpyxl for Excel export: pip install openpyxl")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built for Kalpesh | Data: Yahoo Finance")
st.sidebar.markdown("Run: `streamlit run app.py`")
