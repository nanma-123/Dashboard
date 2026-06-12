import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration to wide and dark-friendly
st.set_page_config(
    page_title="Wayne Enterprises — State of the Enterprise Report | Q4 2024",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Color Palette ───
COLORS = {
    'blue': '#3b82f6',
    'cyan': '#22d3ee',
    'purple': '#8b5cf6',
    'emerald': '#10b981',
    'amber': '#f59e0b',
    'rose': '#f43f5e',
    'indigo': '#6366f1',
    'pink': '#ec4899',
    'teal': '#14b8a6',
    'sky': '#0ea5e9',
}

# ─── Custom CSS Styling ───
st.markdown("""
    <style>
        /* Import Inter and Playfair Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;600;700;800&display=swap');
        
        /* Apply background and global typography */
        .stApp {
            background: linear-gradient(135deg, #0b0f19 0%, #111827 100%) !important;
            font-family: 'Inter', sans-serif !important;
            color: #e2e8f0 !important;
        }
        
        /* Titles and Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', serif !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        /* Confidential Badge */
        .badge {
            background-color: rgba(244, 63, 94, 0.1);
            color: #f43f5e;
            border: 1px solid rgba(244, 63, 94, 0.2);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Glassmorphism Card Wrapper */
        .glass-card {
            background: rgba(17, 24, 39, 0.55);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(59, 130, 246, 0.2);
        }

        /* Top Bar Border Highlights */
        .bar-blue { border-top: 4px solid #3b82f6; }
        .bar-emerald { border-top: 4px solid #10b981; }
        .bar-purple { border-top: 4px solid #8b5cf6; }
        .bar-amber { border-top: 4px solid #f59e0b; }
        .bar-cyan { border-top: 4px solid #22d3ee; }
        .bar-rose { border-top: 4px solid #f43f5e; }

        /* KPI Values */
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            line-height: 1.1;
        }
        .kpi-label {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 4px;
            font-weight: 500;
        }
        .kpi-change {
            font-size: 0.78rem;
            margin-top: 8px;
            font-weight: 600;
        }
        .positive { color: #10b981; }
        .negative { color: #f43f5e; }

        /* Narrative Headers */
        .narrative-category {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.05em;
            color: #3b82f6;
        }
        .narrative-date {
            font-size: 0.75rem;
            color: #64748b;
            margin-left: 12px;
        }
        .narrative-headline {
            font-size: 1.4rem;
            margin-top: 6px;
            margin-bottom: 12px;
            line-height: 1.3;
        }
        .narrative-subhead {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        .narrative-text {
            font-size: 0.88rem;
            color: #cbd5e1;
            line-height: 1.6;
        }

        /* Prediction Card */
        .pred-card {
            border-left: 4px solid #3b82f6;
            padding-left: 16px;
            margin-bottom: 20px;
        }
        .pred-card.growth { border-left-color: #10b981; }
        .pred-card.risk { border-left-color: #f43f5e; }
        .pred-card.opportunity { border-left-color: #8b5cf6; }

        .pred-metric {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
        }

        /* Stat highlights inside narratives */
        .stat-highlight {
            color: #ffffff;
            font-weight: 600;
            background: rgba(59, 130, 246, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }

        /* Custom style for streamlit tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(17, 24, 39, 0.4);
            padding: 8px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.04);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            padding: 8px 16px !important;
            color: #94a3b8 !important;
            font-weight: 600 !important;
            border: none !important;
            background-color: transparent !important;
            transition: background-color 0.2s, color 0.2s;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.03) !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Data Loading ───
@st.cache_data
def load_data():
    financial = pd.read_csv('data/wayne_financial_data.csv')
    security = pd.read_csv('data/wayne_security_data.csv')
    rd = pd.read_csv('data/wayne_rd_portfolio.csv')
    supply = pd.read_csv('data/wayne_supply_chain.csv')
    hr = pd.read_csv('data/wayne_hr_analytics.csv')
    return financial, security, rd, supply, hr

try:
    financialData, securityData, rdData, supplyData, hrData = load_data()
except Exception as e:
    st.error(f"Error loading CSV data files: {e}")
    st.stop()

# ─── Helper Functions for Plotly Custom Styling ───
def style_plotly_fig(fig, title=None, height=300):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter, sans-serif', size=11),
        title=dict(text=title, font=dict(color='#ffffff', size=14, family='Playfair Display, serif')) if title else None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.04)',
        zeroline=False,
        linecolor='rgba(255,255,255,0.1)',
        tickfont=dict(size=10)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.04)',
        zeroline=False,
        linecolor='rgba(255,255,255,0.1)',
        tickfont=dict(size=10)
    )
    return fig

# ═══════════════════════════════════════════
#  NAVIGATION / HEADER
# ═══════════════════════════════════════════
st.write(" ")
cols_header = st.columns([8, 4])
with cols_header[0]:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 16px;'>
            <div style='background: #3b82f6; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.4rem; color: #ffffff;'>WE</div>
            <div>
                <h1 style='margin: 0; font-size: 2.2rem;'>Wayne Enterprises</h1>
                <p style='margin: 0; color: #3b82f6; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;'>Board Analytics Platform</p>
            </div>
        </div>
    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════
#  HERO SECTION (KPIs)
# ═══════════════════════════════════════════
kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.markdown("""
        <div class='glass-card bar-blue'>
            <div class='kpi-value'>$14.8B</div>
            <div class='kpi-label'>Total Revenue FY2024</div>
            <div class='kpi-change positive'>▲ 18.2% YoY</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown("""
        <div class='glass-card bar-emerald'>
            <div class='kpi-value'>$4.12B</div>
            <div class='kpi-label'>Net Profit FY2024</div>
            <div class='kpi-change positive'>▲ 22.5% YoY</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown("""
        <div class='glass-card bar-purple'>
            <div class='kpi-value'>75</div>
            <div class='kpi-label'>Active R&D Projects</div>
            <div class='kpi-change positive'>▲ 12 New</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown("""
        <div class='glass-card bar-amber'>
            <div class='kpi-value'>52.4K</div>
            <div class='kpi-label'>Global Workforce</div>
            <div class='kpi-change positive'>▲ 6.8% Growth</div>
        </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  DATA NARRATIVES
# ═══════════════════════════════════════════
st.markdown("## Data Narratives")
st.markdown("<p style='color:#94a3b8; font-size:1.1rem; margin-top:-10px; margin-bottom:24px;'>Six editorial analyses decoding the key trends shaping Wayne Enterprises</p>", unsafe_allow_html=True)

# 1. Financial Narrative
with st.container():
    st.markdown("<div class='glass-card bar-blue'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#3b82f6'>Financial Performance</div>
            <div class='narrative-date'>Analysis Period: Q1 2023 — Q4 2024</div>
            <h3 class='narrative-headline'>Construction & Aerospace Power Record-Breaking Revenue as Wayne Enterprises Crosses $14B</h3>
            <p class='narrative-subhead'>Wayne Construction's 29% CAGR and Aerospace's unwavering growth engine pushed the enterprise past a $14 billion revenue milestone.</p>
            <div class='narrative-text'>
                In a year marked by global economic headwinds, Wayne Enterprises demonstrated remarkable resilience. 
                <strong>Wayne Construction</strong> emerged as the standout performer, growing from $2.1B in Q1 2023 to 
                <span class='stat-highlight'>$3.38B in Q4 2024</span> — a staggering 61% increase driven by the Gotham Smart City Initiative.
                <br><br>
                <strong>Wayne Aerospace</strong> maintained its position as the innovation anchor, with quarterly revenue climbing 
                from $1.25B to <span class='stat-highlight'>$1.95B</span>. R&D investment as a percentage of revenue held steady at ~10%.
                <br><br>
                The <strong>Wayne Foundation</strong>, operating by design at a loss, expanded its programs significantly — revenue grew 102% while deepening community impact.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Process Financial Data for Narrative Chart
        fin_df = financialData.copy()
        fin_df['Period'] = fin_df['Quarter'] + " " + fin_df['Year'].astype(str)
        fin_df = fin_df.sort_values(by=['Year', 'Quarter'])
        
        divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction', 'Wayne Foundation']
        div_colors = [COLORS['blue'], COLORS['emerald'], COLORS['purple'], COLORS['amber'], COLORS['rose']]
        
        fig = go.Figure()
        for idx, div in enumerate(divisions):
            sub_df = fin_df[fin_df['Division'] == div]
            fig.add_trace(go.Bar(
                x=sub_df['Period'],
                y=sub_df['Revenue_M'],
                name=div.replace('Wayne ', ''),
                marker_color=div_colors[idx]
            ))
        
        fig.update_layout(barmode='group', xaxis_title="Quarter", yaxis_title="Revenue ($M)")
        st.plotly_chart(style_plotly_fig(fig, "Quarterly Revenue by Division ($M)", height=320), use_container_width=True)
        
        # Stats Grid
        s1, s2, s3 = st.columns(3)
        s1.metric("FY2024 Revenue", "$14.8B")
        s2.metric("Avg Profit Margin", "27.8%")
        s3.metric("Total R&D Spend", "$1.14B")
        
    st.markdown("</div>", unsafe_allow_html=True)

# 2. Security Narrative
with st.container():
    st.markdown("<div class='glass-card bar-emerald'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#10b981'>Gotham Security</div>
            <div class='narrative-date'>Monthly Tracking: Jan 2023 — Jun 2024</div>
            <h3 class='narrative-headline'>Gotham's Streets Are Getting Safer — But The Narrows Still Demands Attention</h3>
            <p class='narrative-subhead'>Bristol achieved near-zero crime incidents while Wayne Tech deployments drove a 40% average reduction in security incidents.</p>
            <div class='narrative-text'>
                <strong>Bristol</strong> has become Gotham's safest district, recording <span class='stat-highlight'>zero security incidents</span> in June 2024 with a perfect 10.0 safety score and 100% crime prevention effectiveness.
                <br><br>
                <strong>Park Row</strong> showed the most dramatic transformation: incidents fell from 32 to just 1 over 18 months. This turnaround correlates directly with the tripling of community engagement events.
                <br><br>
                However, <strong>The Narrows</strong> remains Gotham's most challenging zone. While incidents did fall from 98 to 60 — a 39% improvement — the district still accounts for 43% of all citywide incidents.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Security Line Chart
        sec_df = securityData.copy().sort_values(by='Date')
        districts = ['Bristol', 'Park Row', 'Downtown', 'Diamond District', 'East End', 'The Narrows']
        dist_colors = [COLORS['emerald'], COLORS['blue'], COLORS['cyan'], COLORS['purple'], COLORS['amber'], COLORS['rose']]
        
        fig = go.Figure()
        for idx, dist in enumerate(districts):
            sub_df = sec_df[sec_df['District'] == dist]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'].str.slice(0, 7),
                y=sub_df['Security_Incidents'],
                name=dist,
                mode='lines+markers',
                line=dict(color=dist_colors[idx], width=2),
                fill='tozeroy' if dist == 'The Narrows' else 'none',  # Fixed parameter setting to valid option
                marker=dict(size=4)
            ))
        
        fig.update_layout(xaxis_title="Date", yaxis_title="Incidents")
        st.plotly_chart(style_plotly_fig(fig, "Security Incidents by District (Monthly Trend)", height=320), use_container_width=True)
        
        s1, s2, s3 = st.columns(3)
        s1.metric("Avg Incident Decline", "-42%")
        s2.metric("Best Response Time", "1.0 min")
        s3.metric("Peak Tech Deployments", "213")
        
    st.markdown("</div>", unsafe_allow_html=True)

# 3. R&D Narrative
with st.container():
    st.markdown("<div class='glass-card bar-purple'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#8b5cf6'>R&D Portfolio</div>
            <div class='narrative-date'>75 Active Projects Across All Divisions</div>
            <h3 class='narrative-headline'>The Innovation Engine: A $8.2B Bet on Tomorrow's Technologies</h3>
            <p class='narrative-subhead'>From neural interfaces to quantum computing, Wayne's R&D portfolio spans the bleeding edge.</p>
            <div class='narrative-text'>
                Wayne Enterprises is running <strong>75 active R&D projects</strong> with a combined budget of $8.2 billion. 
                Aerospace leads with 15 projects, followed by Construction and Biotech.
                <br><br>
                <span class='stat-highlight'>22 projects are rated "Very High"</span> commercialization potential, led by Neural Interface Technology ($145.7M) and the Quantum Computer Chip ($234.7M).
                <br><br>
                However, moonshot programs like <strong>Dimensional Portal Research</strong> (21.8% timeline adherence) are consuming significant budget with "Very Low" commercialization ratings.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Horizontal Bar Chart for R&D
        rd_grouped = rdData.groupby('Division').sum().reset_index()
        rd_grouped = rd_grouped.sort_values(by='Division')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=rd_grouped['Division'].str.replace('Wayne ', ''),
            x=rd_grouped['Budget_Allocated_M'],
            name='Allocated',
            orientation='h',
            marker_color=COLORS['purple']
        ))
        fig.add_trace(go.Bar(
            y=rd_grouped['Division'].str.replace('Wayne ', ''),
            x=rd_grouped['Budget_Spent_M'],
            name='Spent',
            orientation='h',
            marker_color=COLORS['cyan']
        ))
        
        fig.update_layout(barmode='group', xaxis_title="Budget ($M)", yaxis_title="Division")
        st.plotly_chart(style_plotly_fig(fig, "R&D Budget vs Spend by Division ($M)", height=320), use_container_width=True)
        
        s1, s2, s3 = st.columns(3)
        s1.metric("Total R&D Budget", "$8.2B")
        s2.metric("Patent Applications", "165")
        s3.metric("Completed Projects", "4")
        
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Supply Chain Narrative
with st.container():
    st.markdown("<div class='glass-card bar-amber'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#f59e0b'>Supply Chain Operations</div>
            <div class='narrative-date'>5 Facilities · 18-Month Tracking</div>
            <h3 class='narrative-headline'>Supply Chain Resilience: Metropolis North Leads the Pack in Quality & Sustainability</h3>
            <p class='narrative-subhead'>While production volumes grew 30%+ across all facilities, Metropolis North achieved a remarkable A+ sustainability rating.</p>
            <div class='narrative-text'>
                <strong>Metropolis North</strong> (Biotech Equipment) is the clear operational champion, achieving a 
                <span class='stat-highlight'>97.0% quality score</span> and A+ sustainability rating.
                <br><br>
                <strong>Gotham Main</strong> (Aerospace Components) performed admirably at scale, growing production 46% to 182K units while maintaining 95% quality.
                <br><br>
                The concern lies with <strong>Central City</strong> (Applied Sciences), which experienced the most supply chain disruptions — averaging 2.7 per month.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Production Volumes Line Chart
        supply_df = supplyData.copy().sort_values(by='Date')
        facilities = ['Gotham_Main', 'Metropolis_North', 'Central_City', 'Star_City', 'Keystone_City']
        fac_colors = [COLORS['blue'], COLORS['emerald'], COLORS['amber'], COLORS['rose'], COLORS['purple']]
        
        fig = go.Figure()
        for idx, fac in enumerate(facilities):
            sub_df = supply_df[supply_df['Facility_Location'] == fac]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'],
                y=sub_df['Monthly_Production_Volume'],
                name=fac.replace('_', ' '),
                mode='lines+markers',
                line=dict(color=fac_colors[idx], width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(xaxis_title="Date", yaxis_title="Units")
        st.plotly_chart(style_plotly_fig(fig, "Production Volume by Facility (Monthly)", height=320), use_container_width=True)
        
        s1, s2, s3 = st.columns(3)
        s1.metric("Peak Monthly Output", "871K")
        s2.metric("Highest Quality Score", "97.0%")
        s3.metric("Best Sustainability", "A+")
        
    st.markdown("</div>", unsafe_allow_html=True)

# 5. HR Narrative
with st.container():
    st.markdown("<div class='glass-card bar-cyan'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#22d3ee'>People & Culture</div>
            <div class='narrative-date'>Workforce Analytics: 2023–2024</div>
            <h3 class='narrative-headline'>The People Factor: Why Wayne's Senior Talent Is Staying — And The Diversity Engine Is Working</h3>
            <p class='narrative-subhead'>100% senior retention, rising diversity indices, and a clear correlation between security clearance and satisfaction scores.</p>
            <div class='narrative-text'>
                Wayne's retention story is exceptional at the top: <strong>Executive retention hit 100%</strong> across both Aerospace and Biotech.
                <br><br>
                The <strong>diversity index</strong> showed consistent improvement across all levels, with entry-level leading at 0.91 in June 2024.
                <br><br>
                A fascinating correlation emerges between <strong>security clearance and satisfaction</strong>: executives with higher clearance levels score 10.0 satisfaction.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Retention by Level Grouped Bar
        hr_df = hrData.copy()
        # Get latest record for each dept and level
        hr_latest = hr_df.sort_values('Date').groupby(['Department', 'Employee_Level']).last().reset_index()
        
        levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive']
        depts = hr_latest['Department'].unique()
        hr_colors = [COLORS['blue'], COLORS['emerald'], COLORS['purple']]
        
        fig = go.Figure()
        for idx, dept in enumerate(depts):
            sub_df = hr_latest[hr_latest['Department'] == dept]
            sub_df = sub_df.set_index('Employee_Level').reindex(levels).reset_index()
            fig.add_trace(go.Bar(
                x=levels,
                y=sub_df['Retention_Rate_Pct'],
                name=dept.replace('Wayne ', ''),
                marker=dict(color=hr_colors[idx])
            ))
        
        fig.update_layout(barmode='group', xaxis_title="Employee Level", yaxis_title="% Retention", yaxis=dict(range=[85, 102]))
        st.plotly_chart(style_plotly_fig(fig, "Retention Rate by Employee Level (%)", height=320), use_container_width=True)
        
        s1, s2, s3 = st.columns(3)
        s1.metric("Executive Retention", "100%")
        s2.metric("Peak Diversity Index", "0.91")
        s3.metric("Peak Satisfaction", "10.0")
        
    st.markdown("</div>", unsafe_allow_html=True)

# 6. Cross-Dataset Narrative
with st.container():
    st.markdown("<div class='glass-card bar-rose'>", unsafe_allow_html=True)
    cols = st.columns([5, 7])
    with cols[0]:
        st.markdown("""
            <div class='narrative-category' style='color:#f43f5e'>Cross-Dataset Intelligence</div>
            <div class='narrative-date'>Multi-Source Correlation Analysis</div>
            <h3 class='narrative-headline'>Connecting the Dots: How R&D Fuels Revenue, and Why Happy Workers Build Better Products</h3>
            <p class='narrative-subhead'>Cross-dataset analysis reveals powerful correlations: divisions with higher R&D intensity generate faster revenue growth.</p>
            <div class='narrative-text'>
                <strong>R&D investment intensity predicts revenue growth</strong>. Wayne Biotech, investing ~10% in R&D, grew revenue 65% over the analysis period.
                <br><br>
                A second powerful signal connects <strong>employee satisfaction to output quality</strong>. Metropolis North (Biotech) — with highly satisfied workforce — delivers the highest quality scores (97%).
                <br><br>
                <strong>Community investment is the highest-ROI security strategy:</strong> districts with higher community engagement events show steeper declines in security incidents.
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        # Scatter Plot: R&D intensity vs revenue growth
        divs = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']
        scatter_colors = [COLORS['blue'], COLORS['emerald'], COLORS['purple'], COLORS['amber']]
        
        fig = go.Figure()
        for idx, div in enumerate(divs):
            div_fin = financialData[financialData['Division'] == div].sort_values(by=['Year', 'Quarter'])
            first = div_fin.iloc[0]
            last = div_fin.iloc[-1]
            rev_growth = ((last['Revenue_M'] - first['Revenue_M']) / first['Revenue_M']) * 100
            rd_intensity = (last['RD_Investment_M'] / last['Revenue_M']) * 100
            
            fig.add_trace(go.Scatter(
                x=[rd_intensity],
                y=[rev_growth],
                name=div.replace('Wayne ', ''),
                mode='markers',
                marker=dict(color=scatter_colors[idx], size=20, line=dict(width=2, color='#ffffff'))
            ))
        
        fig.update_layout(
            xaxis=dict(title="R&D as % of Revenue", range=[3, 12]),
            yaxis=dict(title="Revenue Growth (%)", range=[40, 80]),
        )
        st.plotly_chart(style_plotly_fig(fig, "R&D Investment vs Revenue Growth", height=320), use_container_width=True)
        
        s1, s2, s3 = st.columns(3)
        s1.metric("R&D-Revenue Corr.", "0.87")
        s2.metric("Satisfaction-Quality", "0.92")
        s3.metric("Community-Safety", "0.95")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 30px; margin-bottom: 40px;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  INTERACTIVE DASHBOARDS
# ═══════════════════════════════════════════
st.markdown("## Interactive Dashboards")
st.markdown("<p style='color:#94a3b8; font-size:1.1rem; margin-top:-10px; margin-bottom:24px;'>Deep-dive analytics across every dimension of Wayne Enterprises operations</p>", unsafe_allow_html=True)

dash_tabs = st.tabs(["Financial", "Security", "R&D", "Supply Chain", "HR", "Cross-Insights"])

# ─── Tab 1: Financial ───
with dash_tabs[0]:
    t1_col1, t1_col2 = st.columns(2)
    
    with t1_col1:
        # Revenue Trend Line Chart
        fin_df = financialData.copy()
        fin_df['Period'] = fin_df['Quarter'] + " " + fin_df['Year'].astype(str).str.slice(2,4)
        fin_df = fin_df.sort_values(by=['Year', 'Quarter'])
        
        fig = go.Figure()
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            sub_df = fin_df[fin_df['Division'] == div]
            fig.add_trace(go.Scatter(
                x=sub_df['Period'],
                y=sub_df['Revenue_M'],
                name=div.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=div_colors[idx], width=2),
                fill='none'
            ))
        fig.update_layout(xaxis_title="Quarter", yaxis_title="Revenue ($M)")
        st.plotly_chart(style_plotly_fig(fig, "Revenue Trend by Division (Quarterly)", height=320), use_container_width=True)
        
    with t1_col2:
        # Profit Margin Line Chart
        fig = go.Figure()
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            sub_df = fin_df[fin_df['Division'] == div]
            margin = (sub_df['Net_Profit_M'] / sub_df['Revenue_M']) * 100
            fig.add_trace(go.Scatter(
                x=sub_df['Period'],
                y=margin,
                name=div.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=div_colors[idx], width=2, dash='dash' if div == 'Wayne Construction' else None)
            ))
        fig.update_layout(xaxis_title="Quarter", yaxis_title="Margin (%)", yaxis=dict(range=[15, 40]))
        st.plotly_chart(style_plotly_fig(fig, "Profit Margin by Division", height=320), use_container_width=True)

    t1_b1, t1_b2, t1_b3 = st.columns(3)
    
    with t1_b1:
        # Market Share Distribution (Doughnut)
        q4_df = financialData[(financialData['Quarter'] == 'Q4') & (financialData['Year'] == 2024)]
        q4_df = q4_df[q4_df['Market_Share_Pct'] != 'N/A']
        q4_df['Market_Share_Pct'] = pd.to_numeric(q4_df['Market_Share_Pct'])
        
        fig = px.pie(
            q4_df,
            values='Market_Share_Pct',
            names=q4_df['Division'].str.replace('Wayne ', ''),
            hole=0.65,
            color_discrete_sequence=[COLORS['blue'], COLORS['emerald'], COLORS['purple'], COLORS['amber']]
        )
        st.plotly_chart(style_plotly_fig(fig, "Market Share Distribution (Q4 2024)", height=280), use_container_width=True)
        
    with t1_b2:
        # R&D as % of Revenue
        q4_df['RD_Pct'] = (q4_df['RD_Investment_M'] / q4_df['Revenue_M']) * 100
        fig = px.bar(
            q4_df,
            x=q4_df['Division'].str.replace('Wayne ', ''),
            y='RD_Pct',
            color=q4_df['Division'].str.replace('Wayne ', ''),
            color_discrete_map={
                'Aerospace': COLORS['blue'],
                'Biotech': COLORS['emerald'],
                'Applied Sciences': COLORS['purple'],
                'Construction': COLORS['amber']
            }
        )
        fig.update_layout(showlegend=False, xaxis_title="Division", yaxis_title="% of Revenue")
        st.plotly_chart(style_plotly_fig(fig, "R&D as % of Revenue", height=280), use_container_width=True)
        
    with t1_b3:
        # Customer Satisfaction Trend
        fig = go.Figure()
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            sub_df = fin_df[fin_df['Division'] == div]
            fig.add_trace(go.Scatter(
                x=sub_df['Period'],
                y=sub_df['Customer_Satisfaction_Score'],
                name=div.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=div_colors[idx], width=1.5),
                marker=dict(size=4)
            ))
        fig.update_layout(xaxis_title="Quarter", yaxis_title="Score (out of 5)", yaxis=dict(range=[3.5, 5.0]))
        st.plotly_chart(style_plotly_fig(fig, "Customer Satisfaction Trend", height=280), use_container_width=True)


# ─── Tab 2: Security ───
with dash_tabs[1]:
    t2_col1, t2_col2 = st.columns(2)
    
    with t2_col1:
        # Incidents Over Time by District
        sec_df = securityData.copy().sort_values(by='Date')
        fig = go.Figure()
        for idx, dist in enumerate(districts):
            sub_df = sec_df[sec_df['District'] == dist]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'].str.slice(0, 7),
                y=sub_df['Security_Incidents'],
                name=dist,
                mode='lines',
                line=dict(color=dist_colors[idx], width=1.5)
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Incidents")
        st.plotly_chart(style_plotly_fig(fig, "Incidents Over Time by District", height=320), use_container_width=True)
        
    with t2_col2:
        # Response Time Improvement
        fig = go.Figure()
        for idx, dist in enumerate(districts):
            sub_df = sec_df[sec_df['District'] == dist]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'].str.slice(0, 7),
                y=sub_df['Response_Time_Minutes'],
                name=dist,
                mode='lines',
                line=dict(color=dist_colors[idx], width=1.5)
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Minutes")
        st.plotly_chart(style_plotly_fig(fig, "Response Time Improvement", height=320), use_container_width=True)

    t2_b1, t2_b2 = st.columns(2)
    
    with t2_b1:
        # Wayne Tech Deployments vs Crime Prevention (Scatter)
        sec_latest = sec_df.sort_values(by='Date').groupby('District').last().reset_index()
        fig = go.Figure()
        for idx, dist in enumerate(districts):
            rec = sec_latest[sec_latest['District'] == dist]
            fig.add_trace(go.Scatter(
                x=rec['Wayne_Tech_Deployments'],
                y=rec['Crime_Prevention_Effectiveness_Pct'],
                name=dist,
                mode='markers',
                marker=dict(color=dist_colors[idx], size=16, line=dict(width=1, color='#ffffff'))
            ))
        fig.update_layout(xaxis_title="Wayne Tech Deployments", yaxis_title="Crime Prevention (%)", yaxis=dict(range=[60, 102]))
        st.plotly_chart(style_plotly_fig(fig, "Wayne Tech Deployments vs Crime Prevention", height=300), use_container_width=True)
        
    with t2_b2:
        # Public Safety Radar
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=sec_latest['Public_Safety_Score'],
            theta=sec_latest['District'],
            fill='toself',
            name='Public Safety Score',
            line_color=COLORS['emerald']
        ))
        fig.add_trace(go.Scatterpolar(
            r=sec_latest['Employee_Safety_Index'],
            theta=sec_latest['District'],
            fill='toself',
            name='Employee Safety Index',
            line_color=COLORS['blue']
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[5, 11])),
            showlegend=True
        )
        st.plotly_chart(style_plotly_fig(fig, "Public Safety Score by District (Latest)", height=300), use_container_width=True)


