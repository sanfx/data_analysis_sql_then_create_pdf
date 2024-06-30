import sys
from datetime import date
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Defining the plotly template.
plotly_template = "presentation"

current_dir = Path(__file__).parent
database_path = current_dir / "sales.db"
output_dir = current_dir / "output"

output_dir.mkdir(parents=True, exist_ok=True)
# Create a connection to the database
conn = sqlite3.connect(database_path)

# Execute the query and load results into a Pandas DataFrame
query = '''
SELECT sale_date, SUM(total_price) as total_sales
FROM sales
GROUP BY sale_date
ORDER BY sale_date ASC
'''

df = pd.read_sql_query(query, conn)
df["sale_date"] = pd.to_datetime(df["sale_date"])
# Set the sale_date column as the index
df = df.set_index('sale_date')
df_monthly = df.resample('ME').sum()

# Map the month number to short month name
df_monthly['month_name'] = df_monthly.index.strftime('%b')
# Create the Plotly figure with text parameter
fig = px.bar(df_monthly,
            x='month_name',
            y='total_sales',
            template=plotly_template,
            text='total_sales')

# Set the layout
fig.update_layout(
    title='Total Sales by Month',
    xaxis_title='Month',
    yaxis_title="Total Sales ($)",
    yaxis_tickprefix="$",
)
# fig.show()
fig.write_image(output_dir / "monthly_sales.png",
                width=1200,
                height=400,
                scale=4)

# query to load the results into a Pandas DataFrame
query = '''
SELECT p.product_name, SUM(s.total_price) as total_sales
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_name
'''
df = pd.read_sql_query(query, conn)
print(df)
# create the Plotly figure with text parameter
fig = px.bar(df,
            x='product_name',
            y='total_sales',
            template=plotly_template,
            text='total_sales')

# Setting the layout for sales figure
fig.update_layout(
    title="Total Sales by Product",
    xaxis_title="Product",
    yaxis_title="Total Sales ($)",
    yaxis_tickprefix="$",
)

#fig.show()

fig.write_image(output_dir / "product_sales.png",
                width=1200,
                height=400,
                scale=4
)
# Query to load the results into a Pandas DataFrame

query = '''
SELECT c.first_name || ' ' || c.last_name as customer_name, SUM(s.total_price) as total_sales
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY customer_name
ORDER BY total_sales DESC
LIMIT 10
'''

df = pd.read_sql_query(query, conn)
print(df)
#  Now lets create a Plotly figure.
fig = px.bar(df,
    x='customer_name',
    y='total_sales',
    template=plotly_template,
    text='total_sales')

# finally I am setting the layout
fig.update_layout(
    title='Top Customers by Sales',
    xaxis_title="Customer",
    yaxis_title="Total Sales ($)",
    yaxis_tickprefix="$",
)

# lets take a look at the plot.
# fig.show()

fig.write_image(output_dir / 'customer_sales.png',
                width=1200,
                height=400,
                scale=4)

conn.close()

# Define the font color as RGB values (dark gray)
font_colour = (64, 64, 64)

# Find all PNG files in the output folder
chart_filenames = [str(chart_path) for chart_path in output_dir.glob("*.png")]

# create a pdf document and set the page size
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 24)

# Add the overall page title.
title = f"Sales Report as of {date.today().strftime('%m/%d/%Y')}"
pdf.set_text_color(*font_colour)
pdf.cell(0, 20, title, align="C", ln=1)

for chart_filename in chart_filenames:
    pdf.ln(10)
    pdf.image(chart_filename, x=None, y=None, w=pdf.w - 20, h=0)

# Save the PDF document to a file on disk
pdf.output(output_dir / " sales_report.pdf", "F")