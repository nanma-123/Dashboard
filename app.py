import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_processing import get_all_metrics

# --- Configuration & Styling ---
st.set_page_config(page_title="Wayne Enterprises Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Playfair+Display:wght@400;600;700;900&display=swap" rel="stylesheet"><style>
    html, body, [class*="css"] { font-family: 'Playfair Display', serif !important; background-color: #FAFAFA !important; color: #1e293b !important; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Playfair Display', serif !important; color: #0f172a !important; font-weight: 700 !important; }
    header {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }
    
    .metric-card { background: #FFFFFF; border-radius: 12px; padding: 24px; text-align: left; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .metric-title { font-size: 1.05rem; color: #64748b; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; }
    .metric-value { font-size: 2.6rem; font-weight: 700; color: #0f172a; margin: 0; }
    
    /* Highlighted Tab Navigation Bar */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; 
        justify-content: center; 
        margin-top: 50px; 
        margin-bottom: 40px; 
        background-color: #f1f5f9; 
        padding: 24px 32px; 
        border-radius: 20px; 
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent !important; 
        border-radius: 16px !important; 
        padding: 20px 60px; 
        transition: all 0.3s ease-in-out;
        height: auto;
        border: none !important;
        outline: none !important;
    }
    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:active {
        background-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab"] p {
        font-weight: 800 !important; 
        font-size: 2.2rem !important; 
        color: #64748b !important; 
        margin: 0;
        transition: color 0.3s ease-in-out;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { 
        background-color: #0f172a !important; 
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.4) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p,
    .stTabs [data-baseweb="tab"][aria-selected="true"] span {
        color: #FFFFFF !important; 
    }
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover p {
        color: #0f172a !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
        background-color: transparent !important;
    }

    /* Newspaper specific CSS for the analysis section */
    .newspaper-sub-header {
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: 5px;
        margin-top: 15px;
        text-transform: uppercase;
        border-bottom: 2px solid #111;
        border-top: 1px solid #111;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .in-charts-badge {
        background-color: #be1e2d;
        color: white;
        padding: 4px 12px;
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 1.5rem;
        display: inline-block;
        margin-right: 15px;
        vertical-align: middle;
        letter-spacing: 1px;
    }
    .deep-dive-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        text-transform: uppercase;
        vertical-align: middle;
        display: inline-block;
        letter-spacing: 1px;
    }
    .intro-paragraph {
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        max-width: 900px;
        margin: 20px auto 30px auto;
        line-height: 1.6;
        color: #333;
    }
    .intro-paragraph b {
        font-weight: 900;
        color: #111;
    }
    
    .story-headline {
        font-family: 'Playfair Display', serif;
        font-size: 3.8rem;
        line-height: 1.1;
        margin-bottom: 5px;
        color: #111;
        font-weight: 400;
    }
    .story-category {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        color: #be1e2d;
        text-transform: uppercase;
        font-weight: 900;
        margin-bottom: 2px;
        letter-spacing: 1px;
    }
    .newspaper-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 400;
        line-height: 1.7;
        text-align: left;
        margin-top: 50px;
        color: #334155;
        background-color: #f8fafc;
        padding: 18px;
        border-left: 5px solid #be1e2d;
        border-radius: 8px;
    }
    .newspaper-text strong.lead-in {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        text-transform: uppercase;
        color: #0f172a;
    }
    .newspaper-text strong.intervention {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #be1e2d;
        text-transform: uppercase;
        display: block;
        margin-top: 12px;
        border-top: 1px solid #e2e8f0;
        padding-top: 12px;
    }
    .chart-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.6rem;
        color: #555;
        font-weight: 600;
        margin-bottom: -10px;
        z-index: 10;
        position: relative;
    }
    
    .horizontal-rule {
        border-top: 1px solid #ccc;
        margin: 40px 0;
    }
    .vertical-rule {
        border-right: 1px solid #ccc;
        height: 100%;
        padding-right: 20px;
    }
    .col-padding-left {
        padding-left: 20px;
    }
    
    .big-number {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 7rem;
        color: #be1e2d;
        line-height: 1;
        text-align: center;
        margin: 40px 0 20px 0;
        letter-spacing: -2px;
    }
    .big-number-sub {
        font-size: 3.5rem;
    }
    </style>""", unsafe_allow_html=True)

# Custom Metric Component
def editorial_metric(title, value):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# Helper for Print-Style Plotly Theme
def apply_plotly_theme(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=22, color="#333"),
        title=None, # We use custom headlines
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=22)),
        margin=dict(l=10, r=10, t=20, b=40),
        hoverlabel=dict(bgcolor="white", font_size=22, font_family="Inter"),
        xaxis=dict(automargin=True, title_font=dict(size=22), tickfont=dict(size=20), showgrid=True, gridwidth=1, gridcolor='#e5e7eb', zeroline=False),
        yaxis=dict(automargin=True, title_font=dict(size=22), tickfont=dict(size=20), showgrid=True, gridwidth=1, gridcolor='#e5e7eb', zeroline=False)
    )
    fig.layout.title.text = ""
    return fig

def render_headline(headline, category=None):
    cat_html = f'<div class="story-category">{category}</div>' if category else ''
    st.markdown(f"""
        {cat_html}
        <div class="story-headline">{headline}</div>
    """, unsafe_allow_html=True)

def render_chart_subtitle(subtitle):
    st.markdown(f'<div class="chart-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def render_story_text(insight, intervention_text=None):
    words = insight.split()
    if len(words) > 2:
        lead_in = " ".join(words[:2]).upper()
        rest = " ".join(words[2:])
        insight_html = f'<strong class="lead-in">{lead_in}</strong> {rest}'
    else:
        insight_html = insight

    intervention_html = f'<strong class="intervention">Strategic Intervention:</strong> {intervention_text}' if intervention_text else ''
    
    st.markdown(f"""
        <div class="newspaper-text">
            {insight_html}
            {intervention_html}
        </div>
    """, unsafe_allow_html=True)

def render_big_number(number, subtitle=""):
    st.markdown(f'<div class="big-number">{number}<span class="big-number-sub">{subtitle}</span></div>', unsafe_allow_html=True)


# --- Data Loading ---
@st.cache_data
def load_and_process_data():
    return get_all_metrics()

try:
    with st.spinner("Loading Wayne Analytics Engine..."):
        data, p1, p2, p3 = load_and_process_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

VIBRANT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
MINT_COLORS = ['#274e13', '#6aa84f', '#bf9000', '#cc0000', '#0b5394', '#674ea7']

# ==========================================
# REPORT HEADER (ORIGINAL WAYNE STYLE)
# ==========================================
st.markdown("<div style='display: flex; justify-content: center; align-items: center; margin-top: 20px;'><div style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; width: 75px; height: 75px; display: flex; justify-content: center; align-items: center; border-radius: 16px; margin-right: 24px; font-family: \"Playfair Display\", serif; font-size: 3.8rem; font-weight: 800; box-shadow: 0 6px 12px rgba(0,0,0,0.15); line-height: 1;'>W</div><h1 style='color: #0f172a; font-size: 4.0rem; margin: 0;'>Wayne Enterprises</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.4rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 50px;'>Executive Analytics & Strategic Interventions Report</p>", unsafe_allow_html=True)

# ==========================================
# EXECUTIVE OVERVIEW (Always Visible)
# ==========================================
esg = p3['esg']
col1, col2, col3, col4 = st.columns(4)
with col1: editorial_metric("Composite ESG Score", f"{esg['Composite_ESG']:.1f}")
with col2: editorial_metric("Carbon Footprint", f"{esg['Carbon_Footprint']:.0f} MT")
with col3: editorial_metric("Diversity Index", f"{esg['Diversity_Index']:.2f}")
with col4: editorial_metric("Community Events", f"{esg['Community_Events']:.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# TABS NAVIGATION
# ==========================================
tab_diag, tab_pred, tab_strat = st.tabs(["Diagnostics", "Predictive Analytics", "Strategy"])

# --- TAB 1: Diagnostics ---
with tab_diag:
    st.markdown("<hr class='horizontal-rule'>", unsafe_allow_html=True)
    
    # ROW 1: Revenue & Profit
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="vertical-rule">', unsafe_allow_html=True)
        render_headline("Top Line Drivers", "Financial Operations")
        render_chart_subtitle("Sum of Revenue by Division ($M)")
        df_fin_agg = data['finance'].groupby('Division')['Revenue_M'].sum().reset_index()
        df_fin_agg = df_fin_agg.sort_values('Revenue_M', ascending=True)
        fig_rev = px.funnel(df_fin_agg, y='Division', x='Revenue_M', color='Division', color_discrete_sequence=MINT_COLORS)
        st.plotly_chart(apply_plotly_theme(fig_rev), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "THE FUNNEL CHART illustrates Wayne Construction and Aerospace dominate top-line revenue. An analysis of cumulative revenue across divisions shows that infrastructure and defense contracts heavily outweigh biotechnology and applied sciences in absolute dollar terms.",
            "Double down on scalable infrastructure projects while exploring high-margin pivot opportunities for Biotech."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="col-padding-left">', unsafe_allow_html=True)
        render_headline("Bottom Line Realities", "Profitability")
        render_chart_subtitle("Sum of Net Profit by Division ($M)")
        df_prof_agg = data['finance'].groupby('Division')['Net_Profit_M'].sum().reset_index()
        df_prof_agg = df_prof_agg.sort_values('Net_Profit_M', ascending=False)
        fig_prof = go.Figure(go.Waterfall(
            name="Profit", orientation="v",
            measure=["relative"] * len(df_prof_agg),
            x=df_prof_agg['Division'],
            y=df_prof_agg['Net_Profit_M'],
            textposition="outside",
            text=[f"${v:,.0f}M" for v in df_prof_agg['Net_Profit_M']],
            decreasing={"marker":{"color":MINT_COLORS[3]}},
            increasing={"marker":{"color":MINT_COLORS[0]}},
            totals={"marker":{"color":MINT_COLORS[4]}}
        ))
        st.plotly_chart(apply_plotly_theme(fig_prof), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "THE WATERFALL CHART breaks down net profit margins, revealing where the true enterprise value lies. Even though some divisions show massive revenue, operating costs significantly reduce their net contribution. Wayne Foundation operates at a slight deficit, while Wayne Construction remains the most profitable engine.",
            "Investigate cost overruns in applied sciences to bring profit margins closer to the corporate average."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='horizontal-rule'>", unsafe_allow_html=True)

    # ROW 2: R&D Budget & Supply Chain Carbon
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="vertical-rule">', unsafe_allow_html=True)
        render_headline("Capital Burn", "R&D Economics")
        render_chart_subtitle("Budget Allocated vs Spent by Division ($M)")
        df_rd_agg = data['rd'].groupby('Division')[['Budget_Allocated_M', 'Budget_Spent_M']].sum().reset_index()
        fig_rd = px.scatter(df_rd_agg, x='Budget_Allocated_M', y='Budget_Spent_M', size='Budget_Allocated_M', color='Division', text='Division', size_max=40, color_discrete_sequence=MINT_COLORS)
        fig_rd.update_traces(textposition='top center')
        fig_rd.add_shape(type="line", line=dict(dash='dash', color='gray'), x0=0, y0=0, x1=df_rd_agg['Budget_Allocated_M'].max()*1.1, y1=df_rd_agg['Budget_Allocated_M'].max()*1.1)
        st.plotly_chart(apply_plotly_theme(fig_rd), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "THIS SCATTER PLOT maps actual budget spent against allocated capital. The dashed reference line represents 100% utilization. Divisions falling far below the line show a massive gap between allocated capital and actual deployed capital, suggesting bottlenecks in pipeline execution.",
            "Reallocate stagnant capital from under-spending divisions to high-velocity projects in Aerospace."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="col-padding-left">', unsafe_allow_html=True)
        render_headline("Environmental Toll", "Supply Chain ESG")
        render_chart_subtitle("Average Carbon Footprint by Facility Location (MT)")
        df_sup_agg = data['supply'].groupby('Facility_Location')['Carbon_Footprint_MT'].mean().reset_index()
        df_sup_agg = df_sup_agg.sort_values('Carbon_Footprint_MT', ascending=True)
        fig_cf = px.bar(df_sup_agg, x='Carbon_Footprint_MT', y='Facility_Location', orientation='h', color='Facility_Location', color_discrete_sequence=MINT_COLORS)
        st.plotly_chart(apply_plotly_theme(fig_cf), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "THE BAR CHART visually weights the environmental impact. The large geographic block for Star City facilities highlights severe inefficiencies in our manufacturing hubs compared to smaller contributors like Keystone City.",
            "Accelerate the rollout of green-energy retrofits specifically targeting Star City manufacturing centers."
        )
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Predictive Analytics ---
with tab_pred:
    st.markdown("<hr class='horizontal-rule'>", unsafe_allow_html=True)

    # ROW 3: Threat Forecasting & Innovation Probabilities
    c5, c6 = st.columns(2)
    with c5:
        st.markdown('<div class="vertical-rule">', unsafe_allow_html=True)
        render_headline("Headwinds Ahead?", "Threat Forecasting")
        render_chart_subtitle("Next-Month Security Incident Forecast")
        sec_f = p2['sec_forecast']
        districts = data['security']['District'].unique()
        df_f = pd.DataFrame({'District': districts, 'Forecasted_Incidents': sec_f})
        fig_f = px.bar(df_f, x='District', y='Forecasted_Incidents', color='District', color_discrete_sequence=MINT_COLORS)
        fig_f.update_layout(xaxis=dict(tickangle=-45)) 
        st.plotly_chart(apply_plotly_theme(fig_f), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "RANDOM FOREST modeling anticipates an escalation in The Narrows. Feeding historical crime data, spatial geometries, and technological deployment rates into our regressor allows us to forecast next month's incidents. The algorithm flags a persistent, high-volume threat remaining in specific urban districts.",
            "Pre-emptively stage rapid-response teams in the highest forecasted districts before the start of the next calendar month."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="col-padding-left">', unsafe_allow_html=True)
        render_headline("Strategic Focus", "Innovation Probabilities")
        render_chart_subtitle("Probability of Commercialization (%)")
        df_p = p2['project_preds']
        if df_p is not None:
            top_10 = df_p.sort_values('Success_Probability', ascending=False).head(10)
            fig_p = px.bar(top_10, x='Success_Probability', y='Project_Name', orientation='h', color='Success_Probability', color_continuous_scale='Greys')
            fig_p.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(apply_plotly_theme(fig_p), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "MACHINE LEARNING successfully isolates top viable R&D projects. Not all R&D is created equal. Using historical completion data, we trained a classification model to output the percentage likelihood of success for currently active projects. The model penalizes bloated budgets and rewards rapid prototyping.",
            "Immediately halt funding for projects with a success probability below 30%. Reallocate capital reserves to the top projects to accelerate time-to-market."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='horizontal-rule'>", unsafe_allow_html=True)

    # ROW 4: Human Capital Retention & Supply Chain Risk
    c7, c8 = st.columns(2)
    with c7:
        st.markdown('<div class="vertical-rule">', unsafe_allow_html=True)
        render_headline("Talent Drain", "Human Capital Retention")
        render_chart_subtitle("Turnover Hazard Ratios (< 1.0 Reduces Risk)")
        df_hr_haz = p2['hr_hazard']
        if df_hr_haz is not None:
            df_hr_haz = df_hr_haz.reset_index().rename(columns={'index': 'Feature', 'exp(coef)': 'Hazard_Ratio'})
            name_map = {
                'Benefits_Utilization_Pct': 'Benefits Utilization Rate',
                'Training_Hours_Annual': 'Annual Training Hours',
                'Employee_Satisfaction_Score': 'Employee Satisfaction Score'
            }
            df_hr_haz['Feature'] = df_hr_haz['Feature'].map(name_map).fillna(df_hr_haz['Feature'])
            fig_hr = px.bar(df_hr_haz, x='Hazard_Ratio', y='Feature', orientation='h', color_discrete_sequence=['#be1e2d'])
            fig_hr.add_vline(x=1.0, line_dash="dash", line_color="black")
            st.plotly_chart(apply_plotly_theme(fig_hr), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "COX PROPORTIONAL hazards model decodes turnover drivers. Survival analysis isolates how specific employee benefits and training programs affect the risk of resignation. A Hazard Ratio below 1.0 indicates a reduction in attrition risk. The model proves high Employee Satisfaction is the strongest buffer.",
            "Implement targeted benefits awareness campaigns in departments with declining retention rates."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c8:
        st.markdown('<div class="col-padding-left">', unsafe_allow_html=True)
        render_headline("Hidden Costs", "Supply Chain Shocks")
        render_chart_subtitle("Simulated Distribution of Average Cost Per Unit")
        mc = p2['mc_results']
        fig_mc = px.histogram(mc, x='Avg_Cost', nbins=40, color_discrete_sequence=['#4b5563'])
        fig_mc.add_vline(x=mc['Avg_Cost'].mean(), line_dash="dash", line_color="black")
        fig_mc.add_vline(x=np.percentile(mc['Avg_Cost'], 95), line_dash="solid", line_color="#be1e2d")
        st.plotly_chart(apply_plotly_theme(fig_mc), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "MONTE CARLO simulation exposes massive downside cost risks. By running 1,000 randomized 12-month simulations based on our historical disruption variance, we modeled the worst-case scenarios for supply chain costs. The distribution shows a long tail of catastrophic cost spikes if global logistics fail.",
            "Do not plan for the 'Average Cost'. Build cash reserves to withstand the 95th percentile cost curve to ensure uninterrupted operations during global crises."
        )
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Strategy ---
with tab_strat:
    st.markdown("<hr class='horizontal-rule'>", unsafe_allow_html=True)

    # ROW 5: Resource Optimization & Innovation Efficiency
    c9, c10 = st.columns(2)
    with c9:
        st.markdown('<div class="vertical-rule">', unsafe_allow_html=True)
        render_headline("Capital Allocation", "Resource Optimization")
        render_chart_subtitle("Linear Programming Optimization Table")
        ra = p3['resource_allocation']
        st.markdown("""<style>
        table { font-size: 1.5rem !important; font-family: 'Inter', sans-serif !important; width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 15px !important; text-align: left; border-bottom: 1px solid #ddd; }
        th { font-weight: bold; background-color: #f8fafc; color: #333; }
        </style>""", unsafe_allow_html=True)
        st.table(ra.style.format({'Optimal_Multiplier': "{:.2f}", 'Current_Avg_Cost': "${:.2f}M", 'Proposed_Cost': "${:.2f}M"}))
        render_story_text(
            "LINEAR PROGRAMMING algorithm dictates optimal capital redistribution. We ran an optimization model to maximize enterprise Net Profit, constrained by maximum operating costs and minimum safety requirements. The model explicitly tells us exactly how much to scale each division.",
            "Execute the 'Optimal Multiplier'. If a division's multiplier is 1.20, increase their operating budget by exactly 20% next quarter."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c10:
        st.markdown('<div class="col-padding-left">', unsafe_allow_html=True)
        render_headline("Lean Innovators", "Innovation Efficiency")
        render_chart_subtitle("Patents Generated vs. Budget Spent ($M)")
        ino = p3['innovation_data']
        fig_ino = px.scatter(ino, x='Budget_Spent_M', y='Patent_Applications', color='Division', hover_data=['Project_Name', 'Status'], size_max=15, color_discrete_sequence=MINT_COLORS)
        fig_ino.add_shape(type="rect", x0=ino['Budget_Spent_M'].min(), y0=ino['Patent_Applications'].median(), x1=ino['Budget_Spent_M'].median(), y1=ino['Patent_Applications'].max()*1.1, fillcolor="rgba(16, 185, 129, 0.1)", line_width=0)
        fig_ino.update_layout(xaxis_title="Budget Spent ($M)", yaxis_title="Patent Applications")
        st.plotly_chart(apply_plotly_theme(fig_ino), use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        render_story_text(
            "PLOTTING PATENT applications against Budget Spent reveals highly efficient outliers. The top-left quadrant represents teams generating massive intellectual property while burning minimal cash.",
            "Identify the project managers in the top-left quadrant and promote them to direct underperforming, high-budget projects."
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr class='horizontal-rule'>
<div style="text-align: center; font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #666; margin-top: 20px; padding-bottom: 50px;">
    <i>Data points sourced from Wayne Enterprises Global Operations Matrix. Analytics performed by Fox Applied Sciences.</i>
</div>
""", unsafe_allow_html=True)
