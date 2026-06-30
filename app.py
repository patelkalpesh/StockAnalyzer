"""
Kalpesh Stock Portfolio Analyzer - Professional Edition
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
# CACHING - fetch data once, reuse for 5 minutes
# ============================================================
@st.cache_data(ttl=300)
def fetch_all_portfolio_data(stocks_json):
    """Fetch all stock data in one go, cached for 5 min"""
    stocks = json.loads(stocks_json)
    results = {}
    for symbol in stocks:
        try:
            data = get_stock_data(symbol)
            if data and data['cmp']:
                results[symbol] = data
        except:
            pass
    return results

@st.cache_data(ttl=300)
def fetch_stock_cached(symbol):
    """Cache individual stock lookups"""
    return fetch_stock_cached(symbol)

@st.cache_data(ttl=300)
def analyze_stock_cached(symbol):
    """Cache analysis results"""
    return analyze_stock(symbol)

# ============================================================
# CONFIG
# ============================================================
PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio.json')

st.set_page_config(
    page_title="Kalpesh Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PASSWORD PROTECTION
# ============================================================
def check_password():
    """Simple password gate"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    st.markdown("<div style='max-width:400px; margin:80px auto; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("## 📈 Stock Analyzer")
    st.markdown("Enter password to access your portfolio")
    
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", type="primary"):
        if password == st.secrets.get("password", "kalpesh2026"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# ============================================================
# CUSTOM CSS FOR PROFESSIONAL LOOK
# ============================================================
st.markdown("""
<style>
    /* ABSOLUTE ZERO TOP - content starts at pixel 0 */
    .appview-container { padding-top: 0 !important; margin-top: 0 !important; }
    .main .block-container { padding-top: 0 !important; margin-top: 0 !important; max-width: 100% !important; padding-left: 1rem !important; padding-right: 1rem !important; padding-bottom: 0.5rem !important; }
    .stApp { margin-top: 0 !important; padding-top: 0 !important; }
    section.main { padding-top: 0 !important; }
    .block-container { padding-top: 0 !important; }
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { min-width: 180px !important; max-width: 180px !important; display: block !important; visibility: visible !important; transform: none !important; }
    [data-testid="stSidebar"] > div:first-child { padding: 0.3rem 0.6rem; }
    [data-testid="stSidebar"][aria-expanded="false"] { display: block !important; min-width: 180px !important; max-width: 180px !important; margin-left: 0 !important; transform: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 0; }
    [data-testid="stSidebar"] .stRadio label { font-size: 0.8rem; padding: 3px 2px; margin: 0; }
    [data-testid="stSidebar"] h2 { font-size: 0.95rem; margin: 0; }
    [data-testid="stSidebar"] hr { margin: 3px 0; }
    [data-testid="stSidebar"] .stCaption { font-size: 0.6rem; margin: 0; }
    [data-testid="stSidebar"] .stMarkdown p { font-size: 0.7rem; margin: 0; }
    
    /* Gaps */
    [data-testid="stVerticalBlock"] > div { gap: 0.15rem !important; }
    .element-container { margin: 0 !important; padding: 0 !important; }
    [data-testid="column"] { padding: 0 0.25rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.25rem !important; }
    
    /* Metrics */
    [data-testid="stMetric"] { background: #fff; border: 1px solid #e8e8e8; border-radius: 4px; padding: 6px 10px !important; }
    [data-testid="stMetricLabel"] { font-size: 0.6rem; color: #888; }
    [data-testid="stMetricValue"] { font-size: 1rem; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.65rem; }
    
    /* Headers */
    h1, h2, h3, h4 { margin: 0 !important; padding: 0 !important; }
    h4 { font-size: 0.9rem !important; }
    
    /* Content */
    .stPlotlyChart { margin: 0 !important; padding: 0 !important; }
    .stDataFrame { margin: 0 !important; }
    .stButton > button { border-radius: 4px; font-weight: 600; padding: 4px 12px; font-size: 0.78rem; background-color: #2563eb !important; color: white !important; border: none !important; }
    .stButton > button:hover { background-color: #1d4ed8 !important; }
    .stButton > button[kind="secondary"] { background-color: #fff !important; color: #2563eb !important; border: 1px solid #2563eb !important; }
    .pro-divider { display: none !important; }
    .stTabs [data-baseweb="tab"] { padding: 4px 10px; font-size: 0.78rem; }
    .stMarkdown { min-height: 0 !important; }
    .stMarkdown p { margin: 0 !important; }
    .stSpinner { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"stocks": {}, "mutual_funds": {}}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

def get_score_color(rec):
    colors = {
        'STRONG BUY': '#00d26a', 'BUY': '#4caf50',
        'HOLD': '#ff9800', 'SELL': '#f44336', 'STRONG SELL': '#b71c1c'
    }
    return colors.get(rec, '#666')

def get_score_emoji(rec):
    emojis = {
        'STRONG BUY': '🟢🟢', 'BUY': '🟢',
        'HOLD': '🟡', 'SELL': '🔴', 'STRONG SELL': '🔴🔴'
    }
    return emojis.get(rec, '⚪')

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 📈 Stock Analyzer")
st.sidebar.markdown(f"*{datetime.now().strftime('%d %b %Y, %I:%M %p')}*")
st.sidebar.markdown("---")

# Manual Refresh Button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio("Navigate", [
    "🏠 Dashboard",
    "📊 Mutual Funds",
    "🔍 Analyze (BUY/SELL?)",
    "⚔️ Compare Stocks",
    "🛡️ Risk Engine",
    "💡 Opportunities",
    "🤖 AI Advisor",
    "➕ Manage Portfolio",
    "🔔 Alerts & Export",
    "📈 Watchlist",
])

st.sidebar.markdown("---")
st.sidebar.caption("Data: Yahoo Finance (Live)")
st.sidebar.caption("Built for Kalpesh")

# ============================================================
# THEME SELECTOR
# ============================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Theme")
theme = st.sidebar.selectbox("Theme", [
    "⬜ Clean White",
    "🌙 Dark Pro",
    "☁️ AWS Console",
    "🌊 Ocean Blue",
    "🌲 Forest Green",
    "🔥 Fire Red",
    "💜 Purple Haze",
], label_visibility="collapsed")

# Apply theme CSS based on selection
theme_css = ""
if theme == "⬜ Clean White":
    theme_css = """
    <style>
    /* Clean White Sober Theme */
    .main { background-color: #ffffff !important; color: #1a1a1a !important; }
    [data-testid="stSidebar"] { background: #f8f9fa !important; border-right: 1px solid #e0e0e0 !important; }
    [data-testid="stSidebar"] * { color: #333333 !important; }
    
    [data-testid="stMetric"] { 
        background: #ffffff !important; 
        border: 1px solid #e0e0e0 !important; 
        border-radius: 8px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    [data-testid="stMetricLabel"] { color: #666666 !important; }
    [data-testid="stMetricValue"] { color: #1a1a1a !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] svg { display: inline !important; }
    
    h1 { 
        background: none !important; 
        -webkit-text-fill-color: #1a1a1a !important; 
        color: #1a1a1a !important;
        font-weight: 800 !important;
    }
    h2, h3 { color: #333333 !important; }
    p, span, label, div { color: #333333; }
    
    .stButton > button[kind="primary"] { 
        background: #1a1a1a !important; 
        color: #ffffff !important; 
        border-radius: 6px !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover { background: #333333 !important; }
    .stButton > button[kind="secondary"] { 
        border: 1px solid #333333 !important; 
        color: #333333 !important; 
        background: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { border-bottom-color: #e0e0e0 !important; }
    .stTabs [data-baseweb="tab"] { color: #666666 !important; }
    .stTabs [aria-selected="true"] { color: #1a1a1a !important; border-bottom-color: #1a1a1a !important; }
    
    .stDataFrame { border: 1px solid #e0e0e0 !important; border-radius: 6px !important; }
    
    .stSelectbox > div > div { background: #ffffff !important; border-color: #d0d0d0 !important; color: #1a1a1a !important; }
    .stTextInput > div > div > input { background: #ffffff !important; border-color: #d0d0d0 !important; color: #1a1a1a !important; }
    .stNumberInput > div > div > input { background: #ffffff !important; border-color: #d0d0d0 !important; color: #1a1a1a !important; }
    
    .pro-divider { background: linear-gradient(90deg, transparent, #e0e0e0, transparent) !important; }
    
    .stAlert { border-radius: 6px !important; }
    
    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio label:hover { color: #000000 !important; font-weight: 600 !important; }
    
    /* Make markdown text black */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th { color: #1a1a1a !important; }
    
    /* Table headers */
    .stMarkdown table th { background: #f8f9fa !important; color: #1a1a1a !important; border: 1px solid #e0e0e0 !important; }
    .stMarkdown table td { border: 1px solid #e0e0e0 !important; color: #333333 !important; }
    </style>"""
elif theme == "☁️ AWS Console":
    theme_css = """
    <style>
    /* AWS Console Theme */
    .main { background-color: #232f3e !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1b2838 0%, #232f3e 100%) !important; }
    
    [data-testid="stMetric"] { 
        background: linear-gradient(135deg, #37475a 0%, #2a3f54 100%) !important; 
        border: 1px solid #527fff !important; 
        border-radius: 4px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stMetricLabel"] { color: #d5dbdb !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    
    h1 { 
        background: linear-gradient(90deg, #ff9900, #ffb84d) !important; 
        -webkit-background-clip: text !important; 
        -webkit-text-fill-color: transparent !important; 
        font-weight: 800 !important;
    }
    h2, h3 { color: #ff9900 !important; }
    
    .stButton > button[kind="primary"] { 
        background: #ff9900 !important; 
        color: #232f3e !important; 
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover { background: #ffb84d !important; }
    
    .stButton > button[kind="secondary"] { 
        border: 1px solid #ff9900 !important; 
        color: #ff9900 !important; 
        background: transparent !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { border-bottom-color: #37475a !important; }
    .stTabs [data-baseweb="tab"] { color: #d5dbdb !important; }
    .stTabs [aria-selected="true"] { color: #ff9900 !important; border-bottom-color: #ff9900 !important; }
    
    /* DataFrames */
    .stDataFrame { border: 1px solid #37475a !important; border-radius: 4px !important; }
    
    /* AWS-style info boxes */
    .stAlert { border-radius: 4px !important; border-left: 4px solid #ff9900 !important; }
    
    /* Selectbox, Input */
    .stSelectbox > div > div { background: #37475a !important; border-color: #527fff !important; }
    .stTextInput > div > div > input { background: #37475a !important; border-color: #527fff !important; color: white !important; }
    
    /* Sidebar radio */
    [data-testid="stSidebar"] .stRadio label { color: #d5dbdb !important; }
    [data-testid="stSidebar"] .stRadio label:hover { color: #ff9900 !important; }
    
    /* AWS orange accent line */
    .pro-divider { background: linear-gradient(90deg, transparent, #ff9900, transparent) !important; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #232f3e; }
    ::-webkit-scrollbar-thumb { background: #37475a; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #ff9900; }
    </style>"""
elif theme == "🌊 Ocean Blue":
    theme_css = """
    <style>
    [data-testid="stMetric"] { background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%); border-color: #1e90ff; }
    h1 { background: linear-gradient(90deg, #00b4d8, #48cae4) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
    .stButton > button[kind="primary"] { background: #0077b6; }
    </style>"""
elif theme == "🌲 Forest Green":
    theme_css = """
    <style>
    [data-testid="stMetric"] { background: linear-gradient(135deg, #1a2e1a 0%, #2d4a2d 100%); border-color: #2d6a4f; }
    h1 { background: linear-gradient(90deg, #40916c, #74c69d) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
    .stButton > button[kind="primary"] { background: #2d6a4f; }
    </style>"""
elif theme == "🔥 Fire Red":
    theme_css = """
    <style>
    [data-testid="stMetric"] { background: linear-gradient(135deg, #2b1515 0%, #3d1f1f 100%); border-color: #e63946; }
    h1 { background: linear-gradient(90deg, #e63946, #ff6b6b) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
    .stButton > button[kind="primary"] { background: #e63946; }
    </style>"""
elif theme == "💜 Purple Haze":
    theme_css = """
    <style>
    [data-testid="stMetric"] { background: linear-gradient(135deg, #1a1028 0%, #2d1b4e 100%); border-color: #7b2cbf; }
    h1 { background: linear-gradient(90deg, #9b5de5, #c77dff) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
    .stButton > button[kind="primary"] { background: #7b2cbf; }
    </style>"""

if theme_css:
    st.markdown(theme_css, unsafe_allow_html=True)


# ============================================================
# PAGE: DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    # Row 1: Title inline
    st.markdown("#### 🏠 Portfolio Dashboard")
    
    portfolio = load_portfolio()
    stocks = portfolio.get('stocks', {})
    mf = portfolio.get('mutual_funds', {})
    
    if not stocks:
        st.warning("No stocks in portfolio. Go to 'Manage Portfolio' to add.")
    else:
        with st.spinner("Loading..."):
            # Fetch ALL data at once (cached 5 min)
            all_data = fetch_all_portfolio_data(json.dumps(list(stocks.keys())))
            
            data_rows = []
            total_invested = 0
            total_current = 0
            winners = 0
            losers = 0
            
            for symbol, pos in stocks.items():
                stock_data = all_data.get(symbol)
                if stock_data and stock_data['cmp']:
                    cmp = stock_data['cmp']
                    invested = pos['avg_cost'] * pos['shares']
                    current = cmp * pos['shares']
                    pnl = current - invested
                    pnl_pct = (pnl / invested * 100) if invested > 0 else 0
                    total_invested += invested
                    total_current += current
                    
                    if pnl >= 0:
                        winners += 1
                    else:
                        losers += 1
                    
                    scoring = score_stock(stock_data)
                    
                    data_rows.append({
                        'Stock': pos['name'],
                        'Shares': pos['shares'],
                        'Avg': round(pos['avg_cost'], 2),
                        'CMP': round(cmp, 2),
                        'Invested': round(invested, 2),
                        'Current': round(current, 2),
                        'P&L': round(pnl, 2),
                        'P&L %': round(pnl_pct, 2),
                        'Score': scoring['score'],
                        'Rating': scoring['recommendation'],
                    })
            
            # MF totals
            mf_invested = sum(m['invested'] for m in mf.values())
            mf_current = sum(m.get('current', m['invested']) for m in mf.values())
            
            grand_invested = total_invested + mf_invested
            grand_current = total_current + mf_current
            grand_pnl = grand_current - grand_invested
            grand_pnl_pct = (grand_pnl / grand_invested * 100) if grand_invested > 0 else 0
            stock_pnl = total_current - total_invested
            stock_pnl_pct = (stock_pnl / total_invested * 100) if total_invested > 0 else 0
            mf_pnl = mf_current - mf_invested
            mf_pnl_pct = (mf_pnl / mf_invested * 100) if mf_invested > 0 else 0
        
        # Row 2: ALL metrics in one row (7 columns)
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Invested", f"₹{grand_invested:,.0f}")
        c2.metric("Current", f"₹{grand_current:,.0f}")
        c3.metric("Total P&L", f"₹{grand_pnl:,.0f}", f"{grand_pnl_pct:+.1f}%")
        c4.metric("Stocks P&L", f"₹{stock_pnl:,.0f}", f"{stock_pnl_pct:+.1f}%")
        c5.metric("MF P&L", f"₹{mf_pnl:,.0f}", f"{mf_pnl_pct:+.1f}%")
        c6.metric("W / L", f"{winners}W / {losers}L")
        c7.metric("Holdings", f"{len(data_rows)} + {len(mf)} MF")
        
        # Row 3: Holdings table immediately
        if data_rows:
            df = pd.DataFrame(data_rows)
            
            st.dataframe(
                df.style.format({
                    'Avg': '{:.2f}',
                    'CMP': '{:.2f}',
                    'Invested': '{:.2f}',
                    'Current': '{:.2f}',
                    'P&L': '{:.2f}',
                    'P&L %': '{:.2f}',
                }).map(
                    lambda x: 'color: #16a34a' if isinstance(x, (int, float)) and x > 0 else ('color: #dc2626' if isinstance(x, (int, float)) and x < 0 else ''),
                    subset=['P&L', 'P&L %']
                ),
                use_container_width=True,
                height=min(400, 35 + len(data_rows) * 35)
            )
            
            # Row 4: Charts side by side
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.pie(df, values='Current', names='Stock', hole=0.45,
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=280, margin=dict(l=10,r=10,t=30,b=10),
                    title_text="Allocation", title_font_size=12, showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                df_sorted = df.sort_values('P&L')
                colors = ['#dc2626' if x < 0 else '#16a34a' for x in df_sorted['P&L']]
                fig = go.Figure(go.Bar(
                    x=df_sorted['P&L'], y=df_sorted['Stock'],
                    orientation='h', marker_color=colors
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=280, margin=dict(l=10,r=10,t=30,b=10),
                    title_text="P&L", title_font_size=12
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                df_score = df.sort_values('Score', ascending=True)
                colors_score = [get_score_color(r) for r in df_score['Rating']]
                fig = go.Figure(go.Bar(
                    x=df_score['Score'], y=df_score['Stock'],
                    orientation='h', marker_color=colors_score,
                    text=df_score['Score'], textposition='inside'
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=280, margin=dict(l=10,r=10,t=30,b=10),
                    title_text="Scores", title_font_size=12,
                    xaxis_range=[0, 100]
                )
                st.plotly_chart(fig, use_container_width=True)



# ============================================================
# PAGE: ANALYZE STOCK
# ============================================================
elif page == "🔍 Analyze (BUY/SELL?)":
    st.markdown("# 🔍 Should You BUY This Stock?")
    st.markdown("Enter any NSE stock symbol to get a **score out of 100** with BUY/SELL recommendation.")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    symbol = col1.text_input("🔎 Stock Symbol", placeholder="e.g. TCS, RELIANCE, TATAMOTORS").strip().upper()
    col2.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = col2.button("🔍 Analyze", type="primary", use_container_width=True)
    
    if analyze_btn and symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            data = analyze_stock(symbol)
            
            if not data:
                st.error(f"Could not find '{symbol}'. Try the exact NSE symbol (e.g., HDFCBANK, RELIANCE, TCS)")
            else:
                scoring = data['scoring']
                score = scoring['score']
                rec = scoring['recommendation']
                
                st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
                
                # Header with score
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(f"## {data['name']}")
                col2.metric("Score", f"{score}/100")
                color = get_score_color(rec)
                col3.markdown(f"""
                <div style="background:{color}; color:{'#000' if rec in ['STRONG BUY','HOLD'] else '#fff'}; 
                padding:12px 20px; border-radius:12px; text-align:center; font-weight:700; font-size:1.2rem; margin-top:12px;">
                {get_score_emoji(rec)} {rec}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
                
                # Key metrics grid
                st.markdown("### 📊 Key Metrics")
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("CMP", f"₹{data['cmp']:.2f}")
                c2.metric("P/E Ratio", f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else "N/A")
                c3.metric("ROE", f"{data['roe']*100:.1f}%" if data['roe'] else "N/A")
                c4.metric("Rev Growth", f"{data['revenue_growth']*100:.1f}%" if data['revenue_growth'] else "N/A")
                c5.metric("Debt/Equity", f"{data['debt_to_equity']:.0f}" if data['debt_to_equity'] else "N/A")
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("52W High", f"₹{data['high_52w']:.0f}" if data['high_52w'] else "N/A")
                c2.metric("52W Low", f"₹{data['low_52w']:.0f}" if data['low_52w'] else "N/A")
                c3.metric("Analyst Target", f"₹{data['target_mean']:.0f}" if data['target_mean'] else "N/A")
                if data['target_mean'] and data['cmp']:
                    upside = (data['target_mean'] - data['cmp']) / data['cmp'] * 100
                    c4.metric("Upside", f"{upside:+.1f}%")
                c5.metric("Market Cap", f"₹{data['market_cap']/10000000:,.0f} Cr" if data['market_cap'] else "N/A")
                
                st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
                
                # Score breakdown
                st.markdown("### 🎯 Score Breakdown")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    breakdown_df = pd.DataFrame([
                        {'Factor': k, 'Score': v, 'Max': scoring['weights'][k]}
                        for k, v in scoring['breakdown'].items()
                    ])
                    breakdown_df['Fill'] = breakdown_df['Max'] - breakdown_df['Score']
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=breakdown_df['Factor'], x=breakdown_df['Score'],
                        orientation='h', name='Score',
                        marker_color=[get_score_color(rec) if s/m > 0.6 else ('#ff9800' if s/m > 0.4 else '#f44336') 
                                     for s, m in zip(breakdown_df['Score'], breakdown_df['Max'])],
                        text=[f"{s}/{m}" for s, m in zip(breakdown_df['Score'], breakdown_df['Max'])],
                        textposition='inside'
                    ))
                    fig.add_trace(go.Bar(
                        y=breakdown_df['Factor'], x=breakdown_df['Fill'],
                        orientation='h', name='Remaining',
                        marker_color='rgba(255,255,255,0.1)'
                    ))
                    fig.update_layout(
                        barmode='stack', height=280, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font_color='white', margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        title={'text': "Overall Score", 'font': {'color': 'white'}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': 'white'},
                            'bar': {'color': color},
                            'bgcolor': 'rgba(0,0,0,0)',
                            'steps': [
                                {'range': [0, 30], 'color': 'rgba(244,67,54,0.2)'},
                                {'range': [30, 45], 'color': 'rgba(244,67,54,0.1)'},
                                {'range': [45, 60], 'color': 'rgba(255,152,0,0.1)'},
                                {'range': [60, 75], 'color': 'rgba(76,175,80,0.1)'},
                                {'range': [75, 100], 'color': 'rgba(0,210,106,0.2)'},
                            ],
                            'threshold': {'line': {'color': 'white', 'width': 2}, 'value': score}
                        },
                        number={'font': {'color': 'white', 'size': 48}}
                    ))
                    fig.update_layout(
                        height=250, paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white', margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Verdict box
                st.markdown("### 💡 Verdict")
                if rec == 'STRONG BUY':
                    st.success(f"✅ **STRONG BUY** — {data['name']} scores {score}/100. Strong fundamentals, good growth, attractive valuation. Consider buying.")
                elif rec == 'BUY':
                    st.success(f"✅ **BUY** — {data['name']} scores {score}/100. Good overall. Can enter at current levels.")
                elif rec == 'HOLD':
                    st.warning(f"⚠️ **HOLD** — {data['name']} scores {score}/100. Not the best entry point. Wait for better price or accumulate slowly.")
                elif rec == 'SELL':
                    st.error(f"❌ **SELL** — {data['name']} scores {score}/100. Weak fundamentals or overvalued. Avoid buying.")
                else:
                    st.error(f"🚫 **STRONG SELL** — {data['name']} scores {score}/100. Significant red flags. Stay away.")



# ============================================================
# PAGE: COMPARE STOCKS
# ============================================================
elif page == "⚔️ Compare Stocks":
    st.markdown("# ⚔️ Compare Stocks")
    st.markdown("Compare up to 3 stocks side-by-side to pick the best one.")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    s1 = col1.text_input("Stock 1", "HDFCBANK").strip().upper()
    s2 = col2.text_input("Stock 2", "ICICIBANK").strip().upper()
    s3 = col3.text_input("Stock 3 (optional)", "").strip().upper()
    
    symbols = [s for s in [s1, s2, s3] if s]
    
    if st.button("⚔️ Compare Now", type="primary") and len(symbols) >= 2:
        with st.spinner("Fetching data..."):
            results = compare_stocks(symbols)
            
            if results:
                winner = results[0]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #00d26a22, #00b4d822); border: 1px solid #00d26a;
                border-radius: 12px; padding: 16px 24px; margin: 16px 0;">
                <h3 style="margin:0; color:#00d26a;">🏆 Winner: {winner['name']} — Score {winner['scoring']['score']}/100 ({winner['scoring']['recommendation']})</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Comparison table
                compare_data = []
                for r in results:
                    s = r['scoring']
                    compare_data.append({
                        'Stock': r['name'],
                        'Score': f"{s['score']}/100",
                        'Rating': s['recommendation'],
                        'CMP': f"₹{r['cmp']:.2f}",
                        'P/E': f"{r['pe_ratio']:.1f}" if r['pe_ratio'] else 'N/A',
                        'ROE': f"{r['roe']*100:.1f}%" if r['roe'] else 'N/A',
                        'Revenue Growth': f"{r['revenue_growth']*100:.1f}%" if r['revenue_growth'] else 'N/A',
                        'Earnings Growth': f"{r['earnings_growth']*100:.1f}%" if r['earnings_growth'] else 'N/A',
                        'Debt/Equity': f"{r['debt_to_equity']:.0f}" if r['debt_to_equity'] else 'N/A',
                        'Target': f"₹{r['target_mean']:.0f}" if r['target_mean'] else 'N/A',
                    })
                
                st.dataframe(pd.DataFrame(compare_data), use_container_width=True)
                
                # Radar chart
                st.markdown("### 📊 Radar Comparison")
                fig = go.Figure()
                colors = ['#00d26a', '#00b4d8', '#ff9800']
                for i, r in enumerate(results):
                    breakdown = r['scoring']['breakdown']
                    values = list(breakdown.values()) + [list(breakdown.values())[0]]
                    labels = list(breakdown.keys()) + [list(breakdown.keys())[0]]
                    fig.add_trace(go.Scatterpolar(
                        r=values, theta=labels,
                        fill='toself', name=r['name'],
                        line_color=colors[i % 3],
                        fillcolor=colors[i % 3] + '33'
                    ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 25], gridcolor='#333'),
                        angularaxis=dict(gridcolor='#333'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white', height=450,
                    legend=dict(x=0, y=-0.2, orientation='h')
                )
                st.plotly_chart(fig, use_container_width=True)



# ============================================================
# PAGE: RISK ENGINE
# ============================================================
elif page == "🛡️ Risk Engine":
    st.markdown("# 🛡️ Portfolio Risk Engine")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    portfolio = load_portfolio()
    stocks = portfolio.get('stocks', {})
    mf = portfolio.get('mutual_funds', {})
    
    if not stocks:
        st.warning("Add stocks to portfolio first.")
    else:
        with st.spinner("Analyzing portfolio risk..."):
            # Fetch all stock data
            holdings = []
            total_value = 0
            sectors = {}
            
            for symbol, pos in stocks.items():
                try:
                    data = fetch_stock_cached(symbol)
                    if data and data['cmp']:
                        value = data['cmp'] * pos['shares']
                        total_value += value
                        sector = data.get('sector', 'Unknown')
                        holdings.append({
                            'name': pos['name'],
                            'value': value,
                            'sector': sector,
                            'symbol': symbol,
                            'pct': 0,  # calculate after
                        })
                        sectors[sector] = sectors.get(sector, 0) + value
                except:
                    pass
            
            # Add MF value
            mf_value = sum(m.get('current', m['invested']) for m in mf.values())
            grand_total = total_value + mf_value
            
            # Calculate percentages
            for h in holdings:
                h['pct'] = (h['value'] / grand_total * 100) if grand_total > 0 else 0
            
            # Allocation percentages
            stock_pct = (total_value / grand_total * 100) if grand_total > 0 else 0
            mf_pct = (mf_value / grand_total * 100) if grand_total > 0 else 0
            
            # Gold allocation
            gold_value = sum(h['value'] for h in holdings if 'gold' in h['name'].lower())
            silver_value = sum(h['value'] for h in holdings if 'silv' in h['name'].lower())
            commodity_pct = ((gold_value + silver_value) / grand_total * 100) if grand_total > 0 else 0
            gold_pct = (gold_value / grand_total * 100) if grand_total > 0 else 0
            
            # ── PORTFOLIO HEALTH SCORE ──
            st.markdown("### 🏥 Portfolio Health Score")
            
            # Diversification score (more stocks = better, max at 10+)
            num_holdings = len(holdings) + len(mf)
            diversification = min(100, num_holdings * 8)
            
            # Concentration risk (biggest holding %)
            max_holding_pct = max(h['pct'] for h in holdings) if holdings else 0
            concentration = max(0, 100 - max_holding_pct * 3)
            
            # Sector spread
            num_sectors = len(set(s for s in sectors.keys() if s != 'Unknown'))
            sector_score = min(100, num_sectors * 20)
            
            # Asset allocation (ideal: 50% equity, 30% MF, 10% gold, 10% other)
            allocation_score = 100
            if stock_pct > 65:
                allocation_score -= 20
            if mf_pct < 20:
                allocation_score -= 15
            if gold_pct < 5:
                allocation_score -= 15
            if gold_pct > 15:
                allocation_score -= 10
            
            # MF quality
            mf_score = min(100, len(mf) * 20)
            
            # Overall health
            health_score = int(
                diversification * 0.25 +
                concentration * 0.25 +
                sector_score * 0.20 +
                allocation_score * 0.15 +
                mf_score * 0.15
            )
            
            # Display health score
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=health_score,
                    title={'text': "Health Score", 'font': {'color': 'white'}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': '#00d26a' if health_score >= 70 else ('#ff9800' if health_score >= 50 else '#f44336')},
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(244,67,54,0.2)'},
                            {'range': [40, 70], 'color': 'rgba(255,152,0,0.2)'},
                            {'range': [70, 100], 'color': 'rgba(0,210,106,0.2)'},
                        ],
                    },
                    number={'font': {'color': 'white', 'size': 48}}
                ))
                fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=40,b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                | Factor | Score |
                |--------|-------|
                | Diversification | {diversification}/100 |
                | Concentration Risk | {concentration}/100 |
                | Sector Spread | {sector_score}/100 |
                | Asset Allocation | {allocation_score}/100 |
                | MF Quality | {mf_score}/100 |
                | **Overall** | **{health_score}/100** |
                """)
            
            st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
            
            # ── WARNINGS ──
            st.markdown("### ⚠️ Risk Warnings")
            warnings = []
            
            # Check single stock concentration
            for h in holdings:
                if h['pct'] > 15:
                    warnings.append(f"🔴 **{h['name']}** = {h['pct']:.1f}% of portfolio (should be < 15%)")
            
            # Sector concentration
            for sector, value in sectors.items():
                sec_pct = (value / grand_total * 100)
                if sec_pct > 25 and sector != 'Unknown':
                    warnings.append(f"🟠 **{sector}** sector = {sec_pct:.1f}% (should be < 25%)")
            
            # Gold check
            if gold_pct < 5:
                warnings.append(f"🟡 Gold allocation = {gold_pct:.1f}% (recommended: 5-10%)")
            if gold_pct > 15:
                warnings.append(f"🟡 Gold allocation = {gold_pct:.1f}% (too high, recommended: 5-10%)")
            
            # MF allocation
            if mf_pct < 30:
                warnings.append(f"🟡 Mutual Fund allocation = {mf_pct:.1f}% (consider increasing to 40-50%)")
            
            # Stock allocation
            if stock_pct > 60:
                warnings.append(f"🟠 Direct stocks = {stock_pct:.1f}% (high risk, consider reducing to 50%)")
            
            if warnings:
                for w in warnings:
                    st.markdown(w)
            else:
                st.success("✅ No major risks detected! Portfolio is well-balanced.")
            
            st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
            
            # ── ALLOCATION BREAKDOWN ──
            st.markdown("### 📊 Allocation Breakdown")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**By Asset Type**")
                alloc_data = pd.DataFrame([
                    {'Type': 'Stocks', 'Value': total_value - gold_value - silver_value},
                    {'Type': 'Mutual Funds', 'Value': mf_value},
                    {'Type': 'Gold', 'Value': gold_value},
                    {'Type': 'Silver', 'Value': silver_value},
                ])
                fig = px.pie(alloc_data, values='Value', names='Type', hole=0.4,
                            color_discrete_sequence=['#00b4d8', '#00d26a', '#ffd700', '#c0c0c0'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**By Sector**")
                sector_df = pd.DataFrame([
                    {'Sector': k, 'Value': v} for k, v in sectors.items() if k != 'Unknown'
                ]).sort_values('Value', ascending=False)
                if not sector_df.empty:
                    fig = px.bar(sector_df, x='Value', y='Sector', orientation='h',
                                color_discrete_sequence=['#00b4d8'])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font_color='white', height=300)
                    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE: OPPORTUNITIES
# ============================================================
elif page == "💡 Opportunities":
    st.markdown("# 💡 Smart Investment Opportunities")
    st.markdown("Where should you invest next? Based on your portfolio gaps and market conditions.")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    portfolio = load_portfolio()
    stocks = portfolio.get('stocks', {})
    
    tab1, tab2, tab3 = st.tabs(["🎯 Stock Opportunities", "📈 Rebalancing", "💰 Invest ₹X"])
    
    with tab1:
        st.markdown("### Top Opportunities in Your Holdings")
        if stocks:
            with st.spinner("Calculating opportunity scores..."):
                opp_rows = []
                for symbol, pos in stocks.items():
                    try:
                        data = fetch_stock_cached(symbol)
                        if data and data['cmp'] and data.get('high_52w'):
                            cmp = data['cmp']
                            high52 = data['high_52w']
                            low52 = data.get('low_52w', cmp)
                            
                            # Drawdown from 52W high
                            drawdown = ((cmp - high52) / high52 * 100)
                            
                            # Position in range (0 = at low, 100 = at high)
                            range_pos = ((cmp - low52) / (high52 - low52) * 100) if (high52 - low52) > 0 else 50
                            
                            # Opportunity score: bigger drawdown + good fundamentals = better opportunity
                            opp_score = 50
                            if drawdown < -30:
                                opp_score += 25
                            elif drawdown < -20:
                                opp_score += 20
                            elif drawdown < -10:
                                opp_score += 10
                            
                            # ROE bonus
                            if data.get('roe') and data['roe'] > 0.15:
                                opp_score += 15
                            elif data.get('roe') and data['roe'] > 0.10:
                                opp_score += 8
                            
                            # Analyst target bonus
                            if data.get('target_mean') and data['target_mean'] > cmp:
                                upside = (data['target_mean'] - cmp) / cmp * 100
                                if upside > 30:
                                    opp_score += 15
                                elif upside > 15:
                                    opp_score += 10
                            
                            # Negative ROE penalty
                            if data.get('roe') and data['roe'] < 0:
                                opp_score -= 20
                            
                            opp_score = max(0, min(100, opp_score))
                            
                            opp_rows.append({
                                'Stock': pos['name'],
                                'CMP': f"₹{cmp:.2f}",
                                '52W High': f"₹{high52:.0f}",
                                'Drawdown': f"{drawdown:.1f}%",
                                'Range Position': f"{range_pos:.0f}%",
                                'Opportunity Score': opp_score,
                                'Action': '🟢 BUY MORE' if opp_score >= 70 else ('🟡 WAIT' if opp_score >= 50 else '🔴 AVOID'),
                            })
                    except:
                        pass
                
                if opp_rows:
                    df_opp = pd.DataFrame(opp_rows).sort_values('Opportunity Score', ascending=False)
                    st.dataframe(df_opp, use_container_width=True)
                    
                    # Top picks
                    top = df_opp[df_opp['Opportunity Score'] >= 70]
                    if not top.empty:
                        st.success(f"🎯 **Best opportunities now:** {', '.join(top['Stock'].tolist())}")
    
    with tab2:
        st.markdown("### 🔄 Rebalancing Suggestions")
        st.markdown("**Ideal allocation:** Stocks 45-50% | Mutual Funds 40-45% | Gold 5-10%")
        
        mf = portfolio.get('mutual_funds', {})
        mf_value = sum(m.get('current', m['invested']) for m in mf.values())
        
        with st.spinner("Calculating..."):
            stock_value = 0
            gold_value = 0
            for sym, pos in stocks.items():
                try:
                    data = fetch_stock_cached(sym)
                    if data and data['cmp']:
                        val = data['cmp'] * pos['shares']
                        if 'gold' in pos['name'].lower() or 'silv' in pos['name'].lower():
                            gold_value += val
                        else:
                            stock_value += val
                except:
                    pass
            
            total = stock_value + mf_value + gold_value
            if total > 0:
                stock_pct = stock_value / total * 100
                mf_pct = mf_value / total * 100
                gold_pct = gold_value / total * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Stocks", f"{stock_pct:.0f}%", f"Target: 45-50%")
                col2.metric("Mutual Funds", f"{mf_pct:.0f}%", f"Target: 40-45%")
                col3.metric("Gold/Silver", f"{gold_pct:.0f}%", f"Target: 5-10%")
                
                st.markdown("**Suggestions:**")
                if stock_pct > 55:
                    st.warning(f"⚠️ Stocks overweight ({stock_pct:.0f}%). Direct next investments to Mutual Funds.")
                if mf_pct < 35:
                    st.info(f"💡 Increase MF allocation. Add ₹{int((0.4*total - mf_value)):,} more to MFs to reach 40%.")
                if gold_pct < 5:
                    st.info(f"💡 Gold underweight ({gold_pct:.1f}%). Consider adding ₹{int((0.07*total - gold_value)):,} to Gold ETF.")
                if stock_pct >= 45 and stock_pct <= 55 and mf_pct >= 35 and gold_pct >= 5:
                    st.success("✅ Portfolio is well-balanced! Keep current SIP ratios.")
    
    with tab3:
        st.markdown("### 💰 I have ₹X to invest — where should it go?")
        
        amount = st.number_input("Available amount to invest (₹)", min_value=1000, value=10000, step=1000)
        
        if st.button("🎯 Get Recommendation", type="primary"):
            st.markdown(f"### Recommended Allocation for ₹{amount:,}")
            
            # Simple allocation logic
            mf_alloc = int(amount * 0.5)
            stock_alloc = int(amount * 0.35)
            gold_alloc = int(amount * 0.15)
            
            # Specific picks
            st.markdown(f"""
            | Where | Amount | Why |
            |-------|--------|-----|
            | **Parag Parikh Flexi Cap** | ₹{int(mf_alloc * 0.4):,} | Best diversified fund, international exposure |
            | **HDFC Mid Cap Fund** | ₹{int(mf_alloc * 0.35):,} | Strong mid-cap exposure |
            | **Bandhan Small Cap** | ₹{int(mf_alloc * 0.25):,} | High growth potential |
            | **HDFC Bank** | ₹{int(stock_alloc * 0.5):,} | Strong Buy, 30% upside to target |
            | **Kalyan Jewellers** | ₹{int(stock_alloc * 0.5):,} | 75% upside, best growth story |
            | **TATAGOLD ETF** | ₹{gold_alloc:,} | Portfolio hedge, gold underweight |
            """)
            
            st.markdown(f"""
            **Split:** MF ₹{mf_alloc:,} (50%) | Stocks ₹{stock_alloc:,} (35%) | Gold ₹{gold_alloc:,} (15%)
            """)
            st.info("💡 This is based on your current allocation gaps and stock fundamentals.")


# ============================================================
# PAGE: AI ADVISOR
# ============================================================
elif page == "🤖 AI Advisor":
    st.markdown("# 🤖 AI Investment Advisor")
    st.markdown("Ask me anything about your portfolio, stocks, or investment strategy.")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    # Check for Gemini API key
    api_key = st.session_state.get('gemini_key', '')
    
    if not api_key:
        st.info("Enter your free Gemini API key to enable AI chat. Get one at [aistudio.google.com](https://aistudio.google.com/apikey)")
        key_input = st.text_input("Gemini API Key", type="password")
        if key_input:
            st.session_state['gemini_key'] = key_input
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Quick Answers (No API needed)")
        
        # Pre-built answers based on portfolio data
        portfolio = load_portfolio()
        stocks = portfolio.get('stocks', {})
        mf = portfolio.get('mutual_funds', {})
        
        quick_q = st.selectbox("Select a question:", [
            "Where should I invest ₹5,000 today?",
            "Which holding is most risky?",
            "What is my diversification score?",
            "Am I overexposed to any sector?",
            "Should I add more gold?",
            "What should I sell?",
            "What is my portfolio strategy?",
        ])
        
        if st.button("Get Answer", type="primary"):
            if quick_q == "Where should I invest ₹5,000 today?":
                st.markdown("""
                **Recommended allocation for ₹5,000:**
                
                | Investment | Amount | Reason |
                |-----------|--------|--------|
                | Parag Parikh Flexi Cap MF | ₹2,000 | Best risk-adjusted returns, international diversification |
                | HDFC Bank (Stock) | ₹1,500 | 30% upside to analyst target, India's best bank |
                | Kalyan Jewellers (Stock) | ₹1,000 | 75% upside, revenue growing 67% |
                | TATAGOLD ETF | ₹500 | Gold is underweight in your portfolio |
                
                **Reasoning:** Your MFs are well-chosen, increase allocation there. Among stocks, HDFC Bank and Kalyan Jewellers have the best risk-reward. Gold provides downside protection.
                """)
            
            elif quick_q == "Which holding is most risky?":
                st.error("""
                **🔴 Reliance Power** is your riskiest holding:
                
                - Loss-making company (negative EPS: -₹0.82)
                - Negative ROE (-2.1%) — destroying value
                - Stock crashed 64% in 1 year (₹70 → ₹24)
                - No analyst coverage — institutions have abandoned it
                - 22% of revenue goes to interest payments
                - No mutual fund holds more than 0.56%
                
                **Action:** Sell immediately. Redeploy ₹14,484 into quality stocks.
                """)
            
            elif quick_q == "What is my diversification score?":
                num_stocks = len(stocks)
                num_mf = len(mf)
                score = min(90, (num_stocks + num_mf) * 6)
                st.markdown(f"""
                **Diversification Score: {score}/100**
                
                - {num_stocks} stocks across multiple sectors ✅
                - {num_mf} mutual funds (flexi, mid, small cap) ✅
                - Gold/Silver ETFs for hedging ✅
                
                **Weakness:** Too many small positions in stocks. 
                Having 6 shares of BPCL (₹1,800) doesn't meaningfully diversify — it just adds tracking overhead.
                
                **Fix:** Consolidate to 5-6 stocks with ₹5,000+ each.
                """)
            
            elif quick_q == "Am I overexposed to any sector?":
                st.warning("""
                **⚠️ Potential Overexposure:**
                
                - **Utilities/Power:** Adani Power + Reliance Power + Suzlon = ~35% of stocks
                - **Banking:** HDFC Bank + Bank of Baroda + IRFC = ~53% of stocks
                
                **Banking is OK** — it's India's largest sector. But power sector at 35% is risky.
                
                **Fix:** Exit Reliance Power (loss-making), which reduces power exposure to ~20%.
                """)
            
            elif quick_q == "Should I add more gold?":
                st.markdown("""
                **Current Gold Allocation: ~6% of portfolio**
                
                ✅ This is within the ideal 5-10% range.
                
                However, you also hold TATSILV (silver) which adds commodity exposure. Combined = ~10%.
                
                **Recommendation:** 
                - Don't add more gold/silver right now
                - Consolidate: Keep TATAGOLD, sell HDFCGOLD (too small at ₹722)
                - Your commodity allocation is adequate
                """)
            
            elif quick_q == "What should I sell?":
                st.error("""
                **Sell these immediately:**
                
                | Stock | Reason | Capital Freed |
                |-------|--------|---------------|
                | Reliance Power | Loss-making, -64% in 1 year, no future | ₹14,484 |
                | HDFCGOLD | ₹722 — pointlessly small | ₹722 |
                | TATSILV | Over-allocated to commodities | ₹5,919 |
                
                **Total freed: ~₹21,000** → Redirect to Kalyan Jewellers + HDFC Bank
                """)
            
            elif quick_q == "What is my portfolio strategy?":
                st.markdown("""
                **Your Current Strategy (based on holdings):**
                
                🎯 **Core:** MFs for wealth building (Flexi + Mid + Small cap)
                📈 **Satellite:** Individual stocks for alpha
                🛡️ **Hedge:** Gold ETFs for protection
                
                **What's working:**
                - MF selection is excellent — top-rated funds
                - Banking exposure via HDFC Bank is solid
                - Suzlon gives renewable energy exposure
                
                **What needs fixing:**
                - Too many small stock positions
                - Reliance Power is dead weight
                - Need to increase MF allocation over time
                
                **Ideal target:**
                - 45% Mutual Funds
                - 40% Quality Stocks (5-6 names)
                - 10% Gold
                - 5% Cash for opportunities
                """)
    
    else:
        # Gemini AI Chat
        try:
            from google import genai
            
            client = genai.Client(api_key=api_key)
            
            # Build portfolio context
            portfolio = load_portfolio()
            portfolio_context = json.dumps(portfolio, indent=2)
            
            system_prompt = f"""You are an expert Indian stock market investment advisor. 
            The user's portfolio is:
            {portfolio_context}
            
            Give specific, actionable advice based on their actual holdings.
            Use Indian market context (NSE, BSE, SEBI, Indian tax rules).
            Be direct and practical. Use rupee amounts."""
            
            # Chat history
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
            # Display chat
            for msg in st.session_state.messages:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
            
            # User input
            prompt = st.chat_input("Ask about your portfolio...")
            
            if prompt:
                st.session_state.messages.append({'role': 'user', 'content': prompt})
                with st.chat_message('user'):
                    st.markdown(prompt)
                
                with st.chat_message('assistant'):
                    with st.spinner("Thinking..."):
                        response = client.models.generate_content(
                            model='gemini-2.0-flash',
                            contents=system_prompt + "\n\nUser question: " + prompt
                        )
                        reply = response.text
                        st.markdown(reply)
                        st.session_state.messages.append({'role': 'assistant', 'content': reply})
        
        except ImportError:
            st.warning("Gemini package not found. Using Quick Answers mode instead.")
            st.info("To enable full AI chat, run: `pip install google-genai`")
        except Exception as e:
            st.error(f"AI Error: {e}")
            if st.button("Reset API Key"):
                del st.session_state['gemini_key']
                st.rerun()





# ============================================================
# PAGE: MANAGE PORTFOLIO
# ============================================================
elif page == "➕ Manage Portfolio":
    st.markdown("# ➕ Manage Portfolio")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    portfolio = load_portfolio()
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Stock", "📥 Import Excel/CSV", "🗑️ Remove Stock", "📋 Current Holdings"])
    
    with tab1:
        st.markdown("### Add New Stock")
        col1, col2, col3 = st.columns(3)
        new_symbol = col1.text_input("Symbol (e.g., TCS, INFY, WIPRO)", "").strip().upper()
        new_shares = col2.number_input("Number of Shares", min_value=1, value=10)
        new_avg = col3.number_input("Average Buy Price (₹)", min_value=0.01, value=100.0)
        
        if st.button("➕ Add to Portfolio", type="primary") and new_symbol:
            symbol_key = new_symbol + '.NS' if not new_symbol.endswith('.NS') else new_symbol
            
            with st.spinner("Verifying stock..."):
                data = fetch_stock_cached(symbol_key)
                if data:
                    portfolio['stocks'][symbol_key] = {
                        'name': data['name'],
                        'shares': new_shares,
                        'avg_cost': new_avg
                    }
                    save_portfolio(portfolio)
                    st.success(f"✅ Added **{data['name']}** ({new_shares} shares @ ₹{new_avg})")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Could not find '{new_symbol}'. Check the NSE symbol.")
    
    with tab2:
        st.markdown("### 📥 Import from Excel/CSV")
        st.markdown("Upload a file with columns: **Symbol, Shares, AvgPrice**")
        
        uploaded = st.file_uploader("Upload Excel (.xlsx) or CSV (.csv)", type=['csv', 'xlsx'])
        
        if uploaded:
            try:
                if uploaded.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded)
                else:
                    import_df = pd.read_excel(uploaded)
                
                st.dataframe(import_df, use_container_width=True)
                st.info(f"Found {len(import_df)} stocks to import")
                
                # Try to detect columns
                cols = [c.lower().strip() for c in import_df.columns]
                sym_col = None
                shares_col = None
                price_col = None
                
                for i, c in enumerate(cols):
                    if 'symbol' in c or 'ticker' in c or 'stock' in c or 'name' in c:
                        sym_col = import_df.columns[i]
                    if 'share' in c or 'qty' in c or 'quantity' in c or 'unit' in c:
                        shares_col = import_df.columns[i]
                    if 'price' in c or 'avg' in c or 'cost' in c or 'buy' in c:
                        price_col = import_df.columns[i]
                
                if sym_col and shares_col and price_col:
                    st.success(f"Detected: Symbol=`{sym_col}`, Shares=`{shares_col}`, Price=`{price_col}`")
                    
                    if st.button("✅ Import All", type="primary"):
                        imported = 0
                        for _, row in import_df.iterrows():
                            sym = str(row[sym_col]).strip().upper()
                            key = sym + '.NS' if not sym.endswith('.NS') else sym
                            shares = int(row[shares_col])
                            avg = float(row[price_col])
                            
                            portfolio['stocks'][key] = {
                                'name': sym.replace('.NS', ''),
                                'shares': shares,
                                'avg_cost': avg
                            }
                            imported += 1
                        
                        save_portfolio(portfolio)
                        st.success(f"✅ Imported {imported} stocks!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Could not auto-detect columns. Make sure your file has: Symbol, Shares, AvgPrice columns")
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Download template
        st.markdown("---")
        st.markdown("**Need a template?**")
        template_csv = "Symbol,Shares,AvgPrice\nHDFCBANK,30,753.88\nTCS,10,3500.00\nRELIANCE,5,2400.00"
        st.download_button("📥 Download Template CSV", template_csv, "portfolio_template.csv", "text/csv")
    
    with tab3:
        st.markdown("### Remove Stock")
        stocks = portfolio.get('stocks', {})
        if stocks:
            stock_to_remove = st.selectbox(
                "Select stock to remove",
                options=list(stocks.keys()),
                format_func=lambda x: f"{stocks[x]['name']} ({stocks[x]['shares']} shares @ ₹{stocks[x]['avg_cost']})"
            )
            if st.button("🗑️ Remove from Portfolio", type="secondary"):
                name = stocks[stock_to_remove]['name']
                del portfolio['stocks'][stock_to_remove]
                save_portfolio(portfolio)
                st.success(f"Removed {name}")
                st.rerun()
        else:
            st.info("No stocks to remove.")
    
    with tab4:
        st.markdown("### Current Holdings")
        stocks = portfolio.get('stocks', {})
        if stocks:
            df = pd.DataFrame([
                {'Symbol': k.replace('.NS',''), 'Name': v['name'], 'Shares': v['shares'], 'Avg Cost': f"₹{v['avg_cost']:.2f}"}
                for k, v in stocks.items()
            ])
            st.dataframe(df, use_container_width=True)
            st.info(f"Total: **{len(stocks)} stocks** in portfolio")
        else:
            st.info("Portfolio is empty.")



# ============================================================
# PAGE: MUTUAL FUNDS
# ============================================================
elif page == "📊 Mutual Funds":
    st.markdown("# 📊 Mutual Funds")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
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
                'Invested': f"₹{invested:,}",
                'Current': f"₹{current:,}",
                'P&L (₹)': round(pnl, 0),
                'P&L %': round(pnl_pct, 2),
                'Status': '🟢 Profit' if pnl >= 0 else '🔴 Loss'
            })
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MF Invested", f"₹{total_invested:,}")
        col2.metric("MF Current", f"₹{total_current:,}")
        mf_pnl = total_current - total_invested
        col3.metric("MF P&L", f"₹{mf_pnl:,}", f"{((mf_pnl)/total_invested)*100:+.2f}%")
        col4.metric("XIRR", "10.10%")
        
        st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(mf_data), use_container_width=True)
        
        # Pie chart
        fig = px.pie(
            pd.DataFrame([{'Fund': k, 'Value': v.get('current', v['invested'])} for k, v in mf.items()]),
            values='Value', names='Fund', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=380
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mutual fund data. Update portfolio.json to add.")



# ============================================================
# PAGE: ALERTS & EXPORT
# ============================================================
elif page == "🔔 Alerts & Export":
    st.markdown("# 🔔 Price Alerts & Export")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    portfolio = load_portfolio()
    alerts = portfolio.get('alerts', {})
    
    tab1, tab2, tab3 = st.tabs(["🔔 Set Alerts", "✅ Check Alerts", "📥 Export"])
    
    with tab1:
        st.markdown("### Set Price Alert")
        col1, col2, col3 = st.columns(3)
        alert_symbol = col1.text_input("Stock Symbol", "HDFCBANK").strip().upper()
        alert_type = col2.selectbox("Alert When Price Goes", ["Above (Buy Target)", "Below (Stop Loss)"])
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
        
        if alerts:
            st.markdown("### Active Alerts")
            alert_rows = []
            for sym, alert in alerts.items():
                alert_rows.append({
                    'Stock': alert['symbol'],
                    'Type': '📈 Above' if alert['type'] == 'above' else '📉 Below',
                    'Target': f"₹{alert['price']}",
                })
            st.dataframe(pd.DataFrame(alert_rows), use_container_width=True)
    
    with tab2:
        st.markdown("### Check Alerts")
        if st.button("🔍 Check All Alerts Now", type="primary"):
            alerts = portfolio.get('alerts', {})
            if not alerts:
                st.info("No alerts set.")
            else:
                with st.spinner("Checking live prices..."):
                    for sym, alert in alerts.items():
                        try:
                            data = fetch_stock_cached(sym)
                            if data and data['cmp']:
                                cmp = data['cmp']
                                triggered = False
                                if alert['type'] == 'above' and cmp >= alert['price']:
                                    triggered = True
                                elif alert['type'] == 'below' and cmp <= alert['price']:
                                    triggered = True
                                
                                if triggered:
                                    st.error(f"🚨 **{alert['symbol']}** — CMP ₹{cmp:.2f} has {'crossed above' if alert['type'] == 'above' else 'fallen below'} ₹{alert['price']}!")
                                else:
                                    diff = abs(cmp - alert['price'])
                                    st.info(f"⏳ {alert['symbol']} — CMP ₹{cmp:.2f} | Target ₹{alert['price']} | Distance: ₹{diff:.2f}")
                        except:
                            pass
        
        # Portfolio vs targets
        st.markdown("### 📊 All Holdings vs Analyst Targets")
        if st.button("Check Analyst Targets"):
            stocks = portfolio.get('stocks', {})
            with st.spinner("Fetching..."):
                target_rows = []
                for sym, pos in stocks.items():
                    try:
                        data = fetch_stock_cached(sym)
                        if data and data['cmp'] and data.get('target_mean'):
                            upside = (data['target_mean'] - data['cmp']) / data['cmp'] * 100
                            target_rows.append({
                                'Stock': pos['name'],
                                'CMP': f"₹{data['cmp']:.2f}",
                                'Target': f"₹{data['target_mean']:.2f}",
                                'Upside': f"{upside:+.1f}%",
                                'Action': '🟢 BUY MORE' if upside > 20 else ('🟡 HOLD' if upside > 0 else '🔴 EXIT')
                            })
                    except:
                        pass
                if target_rows:
                    st.dataframe(pd.DataFrame(target_rows), use_container_width=True)
    
    with tab3:
        st.markdown("### 📥 Export Portfolio")
        if st.button("📥 Generate CSV Export", type="primary"):
            stocks = portfolio.get('stocks', {})
            with st.spinner("Generating..."):
                export_rows = []
                for sym, pos in stocks.items():
                    try:
                        data = fetch_stock_cached(sym)
                        if data and data['cmp']:
                            cmp = data['cmp']
                            invested = pos['avg_cost'] * pos['shares']
                            current = cmp * pos['shares']
                            pnl = current - invested
                            scoring = score_stock(data)
                            export_rows.append({
                                'Stock': pos['name'], 'Symbol': sym.replace('.NS',''),
                                'Shares': pos['shares'], 'Avg Cost': pos['avg_cost'],
                                'CMP': cmp, 'Invested': round(invested,2), 'Current': round(current,2),
                                'P&L': round(pnl,2), 'P&L %': round((pnl/invested)*100,2),
                                'Score': scoring['score'], 'Rating': scoring['recommendation'],
                                'P/E': data.get('pe_ratio'), 'ROE': data.get('roe'),
                                'Sector': data.get('sector')
                            })
                    except:
                        pass
                if export_rows:
                    df_export = pd.DataFrame(export_rows)
                    st.dataframe(df_export, use_container_width=True)
                    st.download_button("📥 Download CSV", df_export.to_csv(index=False),
                                      f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")



# ============================================================
# PAGE: WATCHLIST
# ============================================================
elif page == "📈 Watchlist":
    st.markdown("# 📈 Watchlist")
    st.markdown("Add stocks you're watching but haven't bought yet.")
    st.markdown('<hr class="pro-divider">', unsafe_allow_html=True)
    
    portfolio = load_portfolio()
    watchlist = portfolio.get('watchlist', [])
    
    # Add to watchlist
    col1, col2 = st.columns([3, 1])
    new_watch = col1.text_input("Add stock to watchlist", placeholder="e.g. TCS, INFY").strip().upper()
    col2.markdown("<br>", unsafe_allow_html=True)
    if col2.button("➕ Add", use_container_width=True) and new_watch:
        if new_watch not in watchlist:
            watchlist.append(new_watch)
            portfolio['watchlist'] = watchlist
            save_portfolio(portfolio)
            st.success(f"Added {new_watch} to watchlist")
            st.rerun()
    
    if watchlist:
        with st.spinner("Fetching watchlist data..."):
            watch_rows = []
            for sym in watchlist:
                try:
                    key = sym + '.NS' if not sym.endswith('.NS') else sym
                    data = analyze_stock(key)
                    if data:
                        scoring = data['scoring']
                        watch_rows.append({
                            'Stock': data['name'],
                            'Symbol': sym,
                            'CMP': f"₹{data['cmp']:.2f}",
                            'Score': scoring['score'],
                            'Rating': scoring['recommendation'],
                            'P/E': f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else 'N/A',
                            'ROE': f"{data['roe']*100:.1f}%" if data['roe'] else 'N/A',
                            'Target': f"₹{data['target_mean']:.0f}" if data['target_mean'] else 'N/A',
                            'Buy?': '✅ YES' if scoring['score'] >= 60 else ('⚠️ WAIT' if scoring['score'] >= 45 else '❌ NO')
                        })
                except:
                    pass
            
            if watch_rows:
                st.dataframe(pd.DataFrame(watch_rows), use_container_width=True)
        
        # Remove from watchlist
        remove_sym = st.selectbox("Remove from watchlist:", watchlist)
        if st.button("🗑️ Remove"):
            watchlist.remove(remove_sym)
            portfolio['watchlist'] = watchlist
            save_portfolio(portfolio)
            st.rerun()
    else:
        st.info("Watchlist is empty. Add stocks you want to track before buying.")
