import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auto-Fill App", layout="centered")

st.title("Auto-remplissage des données par numéro de commande")

# Charger les données depuis Excel
@st.cache_data
def load_reference_data():
    return pd.read_excel("commandes.xlsx")

df = load_reference_data()

# Entrée utilisateur
commande_num = st.text_input("📦 Entrer le numéro de commande :").strip()

# Rechercher les données liées
commande_info = df[df["commande"] == commande_num]

if not commande_info.empty:
    st.success(f"Données trouvées pour {commande_num}")
    st.text_input("👤 Client", value=commande_info["client"].values[0], disabled=True)
    st.text_input("🧵 Tissu", value=commande_info["tissu"].values[0], disabled=True)
    st.text_input("🎯 Code Rouleau", value=commande_info["code_rouleau"].values[0], disabled=True)
else:
    st.warning("Aucune donnée trouvée pour ce numéro. Veuillez remplir manuellement.")
    st.text_input("👤 Client")
    st.text_input("🧵 Tissu")
    st.text_input("🎯 Code Rouleau")

# Tu peux ajouter d’autres champs à la main ici (longueur, date, heure, etc.)

