import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_portfolio_summary():
    # Setup paths
    output_dir = os.path.abspath("reports/portfolio")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "portfolio_summary.pdf")
    
    # Connect and fetch data
    conn = sqlite3.connect("data/nifty100.db")
    query = """
    SELECT fr.company_id, c.sector, fr.return_on_equity_pct, fr.debt_to_equity, 
           fr.free_cash_flow_cr, fr.capex_intensity_label
    FROM financial_ratios fr
    JOIN companies c ON fr.company_id = c.name
    WHERE fr.year = (SELECT MAX(year) FROM financial_ratios)
    ORDER BY fr.company_id ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Generate PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Nifty 100 Master Portfolio Summary", styles['Title']), Spacer(1, 12)]
    
    for _, row in df.iterrows():
        story.append(Paragraph(f"Company: {row['company_id']}", styles['Heading2']))
        story.append(Paragraph(f"Sector: {row['sector']}", styles['Normal']))
        story.append(Paragraph(f"ROE: {row['return_on_equity_pct']:.2f}% | D/E: {row['debt_to_equity']:.2f}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    doc.build(story)
    print(f"✅ Success! Master Portfolio Summary generated: {pdf_path}")

if __name__ == "__main__":
    generate_portfolio_summary()