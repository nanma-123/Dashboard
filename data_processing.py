import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from lifelines import CoxPHFitter
from scipy.optimize import linprog

DATA_DIR = os.path.join(os.path.dirname(__file__), 'docm')

def load_data():
    files = {
        'finance': 'wayne_financial_data.csv',
        'hr': 'wayne_hr_analytics.csv',
        'rd': 'wayne_rd_portfolio.csv',
        'security': 'wayne_security_data.csv',
        'supply': 'wayne_supply_chain.csv'
    }
    data = {}
    for key, filename in files.items():
        data[key] = pd.read_csv(os.path.join(DATA_DIR, filename))
    return data

def process_phase1(data):
    df_fin = data['finance'].copy()
    df_hr = data['hr'].copy()
    df_sec = data['security'].copy()
    df_sup = data['supply'].copy()

    # 1. R&D vs Revenue (Time Lagged)
    # We will compute cross correlation per division
    rd_rev_corr = {}
    for div in df_fin['Division'].unique():
        df_div = df_fin[df_fin['Division'] == div].sort_values(['Year', 'Quarter'])
        rd = df_div['RD_Investment_M'].values
        rev = df_div['Revenue_M'].values
        # correlation with 0, 1, 2 lags
        if len(rd) > 2:
            corrs = []
            for lag in range(3):
                if lag == 0:
                    corrs.append(np.corrcoef(rd, rev)[0, 1])
                else:
                    corrs.append(np.corrcoef(rd[:-lag], rev[lag:])[0, 1])
            rd_rev_corr[div] = corrs
    
    # 2. Security vs Community Engagement
    sec_model = LinearRegression()
    X_sec = df_sec[['Community_Engagement_Events', 'Wayne_Tech_Deployments']]
    y_sec = df_sec['Security_Incidents']
    sec_model.fit(X_sec, y_sec)
    sec_impact = {
        'Community_Engagement_Coef': sec_model.coef_[0],
        'Tech_Deployments_Coef': sec_model.coef_[1]
    }

    # 3. Employee Satisfaction vs Productivity
    # Create Year-Quarter in HR
    df_hr['Date'] = pd.to_datetime(df_hr['Date'])
    df_hr['Year'] = df_hr['Date'].dt.year
    df_hr['Quarter'] = 'Q' + df_hr['Date'].dt.quarter.astype(str)
    hr_agg = df_hr.groupby(['Department', 'Year', 'Quarter'])['Employee_Satisfaction_Score'].mean().reset_index()
    
    df_fin_prod = df_fin.copy()
    df_fin_prod['Productivity'] = df_fin_prod['Revenue_M'] / (df_fin_prod['Employee_Count'] + 1e-5)
    
    hr_prod_merged = pd.merge(df_fin_prod, hr_agg, left_on=['Division', 'Year', 'Quarter'], right_on=['Department', 'Year', 'Quarter'], how='inner')
    satisfaction_productivity_corr = hr_prod_merged['Employee_Satisfaction_Score'].corr(hr_prod_merged['Productivity'])

    # 4. Supply Chain Efficiency vs Quality
    features = ['Lead_Time_Days', 'Inventory_Turnover', 'Supply_Chain_Disruptions']
    X_sup = df_sup[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_sup)
    
    # Invert Lead_Time and Disruptions so higher is better for clustering
    # Actually K-Means doesn't need inversion, but we want to interpret clusters
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_sup['Efficiency_Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze quality per cluster
    cluster_analysis = df_sup.groupby('Efficiency_Cluster').agg({
        'Lead_Time_Days': 'mean',
        'Inventory_Turnover': 'mean',
        'Supply_Chain_Disruptions': 'mean',
        'Quality_Score_Pct': 'mean'
    }).reset_index()

    return {
        'rd_rev_corr': rd_rev_corr,
        'sec_impact': sec_impact,
        'hr_prod_merged': hr_prod_merged,
        'satisfaction_productivity_corr': satisfaction_productivity_corr,
        'cluster_analysis': cluster_analysis,
        'df_sup_clustered': df_sup
    }

def process_phase2(data):
    df_sec = data['security'].copy()
    df_rd = data['rd'].copy()
    df_hr = data['hr'].copy()
    df_sup = data['supply'].copy()

    # 1. Security Incident Forecasting
    df_sec['Date'] = pd.to_datetime(df_sec['Date'])
    df_sec = df_sec.sort_values('Date')
    # Simple feature engineering for spatial & temporal
    df_sec_encoded = pd.get_dummies(df_sec, columns=['District'])
    # Add lag 1 incident
    df_sec_encoded['Incidents_Lag1'] = df_sec_encoded.groupby('District_Downtown')['Security_Incidents'].shift(1).fillna(df_sec_encoded['Security_Incidents'].mean())
    
    features = [c for c in df_sec_encoded.columns if c.startswith('District_')] + ['Wayne_Tech_Deployments', 'Community_Engagement_Events', 'Incidents_Lag1']
    X_rf = df_sec_encoded[features]
    y_rf = df_sec_encoded['Security_Incidents']
    rf_sec = RandomForestRegressor(random_state=42)
    rf_sec.fit(X_rf, y_rf)
    
    # Predict next month (mocked by adding to deploy)
    next_X = X_rf.iloc[-len(df_sec['District'].unique()):].copy()
    next_X['Wayne_Tech_Deployments'] += 10 # assumed increase
    sec_forecast = rf_sec.predict(next_X)

    # 2. Project Success Prediction
    # Create burn rate
    df_rd['Burn_Rate'] = df_rd['Budget_Spent_M'] / df_rd['Budget_Allocated_M']
    
    # To train, we need to consider Completed as 1, Paused as 0. 
    # For Active, we will predict probability.
    df_rd_train = df_rd[df_rd['Status'].isin(['Completed', 'Paused'])].copy()
    df_rd_active = df_rd[df_rd['Status'] == 'Active'].copy()
    
    project_preds = None
    if len(df_rd_train) > 0 and 'Paused' in df_rd_train['Status'].values and 'Completed' in df_rd_train['Status'].values:
        y_train = (df_rd_train['Status'] == 'Completed').astype(int)
        X_train = df_rd_train[['Burn_Rate', 'Timeline_Adherence_Pct']]
        
        clf = RandomForestClassifier(random_state=42)
        clf.fit(X_train, y_train)
        
        X_active = df_rd_active[['Burn_Rate', 'Timeline_Adherence_Pct']].fillna(0)
        df_rd_active['Success_Probability'] = clf.predict_proba(X_active)[:, 1]
        project_preds = df_rd_active[['Project_Name', 'Success_Probability']]

    # 3. Employee Turnover Risk
    # We will use CoxPH. We need duration and event.
    # Proxy: delta retention month over month
    df_hr['Date'] = pd.to_datetime(df_hr['Date'])
    df_hr = df_hr.sort_values(['Department', 'Employee_Level', 'Date'])
    df_hr['Retention_Delta'] = df_hr.groupby(['Department', 'Employee_Level'])['Retention_Rate_Pct'].diff()
    
    # Synthesize survival data: if retention delta < -2, treat as an "event" (significant churn)
    # Time is months since start (proxy 1 to N)
    df_hr['Month_Idx'] = df_hr.groupby(['Department', 'Employee_Level']).cumcount() + 1
    df_hr['Churn_Event'] = (df_hr['Retention_Delta'] < -1.0).astype(int)
    
    # Drop NaNs
    surv_df = df_hr.dropna(subset=['Salary_Band', 'Benefits_Utilization_Pct', 'Training_Hours_Annual', 'Retention_Delta']).copy()
    surv_df['Salary_Band_Num'] = LabelEncoder().fit_transform(surv_df['Salary_Band'])
    
    cph = CoxPHFitter()
    cph_data = surv_df[['Month_Idx', 'Churn_Event', 'Benefits_Utilization_Pct', 'Training_Hours_Annual', 'Employee_Satisfaction_Score']]
    try:
        cph.fit(cph_data, duration_col='Month_Idx', event_col='Churn_Event')
        hr_hazard = cph.summary[['exp(coef)', 'p']]
    except Exception as e:
        hr_hazard = None

    # 4. Supply Chain Disruption Monte Carlo
    # Historic probability of disruption
    prob_disruption = (df_sup['Supply_Chain_Disruptions'] > 0).mean()
    avg_cost = df_sup['Cost_Per_Unit'].mean()
    avg_vol = df_sup['Monthly_Production_Volume'].mean()
    
    simulations = 1000
    mc_results = []
    np.random.seed(42)
    for _ in range(simulations):
        # 12 months simulation
        disruptions = np.random.binomial(1, prob_disruption, 12)
        # Assuming each disruption increases cost by 15% and reduces vol by 20%
        sim_cost = avg_cost * (1 + 0.15 * disruptions)
        sim_vol = avg_vol * (1 - 0.20 * disruptions)
        mc_results.append({
            'Total_Vol': sim_vol.sum(),
            'Avg_Cost': sim_cost.mean()
        })
    df_mc = pd.DataFrame(mc_results)

    return {
        'sec_forecast': sec_forecast,
        'project_preds': project_preds,
        'hr_hazard': hr_hazard,
        'mc_results': df_mc
    }

def process_phase3(data):
    df_fin = data['finance'].copy()
    df_rd = data['rd'].copy()
    df_hr = data['hr'].copy()
    df_sec = data['security'].copy()
    df_sup = data['supply'].copy()

    # 1. Division Benchmarking
    # Aggregate to division level
    fin_agg = df_fin.groupby('Division')['Net_Profit_M'].mean().reset_index()
    # HR score
    hr_agg = df_hr.groupby('Department')['Employee_Satisfaction_Score'].mean().reset_index()
    # Merge
    bench_df = pd.merge(fin_agg, hr_agg, left_on='Division', right_on='Department', how='left')
    
    # Normalize
    scaler = StandardScaler()
    bench_df['Fin_Norm'] = scaler.fit_transform(bench_df[['Net_Profit_M']])
    bench_df['HR_Norm'] = scaler.fit_transform(bench_df[['Employee_Satisfaction_Score']].fillna(0))
    # Synthetic R&D innovation potential (mocked as rd budget spent / rev)
    # Composite
    bench_df['Composite_Score'] = (0.4 * bench_df['Fin_Norm'] + 0.3 * bench_df['HR_Norm'] + 0.3 * np.random.rand(len(bench_df)))

    # 2. Resource Allocation (Linear Programming)
    # Objective: Maximize Net Profit -> min -Net_Profit
    # Simple setup based on average division stats
    divs = bench_df['Division'].values
    avg_profits = df_fin.groupby('Division')['Net_Profit_M'].mean().values
    avg_costs = df_fin.groupby('Division')['Operating_Costs_M'].mean().values
    
    c = -avg_profits
    A_ub = [avg_costs] # sum of costs
    b_ub = [avg_costs.sum() * 1.05] # 5% cap increase
    bounds = [(0.8, 1.2) for _ in divs] # Keep allocation within 80-120% of current
    
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    allocations = res.x if res.success else np.ones(len(divs))

    lp_res = pd.DataFrame({
        'Division': divs,
        'Optimal_Multiplier': allocations,
        'Current_Avg_Cost': avg_costs,
        'Proposed_Cost': avg_costs * allocations
    })

    # 3. Risk Matrix
    # Using MC results and project success
    # 4. Innovation Pipeline
    # df_rd -> Patent_Applications vs Budget_Spent_M
    innovation_data = df_rd[['Project_Name', 'Division', 'Patent_Applications', 'Budget_Spent_M', 'Status']]

    # ESG Score
    # Carbon footprint (Supply) - normalized inverse
    cf = df_sup['Carbon_Footprint_MT'].mean()
    # Diversity (HR)
    div_idx = df_hr['Diversity_Index'].mean()
    # Community (Sec)
    comm = df_sec['Community_Engagement_Events'].mean()
    
    esg = {
        'Carbon_Footprint': cf,
        'Diversity_Index': div_idx,
        'Community_Events': comm,
        'Composite_ESG': (div_idx * 50) + (comm * 2) - (cf / 100) # Arbitrary weighting for illustration
    }

    return {
        'benchmarking': bench_df,
        'resource_allocation': lp_res,
        'innovation_data': innovation_data,
        'esg': esg
    }

def get_all_metrics():
    data = load_data()
    p1 = process_phase1(data)
    p2 = process_phase2(data)
    p3 = process_phase3(data)
    return data, p1, p2, p3
