import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL for the Western Cape dam levels
url = "https://www.dws.gov.za/Hydrology/Weekly/ProvinceWeek.aspx?region=WC"

# Send a request to the webpage
response = requests.get(url)
response.raise_for_status()  # Ensure we notice bad responses

# Sample HTML content from the response text you printed
html_content = response.text

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all table elements
tables = soup.find_all('table')

# Inspect all tables to find the one with the required data
for index, table in enumerate(tables):
    print(f"Table {index}:")

    print("\n")

# Based on inspection, choose the correct table (assuming the required table is at index 1)
# Update the index if a different table contains the data
target_table_index = 4
table = tables[target_table_index]

# Check if the correct table is found
if table is None:
    print("No table found on the webpage.")
else:
    print("Table found.")

    # Print the table content for debugging
    print("Target Table HTML:")
    # print(table.prettify())

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]
    print("Headers:", headers)

    # Extract table rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the first row as it contains headers
        row_data = [td.text.strip() for td in tr.find_all('td')]
        # Check if the number of columns in the row matches the number of headers
        if len(row_data) == len(headers):
            # Exclude 'River', 'Photo', 'Indicators', and 'FSC' columns
            filtered_row_data = [row_data[0], row_data[5], row_data[6], row_data[7]]
            rows.append(filtered_row_data)
    # print("Rows:", rows)

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=['Dam', 'This Week', 'Last Week', 'Last Year'])

    # Export DataFrame to Excel
    df.to_excel('western_cape_dam_levels.xlsx', index=False)










from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)


# Function to read data
def read_data():
    # Assuming data is stored in a CSV or extracted directly from the source as before
    df = pd.read_excel('western_cape_dam_levels.xlsx')
    return df


@app.route('/')
def index():
    df = read_data()
    latest_data = {
        'this_week':
        '67.7%',  # Example values, replace with actual calculations
        'last_week': '57.8%',
        'last_year': '67.0%',
        'capacity': '1919.9 million m³',
        'retrieved': '2024-06-10'
    }

    # Create a plotly graph
    graph_df = pd.DataFrame({
        'Time Period': ['Last Year', 'Last Week', 'This Week'],
        'Level': [67.0, 57.8, 67.7]
    })
    fig = px.line(graph_df,
                  x='Time Period',
                  y='Level',
                  title='Western Cape Graph')
    graph_html = pio.to_html(fig, full_html=False)

    return render_template('index.html',
                           latest_data=latest_data,
                           graph_html=graph_html,
                           df=df)


if __name__ == '__main__':
    app.run(debug=True)
