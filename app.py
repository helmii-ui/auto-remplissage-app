import pandas as pd
import streamlit as st

# Load Excel data (make sure to replace with your actual file path)
excel_file = "Commandes.xlsx"  # Path to your Excel file
df = pd.read_excel(excel_file)

# Streamlit UI
st.title("Auto-fill Example")

# Input for the order number (which can contain both numbers and text)
order_input = st.text_input("Enter OF", "")

# Strip extra spaces from user input and Excel data, and convert to lowercase for case-insensitive matching
order_input_clean = order_input.strip().lower()

# Ensure the 'OrderNumber' column is also cleaned (strip spaces and convert to lowercase)
df['OF'] = df['OF'].str.strip().str.lower()

# Check if the cleaned input exists in the cleaned 'OrderNumber' column
if order_input_clean in df['OF'].values:
    # Fetch the row with the matching order number
    order_info = df[df['OF'] == order_input_clean].iloc[0]

    # Auto-fill the fields based on the order number
    st.text_input("Client", value=order_info["Client"], disabled=True)  # Replace 'Client' with your actual column name
    st.text_input("Tissu", value=order_info["Tissu"], disabled=True)  # Replace 'Tissu' with your actual column name
    st.text_input("Code Rouleau", value=order_info["CodeRouleau"], disabled=True)  # Replace 'CodeRouleau' with your actual column name
    st.number_input("Longueur Matelas", value=order_info["LongueurMatelas"], disabled=True)  # Replace 'LongueurMatelas' with your actual column name
else:
    st.warning("Order number not found.")
