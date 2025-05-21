import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, Time, Date
import json
import os

# Base SQLite
DB_FILE = "donnees.db"
CONFIG_FILE = "config.json"
CHEF_MATRICULE = "chef123"  # Matricule du chef
OPERATOR_MATRICULE = "1234"  # Matricule fixe de l’opérateur

# Connexion à SQLite
engine = create_engine(f"sqlite:///{DB_FILE}")
metadata = MetaData()

# Table des données
table_donnees = Table(
    "coupe_data", metadata,
    Column("id", Integer, primary_key=True),
    Column("Date", Date),
    Column("Client", String),
    Column("Commande", String),
    Column("Tissu", String),
    Column("CodeRouleau", String),
    Column("LongueurMatelas", Float),
    Column("NombrePlis", Integer),
    Column("HeureDebut", Time),
    Column("HeureFin", Time),
    Column("TempsMatelas", String),
    Column("NomOperateur", String),
    Column("Matricule", String),
)

# Créer la table si elle n'existe pas
metadata.create_all(engine)

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Protec", "IS3", "MOERMAN", "TOYOTA", "Autre"]
if "clients" not in st.session_state:
    st.session_state.clients = default_clients.copy()

# Charger config opérateur
default_operator = {"nom": "Ali", "matricule": OPERATOR_MATRICULE}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        default_operator = json.load(f)

# Titre
st.title("Interface - Atelier de Coupe")

# Authentification
input_matricule = st.text_input("Entrer votre matricule", type="password")

# Accès chef
if input_matricule == CHEF_MATRICULE:
    st.success("Bienvenue Chef (accès lecture seule)")

    with engine.connect() as conn:
        df = pd.read_sql_table("coupe_data", conn)

    st.subheader("Filtrer les données")
    client_filter = st.selectbox("Filtrer par client", ["Tous"] + st.session_state.clients)
    date_filter = st.date_input("Filtrer par date", value=datetime.today(), max_value=datetime.today())

    # Filtrage
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    if client_filter != "Tous":
        df = df[df['Client'] == client_filter]
    df = df[df['Date'] == date_filter]

    st.subheader("Données filtrées")
    st.dataframe(df)

    # Exportation
    st.subheader("Exporter les données")
    export_option = st.selectbox("Exporter en format", ["Sélectionner", "CSV", "Excel"])
    if export_option == "CSV":
        st.download_button("Télécharger CSV", data=df.to_csv(index=False), file_name="donnees.csv", mime="text/csv")
    elif export_option == "Excel":
        st.download_button("Télécharger Excel", data=df.to_excel(index=False), file_name="donnees.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Accès opérateur
elif input_matricule == OPERATOR_MATRICULE:
    st.success("Accès opérateur autorisé.")

    with st.form("form_saisie"):
        date = st.date_input("Date", value=datetime.today())
        client_selection = st.selectbox("Client", st.session_state.clients)

        if client_selection == "Autre":
            nouveau_client = st.text_input("Nom du nouveau client")
            if nouveau_client:
                client = nouveau_client
                if nouveau_client not in st.session_state.clients:
                    st.session_state.clients.insert(-1, nouveau_client)
                    st.success(f"Client ajouté : {nouveau_client}")
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
                with engine.connect() as conn:
                    conn.execute(table_donnees.insert().values(
                        Date=date, Client=client, Commande=commande, Tissu=tissu,
                        CodeRouleau=rouleau, LongueurMatelas=longueur, NombrePlis=plis,
                        HeureDebut=debut, HeureFin=fin, TempsMatelas=temps,
                        NomOperateur=operateur, Matricule=matricule
                    ))

                with open(CONFIG_FILE, "w") as f:
                    json.dump({"nom": operateur, "matricule": matricule}, f)

                st.success("✅ Données enregistrées avec succès !")

    st.subheader("Toutes les données")
    with engine.connect() as conn:
        df = pd.read_sql_table("coupe_data", conn)
        st.dataframe(df)

else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