# ─── Tab 3: R&D ───
with dash_tabs[2]:
    t3_col1, t3_col2 = st.columns(2)
    
    with t3_col1:
        # Budget Allocated vs Spent
        rd_grouped = rdData.groupby('Division').sum().reset_index().sort_values(by='Division')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=rd_grouped['Division'].str.replace('Wayne ', ''),
            y=rd_grouped['Budget_Allocated_M'],
            name='Allocated ($M)',
            marker_color=COLORS['purple']
        ))
        fig.add_trace(go.Bar(
            x=rd_grouped['Division'].str.replace('Wayne ', ''),
            y=rd_grouped['Budget_Spent_M'],
            name='Spent ($M)',
            marker_color=COLORS['cyan']
        ))
        fig.update_layout(barmode='group', xaxis_title="Division", yaxis_title="$M")
        st.plotly_chart(style_plotly_fig(fig, "Budget Allocated vs Spent by Division", height=320), use_container_width=True)
        
    with t3_col2:
        # Commercialization potential distribution (Doughnut)
        pot_order = ['Very High', 'High', 'Medium', 'Low', 'Very Low']
        pot_counts = rdData['Commercialization_Potential'].value_counts().reindex(pot_order).fillna(0).reset_index()
        fig = px.pie(
            pot_counts,
            values='count',
            names='Commercialization_Potential',
            hole=0.6,
            color_discrete_sequence=[COLORS['emerald'], COLORS['blue'], COLORS['amber'], COLORS['rose'], '#64748b']
        )
        st.plotly_chart(style_plotly_fig(fig, "Commercialization Potential Distribution", height=320), use_container_width=True)

    t3_b1, t3_b2 = st.columns(2)
    
    with t3_b1:
        # Timeline Adherence (Bar)
        rd_timeline = rdData.groupby('Division')['Timeline_Adherence_Pct'].mean().reset_index()
        
        fig = px.bar(
            rd_timeline,
            x=rd_timeline['Division'].str.replace('Wayne ', ''),
            y='Timeline_Adherence_Pct',
            color='Timeline_Adherence_Pct',
            color_continuous_scale=[[0, COLORS['rose']], [0.5, COLORS['amber']], [1.0, COLORS['emerald']]]
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="Division", yaxis_title="% Adherence", yaxis=dict(range=[0, 100]))
        st.plotly_chart(style_plotly_fig(fig, "Timeline Adherence by Division", height=300), use_container_width=True)
        
    with t3_b2:
        # Patent Applications (Bar)
        rd_patents = rdData.groupby('Division')['Patent_Applications'].sum().reset_index()
        fig = px.bar(
            rd_patents,
            x=rd_patents['Division'].str.replace('Wayne ', ''),
            y='Patent_Applications',
            color='Division',
            color_discrete_sequence=[COLORS['purple'], COLORS['emerald'], COLORS['blue'], COLORS['amber'], COLORS['rose']]
        )
        fig.update_layout(showlegend=False, xaxis_title="Division", yaxis_title="Patents")
        st.plotly_chart(style_plotly_fig(fig, "Patent Applications by Division", height=300), use_container_width=True)


