import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Fonction pour charger les données de référence
@st.cache_data
def load_reference_data():
    return pd.read_excel("Commandes.xlsx")

df = load_reference_data()

st.title("Interface de saisie intelligente - Atelier de coupe")

# 🔢 Numéro de commande
commande_num = st.text_input("Numéro de commande (OF)")

# Données à remplir automatiquement
if commande_num:
    commande_info = df[df["OF"].astype(str) == commande_num]

    if not commande_info.empty:
        ligne = commande_info.iloc[0]

        client = st.text_input("Client", ligne["Client"], disabled=True)
        tissu = st.text_input("Tissu", ligne["Tissu"], disabled=True)
        code_rouleau = st.text_input("Code Rouleau", ligne["Code Rouleau"], disabled=True)
        longueur_matelas = st.number_input("Longueur Matelas", value=ligne["Longueur Matelas"], disabled=True)
        nb_plis = st.number_input("Nombre de Plis", value=ligne["Nombre de Plis"], disabled=True)
    else:
        st.warning("Commande non trouvée dans le fichier.")
        st.stop()
else:
    st.info("Veuillez entrer un numéro de commande.")
    st.stop()

# Champs à compléter manuellement
date = st.date_input("Date", value=datetime.today())
heure_debut = st.time_input("Heure de début")
heure_fin = st.time_input("Heure de fin")
temps_operation = st.text_input("Temps de l’opération")
operateur = st.text_input("Nom de l’opérateur")
matricule = st.text_input("Matricule opérateur")

# 📩 Enregistrement
if st.button("✅ Enregistrer la saisie"):
    new_row = {
        "Date": date,
        "Commande (OF)": commande_num,
        "Client": client,
        "Tissu": tissu,
        "Code Rouleau": code_rouleau,
        "Longueur Matelas": longueur_matelas,
        "Nombre de Plis": nb_plis,
        "Heure début": heure_debut.strftime("%H:%M"),
        "Heure fin": heure_fin.strftime("%H:%M"),
        "Temps opération": temps_operation,
        "Opérateur": operateur,
        "Matricule": matricule
    }

    fichier_sortie = "donnees_saisies.xlsx"

    if os.path.exists(fichier_sortie):
        df_exist = pd.read_excel(fichier_sortie)
        df_new = pd.concat([df_exist, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df_new = pd.DataFrame([new_row])

    df_new.to_excel(fichier_sortie, index=False)
    st.success("✅ Données enregistrées avec succès dans 'donnees_saisies.xlsx'.")

    # Affichage tableau après saisie
    st.subheader("Données enregistrées")
    st.dataframe(df_new)
