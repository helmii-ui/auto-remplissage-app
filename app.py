import streamlit as st
import pandas as pd

st.set_page_config(page_title="App Auto-remplissage", layout="wide")

# Fonction pour charger les données de référence depuis Excel
@st.cache_data
def load_reference_data():
    df = pd.read_excel("Commandes.xlsx")
    return df

df = load_reference_data()

st.title("🧾 Interface de Saisie avec Auto-remplissage")

# Saisie du numéro de commande (OF)
commande_num = st.text_input("🔍 Saisir le numéro OF")

if commande_num:
    # Rechercher l’OF dans la colonne 'OF'
    commande_info = df[df["OF"].astype(str).str.contains(str(commande_num), na=False)]

    if not commande_info.empty:
        info = commande_info.iloc[0]

        # Auto-remplir les champs
        client = st.text_input("Client", value=info.get("Client", ""))
        tissu = st.text_input("Tissu", value=info.get("Tissu", ""))
        code_rouleau = st.text_input("Code Rouleau", value=info.get("Code Rouleau", ""))
        longueur = st.number_input("Longueur Matelas", value=info.get("Longueur", 0.0))
        nb_plis = st.number_input("Nombre de Plis", value=info.get("Plis", 0))

        st.success("✔️ Données auto-remplies depuis le fichier Excel")
    else:
        st.warning("⚠️ Numéro OF non trouvé dans le fichier Excel.")