# ─── Tab 4: Supply Chain ───
with dash_tabs[3]:
    t4_col1, t4_col2 = st.columns(2)
    
    with t4_col1:
        # Quality score trend
        supply_df = supplyData.copy().sort_values(by='Date')
        fig = go.Figure()
        for idx, fac in enumerate(facilities):
            sub_df = supply_df[supply_df['Facility_Location'] == fac]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'],
                y=sub_df['Quality_Score_Pct'],
                name=fac.replace('_', ' '),
                mode='lines',
                line=dict(color=fac_colors[idx], width=1.5)
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Quality (%)", yaxis=dict(range=[88, 98]))
        st.plotly_chart(style_plotly_fig(fig, "Quality Score Trend by Facility", height=320), use_container_width=True)
        
    with t4_col2:
        # Production volume growth
        fig = go.Figure()
        for idx, fac in enumerate(facilities):
            sub_df = supply_df[supply_df['Facility_Location'] == fac]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'],
                y=sub_df['Monthly_Production_Volume'],
                name=fac.replace('_', ' '),
                mode='lines',
                line=dict(color=fac_colors[idx], width=1.5),
                fill='none'
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Units")
        st.plotly_chart(style_plotly_fig(fig, "Production Volume Growth", height=320), use_container_width=True)

    t4_b1, t4_b2, t4_b3 = st.columns(3)
    
    with t4_b1:
        # Supply Chain Disruptions
        disrupt = supplyData.groupby('Facility_Location')['Supply_Chain_Disruptions'].mean().reset_index()
        fig = px.bar(
            disrupt,
            x=disrupt['Facility_Location'].str.replace('_', ' '),
            y='Supply_Chain_Disruptions',
            color='Facility_Location',
            color_discrete_sequence=[COLORS['blue'], COLORS['emerald'], COLORS['amber'], COLORS['rose'], COLORS['purple']]
        )
        fig.update_layout(showlegend=False, xaxis_title="Facility", yaxis_title="Avg Disruptions/Month")
        st.plotly_chart(style_plotly_fig(fig, "Supply Chain Disruptions", height=280), use_container_width=True)
        
    with t4_b2:
        # Inventory Turnover
        turnover = supplyData.groupby('Facility_Location')['Inventory_Turnover'].mean().reset_index()
        fig = px.bar(
            turnover,
            x=turnover['Facility_Location'].str.replace('_', ' '),
            y='Inventory_Turnover',
            color='Facility_Location',
            color_discrete_sequence=[COLORS['blue'], COLORS['emerald'], COLORS['amber'], COLORS['rose'], COLORS['purple']]
        )
        fig.update_layout(showlegend=False, xaxis_title="Facility", yaxis_title="Turns/Year")
        st.plotly_chart(style_plotly_fig(fig, "Inventory Turnover Comparison", height=280), use_container_width=True)
        
    with t4_b3:
        # Carbon Footprint
        carbon = supplyData.groupby('Facility_Location')['Carbon_Footprint_MT'].mean().reset_index()
        fig = px.bar(
            carbon,
            x=carbon['Facility_Location'].str.replace('_', ' '),
            y='Carbon_Footprint_MT',
            color='Facility_Location',
            color_discrete_sequence=[COLORS['blue'], COLORS['emerald'], COLORS['amber'], COLORS['rose'], COLORS['purple']]
        )
        fig.update_layout(showlegend=False, xaxis_title="Facility", yaxis_title="Metric Tons")
        st.plotly_chart(style_plotly_fig(fig, "Carbon Footprint by Facility", height=280), use_container_width=True)


