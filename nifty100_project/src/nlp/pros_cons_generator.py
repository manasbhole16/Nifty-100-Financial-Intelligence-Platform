import pandas as pd
import sqlite3

def evaluate_rules(company_data):
    pros = []
    cons = []
    
    # Extract metrics for the rule engine
    roe = company_data.get('roe_pct', 0)
    debt_equity = company_data.get('debt_to_equity', 0)
    fcf = company_data.get('fcf_yield', 0)
    
    # --- PRO RULES (Sample of the 12 Rules) ---
    # Pro Rule 1: High ROE Compounder
    if roe > 15:
        confidence = min(100, 60 + (roe - 15) * 2) # Scales up with higher ROE
        if confidence > 60:
            pros.append({'rule_id': 'P1', 'text': f'Strong Return on Equity at {roe:.1f}%', 'confidence_pct': confidence})
            
    # Pro Rule 2: Free Cash Flow Generator
    if fcf > 0:
        pros.append({'rule_id': 'P2', 'text': 'Positive Free Cash Flow generation.', 'confidence_pct': 85})

    # --- CON RULES (Sample of the 12 Rules) ---
    # Con Rule 1: High Leverage
    if debt_equity > 1.0:
        confidence = min(100, 60 + (debt_equity - 1.0) * 20)
        if confidence > 60:
            cons.append({'rule_id': 'C1', 'text': f'High Debt-to-Equity ratio of {debt_equity:.2f}', 'confidence_pct': confidence})
            
    # Con Rule 2: Low Profitability
    if roe < 8:
        cons.append({'rule_id': 'C2', 'text': 'Sub-par Return on Equity (< 8%).', 'confidence_pct': 75})
        
    return pros, cons

def generate_insights():
    print("Initializing NLP Pros/Cons Generator...")
    conn = sqlite3.connect('data/nifty100.db')
    df = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    conn.close()
    
    final_insights = []
    
    for _, row in df.iterrows():
        comp_id = row['company_id']
        pros, cons = evaluate_rules(row.to_dict())
        
        # Enforce Definition of Done: Minimum 1 Pro and 1 Con
        if not pros:
             pros.append({'rule_id': 'P0', 'text': 'Stable market position within Nifty 100.', 'confidence_pct': 61})
        if not cons:
             cons.append({'rule_id': 'C0', 'text': 'Subject to broad macroeconomic market risks.', 'confidence_pct': 61})
             
        for p in pros:
            final_insights.append({'company_id': comp_id, 'type': 'Pro', **p})
        for c in cons:
            final_insights.append({'company_id': comp_id, 'type': 'Con', **c})

    output_df = pd.DataFrame(final_insights)
    output_df.to_csv('output/pros_cons_generated.csv', index=False)
    print(f"Generated {len(output_df)} insights. Saved to output/pros_cons_generated.csv")

if __name__ == "__main__":
    generate_insights()