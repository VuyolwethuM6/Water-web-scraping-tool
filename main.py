import requests
import pandas as pd
from bs4 import BeautifulSoup

# Dictionary of regions with their abbreviations and names
regions = {
    "EC": "Eastern Cape",
    "FS": "Free State",
    "G": "Gauteng",
    "KN": "Kwazulu-Natal",
    "LP": "Limpopo",
    "M": "Mpumalanga",
    "NC": "Northern Cape",
    "NW": "North West",
    "WC": "Western Cape Total"
}

# Dictionary to store DataFrames for each region
region_data = {}

for abbreviation, name in regions.items():
    # Update the URL with the current region abbreviation
    url = f"https://www.dws.gov.za/Hydrology/Weekly/ProvinceWeek.aspx?region={abbreviation}"

    # Send a request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses

    # Sample HTML content from the response text you printed
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all table elements
    tables = soup.find_all('table')

    # Based on inspection, choose the correct table (assuming the required table is at index 4)
    target_table_index = 4
    table = tables[target_table_index]

    # Check if the correct table is found
    if table is None:
        print(f"No table found on the webpage for region {name}.")
        continue  # Skip to the next region
    else:
        print(f"Table found for region {name}.")

        # Extract table headers
        headers = [th.text.strip() for th in table.find_all('th')]
        print("Headers:", headers)

        # Extract table rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip the first row as it contains headers
            row_data = [td.text.strip().replace('#', '') for td in tr.find_all('td')]
            # Check if the number of columns in the row matches the number of headers
            if len(row_data) == len(headers):
                # Exclude 'River', 'Photo', 'Indicators', and 'FSC' columns
                filtered_row_data = [row_data[0], row_data[5], row_data[6], row_data[7]]
                rows.append(filtered_row_data)
        # print("Rows:", rows)

        # Create a DataFrame
        df = pd.DataFrame(rows, columns=['Dam', 'This Week', 'Last Week', 'Last Year'])

        # Store the DataFrame in the dictionary
        region_data[name] = df

# Create an Excel writer object
with pd.ExcelWriter('dam_levels_master.xlsx') as writer:
    # Create a list to store average data for the master sheet
    averages = []

    for region_name, df in region_data.items():
        # Remove '#' from the numeric columns and convert them to numbers
        df['This Week'] = pd.to_numeric(df['This Week'].str.replace('#', ''), errors='coerce')
        df['Last Week'] = pd.to_numeric(df['Last Week'].str.replace('#', ''), errors='coerce')
        df['Last Year'] = pd.to_numeric(df['Last Year'].str.replace('#', ''), errors='coerce')

        # Calculate averages for the region
        this_week_avg = df['This Week'].mean()
        last_week_avg = df['Last Week'].mean()
        last_year_avg = df['Last Year'].mean()

        # Append the averages to the list
        averages.append([region_name, this_week_avg, last_week_avg, last_year_avg])

        # Write each region's DataFrame to a separate sheet
        df.to_excel(writer, sheet_name=region_name.replace(' ', '_'), index=False)

    # Create a DataFrame for the master sheet with averages
    averages_df = pd.DataFrame(averages, columns=['Region', 'This Week Avg', 'Last Week Avg', 'Last Year Avg'])

    # Write the master DataFrame to the Excel file
    averages_df.to_excel(writer, sheet_name='Master', index=False)

print("Data has been saved to 'dam_levels_master.xlsx'.")
