import pandas as pd
import streamlit as st

# Load Excel data (make sure to replace with your actual file path)
excel_file = "Commandes.xlsx"  # Path to your Excel file
df = pd.read_excel(excel_file)

# Streamlit UI
st.title("Auto-fill Example")

# Input for the order number (number column could be order number, or operator ID)
order_number = st.number_input("Enter Order Number", min_value=1)

# Check if the order number exists in the DataFrame
if order_number in df['OF'].values:  # Replace 'OrderNumber' with your actual column name
    # Fetch the row with the matching order number
    order_info = df[df['OF'] == order_number].iloc[0]

    # Auto-fill the fields based on the order number
    st.text_input("Client", value=order_info["Client"], disabled=True)  # Replace 'Client' with your actual column name
    st.text_input("Tissu", value=order_info["Tissu"], disabled=True)  # Replace 'Tissu' with your actual column name
    st.text_input("Code Rouleau", value=order_info["CodeRouleau"], disabled=True)  # Replace 'CodeRouleau' with your actual column name
    st.number_input("Longueur Matelas", value=order_info["LongueurMatelas"], disabled=True)  # Replace 'LongueurMatelas' with your actual column name
else:
    st.warning("Order number not found.")
