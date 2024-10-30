import streamlit as st
import json
import re
from bs4 import BeautifulSoup
import pandas as pd

# Sidebar file upload
st.sidebar.title("Upload HTML run report")
uploaded_file = st.sidebar.file_uploader("Choose file", type="html")

def activity_plot(sequencing_norm, available_norm):
    # Create a DataFrame for the data
    data = pd.DataFrame({
        "Time": [int(s[0] / 3600) for s in sequencing_norm],
        "Sequencing": [s[1] for s in sequencing_norm],
        "Available": [a[1] for a in available_norm]
    })

    # Set the index to "Time" for better visualization in st.bar_chart
    data.set_index("Time", inplace=True)
    
    # Display the stacked bar chart
    st.bar_chart(data, x_label="Time (hours)", y_label="Pore activity status %", color=["#00cc00", "#00ff00"])


if uploaded_file is not None:
    # Read the uploaded HTML content
    html_content = uploaded_file.read().decode('utf-8')
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the first <script> tag containing the reportData variable
    script_tag = soup.find('script')
    if script_tag:
        script_content = script_tag.string

        # Use regular expression to extract JSON data from reportData
        pattern = r'reportData\s*=\s*({.*})'
        match = re.search(pattern, script_content)
        if match:
            report_data = json.loads(match.group(1))

            # Extract the series_data
            series_data = report_data.get('pore_activity_grouped', {}).get('series_data', [])
            if len(series_data) >= 2:
                # Get the "data" lists for the first and second elements
                sequencing = series_data[0].get('data', [])  # Pores sequencing data
                available = series_data[1].get('data', [])   # Pores available data

                # Normalise values
                sequencing_norm = [[s[0], round((s[1] * 100 / (s[1] + a[1])), 2)] for s, a in zip(sequencing, available)]
                available_norm = [[a[0], round((a[1] * 100 / (s[1] + a[1])), 2)] for s, a in zip(sequencing, available)]                

                # Calculate pore occupancy and convert timestamps from seconds to hours
                pore_occupancy = [
                    [(s[0] / 3600), s[1] * 100 / (s[1] + a[1])] if a[1] != 0 else None
                    for s, a in zip(sequencing, available)
                ]
                
                # Filter out None values and find the maximum pore occupancy
                pore_occupancy = [p for p in pore_occupancy if p is not None]
                max_pore_occupancy = max(map(lambda x: x[1], pore_occupancy), default=None)
                
                # Display pore activity plot
                st.title("Pore occupancy")
                st.write(f"**Maximum pore occupancy**: {max_pore_occupancy:.2f} %")
                st.caption("Normalised sequencing and available pores over time.")
                st.caption("'Sequencing' bars represent the pore occupancy. Hover over 'Sequencing' bars to display pore occupancy values.")
                activity_plot(sequencing_norm, available_norm)

            else:
                st.write("Series data not found or insufficient.")
        else:
            st.write("reportData variable not found in script tag.")
    else:
        st.write("No <script> tag found in the HTML file.")
else:
    st.write("Please upload an HTML run report using the left sidebar.")