# ─── Tab 5: People ───
with dash_tabs[4]:
    t5_col1, t5_col2 = st.columns(2)
    
    with t5_col1:
        # Retention Rate by Level and Division
        fig = go.Figure()
        for idx, dept in enumerate(depts):
            sub_df = hr_latest[hr_latest['Department'] == dept]
            sub_df = sub_df.set_index('Employee_Level').reindex(levels).reset_index()
            fig.add_trace(go.Bar(
                x=levels,
                y=sub_df['Retention_Rate_Pct'],
                name=dept.replace('Wayne ', ''),
                marker_color=hr_colors[idx]
            ))
        fig.update_layout(barmode='group', xaxis_title="Employee Level", yaxis_title="% Retention", yaxis=dict(range=[85, 102]))
        st.plotly_chart(style_plotly_fig(fig, "Retention Rate by Level & Division", height=320), use_container_width=True)
        
    with t5_col2:
        # Employee Satisfaction Trend
        hr_entry = hr_df[hr_df['Employee_Level'] == 'Entry Level'].sort_values('Date')
        dates = hr_entry['Date'].unique()
        dates_subset = dates[::2]  # select every second date
        
        fig = go.Figure()
        for idx, dept in enumerate(depts):
            sub_df = hr_entry[hr_entry['Department'] == dept]
            sub_df = sub_df[sub_df['Date'].isin(dates_subset)]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'].str.slice(0, 7),
                y=sub_df['Employee_Satisfaction_Score'],
                name=dept.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=hr_colors[idx])
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Satisfaction Score", yaxis=dict(range=[6, 10]))
        st.plotly_chart(style_plotly_fig(fig, "Employee Satisfaction Trend", height=320), use_container_width=True)

    t5_b1, t5_b2 = st.columns(2)
    
    with t5_b1:
        # Diversity Index Progress
        fig = go.Figure()
        for idx, dept in enumerate(depts):
            sub_df = hr_entry[hr_entry['Department'] == dept]
            sub_df = sub_df[sub_df['Date'].isin(dates_subset)]
            fig.add_trace(go.Scatter(
                x=sub_df['Date'].str.slice(0, 7),
                y=sub_df['Diversity_Index'],
                name=dept.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=hr_colors[idx])
            ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Diversity Index", yaxis=dict(range=[0.6, 1.0]))
        st.plotly_chart(style_plotly_fig(fig, "Diversity Index Progress", height=300), use_container_width=True)
        
    with t5_b2:
        # Training Hours vs Performance scatter
        fig = go.Figure()
        for idx, dept in enumerate(depts):
            sub_df = hr_latest[hr_latest['Department'] == dept]
            fig.add_trace(go.Scatter(
                x=sub_df['Training_Hours_Annual'],
                y=sub_df['Performance_Rating'],
                name=dept.replace('Wayne ', ''),
                mode='markers',
                marker=dict(color=hr_colors[idx], size=12, line=dict(width=1, color='#ffffff'))
            ))
        fig.update_layout(xaxis_title="Training Hours", yaxis_title="Performance Rating")
        st.plotly_chart(style_plotly_fig(fig, "Training Hours vs Performance Rating", height=300), use_container_width=True)


# ─── Tab 6: Cross-Insights ───
with dash_tabs[5]:
    t6_col1, t6_col2 = st.columns(2)
    
    with t6_col1:
        # R&D Investment vs Revenue Growth Correlation (Dual Y-Axis)
        fin_grouped = financialData.sort_values(by=['Year', 'Quarter'])
        quarters_labels = ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24', 'Q2 24', 'Q3 24', 'Q4 24']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            sub_df = fin_grouped[fin_grouped['Division'] == div]
            fig.add_trace(go.Scatter(
                x=quarters_labels,
                y=sub_df['Revenue_M'],
                name=f"{div.replace('Wayne ', '')} Revenue",
                mode='lines',
                line=dict(color=div_colors[idx])
            ), secondary_y=False)
            fig.add_trace(go.Scatter(
                x=quarters_labels,
                y=sub_df['RD_Investment_M'],
                name=f"{div.replace('Wayne ', '')} R&D",
                mode='lines',
                line=dict(color=div_colors[idx], dash='dash')
            ), secondary_y=True)
            
        fig.update_layout(xaxis_title="Quarter")
        fig.update_yaxes(title_text="Revenue ($M)", secondary_y=False)
        fig.update_yaxes(title_text="R&D ($M)", secondary_y=True)
        st.plotly_chart(style_plotly_fig(fig, "R&D Investment vs Revenue Growth Correlation", height=320), use_container_width=True)
        
    with t6_col2:
        # Community Engagement vs Crime Reduction
        sec_latest = securityData.sort_values(by='Date').groupby('District').last().reset_index()
        fig = go.Figure()
        for idx, dist in enumerate(districts):
            rec = sec_latest[sec_latest['District'] == dist]
            fig.add_trace(go.Scatter(
                x=rec['Community_Engagement_Events'],
                y=rec['Security_Incidents'],
                name=dist,
                mode='markers',
                marker=dict(color=dist_colors[idx], size=16, line=dict(width=1, color='#ffffff'))
            ))
        fig.update_layout(xaxis_title="Community Events/Month", yaxis_title="Security Incidents", yaxis=dict(range=[0, 100]))
        st.plotly_chart(style_plotly_fig(fig, "Community Engagement vs Crime Reduction", height=320), use_container_width=True)

    t6_b1, t6_b2 = st.columns(2)
    
    with t6_b1:
        # Employee Satisfaction vs Product Quality
        fig = go.Figure()
        for idx, dept in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences']):
            avg_sat = hrData[hrData['Department'] == dept]['Employee_Satisfaction_Score'].mean()
            fac = 'Gotham_Main' if dept == 'Wayne Aerospace' else 'Metropolis_North' if dept == 'Wayne Biotech' else 'Central_City'
            avg_qual = supplyData[supplyData['Facility_Location'] == fac]['Quality_Score_Pct'].mean()
            
            fig.add_trace(go.Scatter(
                x=[avg_sat],
                y=[avg_qual],
                name=dept.replace('Wayne ', ''),
                mode='markers',
                marker=dict(color=hr_colors[idx], size=20, line=dict(width=2, color='#ffffff'))
            ))
        fig.update_layout(xaxis_title="Avg Employee Satisfaction", yaxis_title="Avg Product Quality (%)", xaxis=dict(range=[7.0, 10.0]), yaxis=dict(range=[90.0, 98.0]))
        st.plotly_chart(style_plotly_fig(fig, "Employee Satisfaction vs Product Quality", height=300), use_container_width=True)
        
    with t6_b2:
        # Operational Efficiency Radar
        fig = go.Figure()
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            div_fin = financialData[financialData['Division'] == div].sort_values(by=['Year', 'Quarter'])
            first = div_fin.iloc[0]
            last = div_fin.iloc[-1]
            growth = ((last['Revenue_M'] - first['Revenue_M']) / first['Revenue_M']) * 100
            margin = (last['Net_Profit_M'] / last['Revenue_M']) * 100
            rd_pct = (last['RD_Investment_M'] / last['Revenue_M']) * 100
            csat = last['Customer_Satisfaction_Score'] * 20  # scale to 100
            
            # get hr retention
            hr_rec = hr_latest[hr_latest['Department'] == div]
            retention = hr_rec['Retention_Rate_Pct'].mean() if not hr_rec.empty else 80.0
            
            fig.add_trace(go.Scatterpolar(
                r=[growth, margin, rd_pct * 8, csat, retention],
                theta=['Revenue Growth', 'Profit Margin', 'R&D Intensity', 'Customer Satisfaction', 'Employee Retention'],
                fill='toself',
                name=div.replace('Wayne ', ''),
                line_color=div_colors[idx]
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
        st.plotly_chart(style_plotly_fig(fig, "Operational Efficiency Radar", height=300), use_container_width=True)


st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 30px; margin-bottom: 40px;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  STRATEGIC OUTLOOK
# ═══════════════════════════════════════════
st.markdown("## Strategic Outlook")
st.markdown("<p style='color:#94a3b8; font-size:1.1rem; margin-top:-10px; margin-bottom:24px;'>Data-driven predictions and strategic recommendations for the next 12–24 months</p>", unsafe_allow_html=True)

outlook_cols = st.columns([5, 7])

with outlook_cols[0]:
    # Prediction Cards
    st.markdown("""
        <div class='glass-card pred-card growth'>
            <h4 style='margin:0; font-size:1.1rem;'>📈 Revenue Will Cross $18B by Q4 2025</h4>
            <p style='color:#94a3b8; font-size:0.85rem; margin-top:6px; line-height:1.5;'>
                Based on current trajectories, Wayne Construction (projected $4.2B) and Aerospace ($2.4B) will drive revenue past $18B. 
                Biotech's gene therapy commercialization could add an upside of $400-600M.
            </p>
            <div class='pred-metric'>$18.2B <span style='font-size:0.85rem; color:#94a3b8;'>Projected FY2025</span></div>
        </div>
        
        <div class='glass-card pred-card risk'>
            <h4 style='margin:0; font-size:1.1rem;'>⚠️ The Narrows Needs a $50M Intervention</h4>
            <p style='color:#94a3b8; font-size:0.85rem; margin-top:6px; line-height:1.5;'>
                Current decline rates suggest The Narrows won't reach safety parity for 4+ years. 
                Deploying 50+ additional Tech units and doubling community events could close the gap by 2026.
            </p>
            <div class='pred-metric'>$50M <span style='font-size:0.85rem; color:#94a3b8;'>Recommended Budget</span></div>
        </div>
        
        <div class='glass-card pred-card opportunity'>
            <h4 style='margin:0; font-size:1.1rem;'>🔬 3 R&D Projects Ready for Commercialization</h4>
            <p style='color:#94a3b8; font-size:0.85rem; margin-top:6px; line-height:1.5;'>
                Gene Therapy Platform (96.8%), Smart City Infrastructure (88.4%), and Quantum Computer Chip (82.6%) are approaching commercialization.
            </p>
            <div class='pred-metric'>$2.1B <span style='font-size:0.85rem; color:#94a3b8;'>Estimated Opportunity</span></div>
        </div>
    """, unsafe_allow_html=True)
    
with outlook_cols[1]:
    # Forecasts Side-by-Side
    sub_col1, sub_col2 = st.columns(2)
    
    with sub_col1:
        # Revenue Forecast Chart
        all_labels = ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24', 'Q2 24', 'Q3 24', 'Q4 24', 'Q1 25', 'Q2 25', 'Q3 25', 'Q4 25']
        fig = go.Figure()
        for idx, div in enumerate(['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction']):
            sub_df = financialData[financialData['Division'] == div].sort_values(by=['Year', 'Quarter'])
            hist_data = sub_df['Revenue_M'].tolist()
            
            # Simple linear forecast
            last4 = hist_data[-4:]
            growth_rate = (last4[3] - last4[0]) / last4[0]
            quarterly = growth_rate / 3
            
            base_rev = last4[3]
            forecast = []
            for q in range(4):
                base_rev = base_rev * (1 + quarterly * 0.9)
                forecast.append(round(base_rev, 1))
                
            full_series = hist_data + forecast
            
            # Historical line
            fig.add_trace(go.Scatter(
                x=all_labels[:8],
                y=full_series[:8],
                name=div.replace('Wayne ', ''),
                mode='lines+markers',
                line=dict(color=div_colors[idx], width=2)
            ))
            # Forecast dashed line
            fig.add_trace(go.Scatter(
                x=all_labels[7:],
                y=full_series[7:],
                showlegend=False,
                mode='lines+markers',
                line=dict(color=div_colors[idx], width=2, dash='dash'),
                marker=dict(symbol='triangle-up', size=6)
            ))
        fig.update_layout(xaxis_title="Quarter", yaxis_title="Revenue ($M)")
        st.plotly_chart(style_plotly_fig(fig, "Revenue Forecast 2025 ($M)", height=320), use_container_width=True)
        
    with sub_col2:
        # Security Incident Forecast
        sec_dates = sorted(securityData['Date'].unique())
        sec_labels = [d[:7] for d in sec_dates]
        forecast_months = ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
        all_sec_labels = sec_labels + forecast_months
        
        fig = go.Figure()
        for idx, dist in enumerate(['Bristol', 'Downtown', 'The Narrows']):
            dist_data = securityData[securityData['District'] == dist].sort_values('Date')['Security_Incidents'].tolist()
            
            last6 = dist_data[-6:]
            monthly_decline = (last6[0] - last6[-1]) / 6
            
            # ✔ Fix 2: Isolated 'current_base' to separate namespacing from outer references
            current_base = last6[-1]
            forecast = []
            for m in range(6):
                current_base = max(0, current_base - monthly_decline * 0.8)
                forecast.append(round(current_base))
                
            full_series = dist_data + forecast
            
            # Historical line
            fig.add_trace(go.Scatter(
                x=all_sec_labels[:len(dist_data)],
                y=full_series[:len(dist_data)],
                name=dist,
                mode='lines',
                line=dict(color=dist_colors[districts.index(dist)], width=2)
            ))
            # Forecast dashed line
            fig.add_trace(go.Scatter(
                x=all_sec_labels[len(dist_data)-1:],
                y=full_series[len(dist_data)-1:],
                showlegend=False,
                mode='lines',
                line=dict(color=dist_colors[districts.index(dist)], width=2, dash='dash')
            ))
        fig.update_layout(xaxis_title="Month", yaxis_title="Incidents")
        st.plotly_chart(style_plotly_fig(fig, "Security Incident Forecast (Next 6 Months)", height=320), use_container_width=True)

# Strategic Insight Callout
st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.08); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px 24px; margin-top: 24px; display: flex; align-items: flex-start; gap: 16px;'>
        <div style='font-size: 1.5rem;'>💡</div>
        <div style='font-size: 0.9rem; line-height: 1.5; color: #cbd5e1;'>
            <strong>CEO Action Item:</strong> The strongest signal in the data is that <strong>community investment drives security outcomes better than technology deployment alone</strong>. 
            Bristol's success (26 events/month → zero crime) vs. The Narrows (14 events → 60 incidents) suggests reallocating 20% of tech deployment budget toward community programs 
            could yield disproportionate returns. Similarly, the tight correlation between employee satisfaction and product quality suggests that HR investment is fundamentally an operational quality strategy.
        </div>
    </div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════
st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 50px; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>Wayne Enterprises · Board-Level Analytics Report · Prepared Q4 2024 · Confidential</p>", unsafe_allow_html=True)
