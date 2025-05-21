import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from sqlalchemy import create_engine

# --- Configuration fichiers ---
CONFIG_FILE = "config.json"
CHEF_MATRICULE = "chef123"  # Matricule du chef
DB_FILE = "donnees.db"
TABLE_NAME = "donnees_coupe"

# Connexion à SQLite
engine = create_engine(f'sqlite:///{DB_FILE}')

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Protec", "IS3", "MOERMAN", "TOYOTA", "Autre"]
if "clients" not in st.session_state:
    st.session_state.clients = default_clients.copy()

# Charger config opérateur
default_operator = {"nom": "najwa", "matricule": "1234"}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        default_operator = json.load(f)

# Interface
st.title("Interface - Atelier de Coupe")

# Authentification
input_matricule = st.text_input("Entrer votre matricule", type="password")

# Accès chef
if input_matricule == CHEF_MATRICULE:
    st.success("Bienvenue Chef (accès lecture seule)")

    st.subheader("Filtrer les données")
    client_filter = st.selectbox("Filtrer par client", options=["Tous"] + st.session_state.clients)
    date_filter = st.date_input("Filtrer par date", value=datetime.today(), max_value=datetime.today())

    # Charger les données depuis SQLite
    try:
        df = pd.read_sql_table(TABLE_NAME, con=engine)
    except:
        df = pd.DataFrame()

    # Filtrer
    if not df.empty:
        if client_filter != "Tous":
            df = df[df['Client'] == client_filter]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df[df['Date'] == date_filter]

    # Afficher
    st.subheader("Données enregistrées")
    st.dataframe(df)

    # Export
    st.subheader("Exporter les données")
    export_option = st.selectbox("Exporter en format", options=["Sélectionner", "CSV", "Excel"])

    if export_option == "CSV":
        st.download_button(
            label="Télécharger en CSV",
            data=df.to_csv(index=False),
            file_name="donnees_filtrees.csv",
            mime="text/csv"
        )
    elif export_option == "Excel":
        st.download_button(
            label="Télécharger en Excel",
            data=df.to_excel(index=False),
            file_name="donnees_filtrees.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Accès opérateur
elif input_matricule == default_operator.get("matricule"):
    st.success("Accès opérateur autorisé.")

    with st.form("form_saisie"):
        date = st.date_input("Date", value=datetime.now())

        client_selection = st.selectbox("Client", options=st.session_state.clients)
        if client_selection == "Autre":
            nouveau_client = st.text_input("Nom du nouveau client")
            if nouveau_client:
                client = nouveau_client
                if nouveau_client not in st.session_state.clients:
                    st.session_state.clients.insert(-1, nouveau_client)
                    st.success(f"Client ajouté à la liste : {nouveau_client}")
            else:
                client = ""
        else:
            client = client_selection

        commande = st.text_input("N° Commande")
        tissu = st.text_input("Tissu")
        rouleau = st.text_input("Code Rouleau")
        longueur = st.number_input("Longueur Matelas (m)", min_value=0.0, step=0.1)
        plis = st.number_input("Nombre de Plis", min_value=1, step=1)
        debut = st.time_input("Heure Début")
        fin = st.time_input("Heure Fin")
        temps = st.text_input("Temps de Matelas (hh:mm)")

        operateur = st.text_input("Nom Opérateur", value=default_operator.get("nom", ""))
        matricule = input_matricule

        submitted = st.form_submit_button("Valider")
        if submitted:
            if not client:
                st.error("Veuillez entrer un nom de client valide.")
            else:
                new_row = pd.DataFrame([[date, client, commande, tissu, rouleau,
                                         longueur, plis, debut, fin, temps, operateur, matricule]],
                                       columns=["Date", "Client", "N° Commande", "Tissu", "Code Rouleau",
                                                "Longueur Matelas", "Nombre de Plis", "Heure Début",
                                                "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"])
                # Enregistrer dans la base SQLite
                new_row.to_sql(TABLE_NAME, con=engine, if_exists="append", index=False)

                # Sauvegarder config opérateur
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"nom": operateur, "matricule": matricule}, f)

                st.success("✅ Données enregistrées avec succès !")

    # Affichage tableau
    st.subheader("Données enregistrées")
    try:
        df = pd.read_sql_table(TABLE_NAME, con=engine)
        st.dataframe(df)
    except:
        st.info("Aucune donnée enregistrée.")

# Matricule incorrect
else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
