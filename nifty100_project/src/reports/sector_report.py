import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_sector_reports():
    output_dir = os.path.abspath("reports/sector")
    os.makedirs(output_dir, exist_ok=True)
    
    db_path = "data/nifty100.db"
    conn = sqlite3.connect(db_path)
    
    # FIXED QUERY: Joining sectors table using company_id
    query = """
    SELECT s.broad_sector as sector, fr.company_id, fr.return_on_equity_pct, fr.debt_to_equity, fr.free_cash_flow_cr
    FROM financial_ratios fr
    JOIN sectors s ON fr.company_id = s.company_id
    WHERE fr.year = (SELECT MAX(year) FROM financial_ratios)
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    sectors = df['sector'].dropna().unique()
    print(f"Aggregating indices across {len(sectors)} macroeconomic sectors...")
    
    for sector in sectors:
        sector_df = df[df['sector'] == sector]
        sanitized_name = sector.replace('/', '_').replace(' ', '_')
        pdf_path = os.path.join(output_dir, f"{sanitized_name}_report.pdf")
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = [Paragraph(f"Sector: {sector}", styles['Heading1']), Spacer(1, 12)]
        
        table_data = [['Ticker', 'ROE', 'D/E']]
        for _, row in sector_df.iterrows():
            table_data.append([row['company_id'], f"{row['return_on_equity_pct']:.1f}%", f"{row['debt_to_equity']:.1f}"])
            
        t = Table(table_data)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
        story.append(t)
        doc.build(story)
        print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    generate_sector_reports()
