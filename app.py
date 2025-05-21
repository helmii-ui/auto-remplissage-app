import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Saisie Données Coupe", layout="centered")
st.title("📝 Interface de Saisie - Département Coupe")

# --- Formulaire de saisie ---
with st.form("formulaire"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.today())
        client = st.text_input("Client")
        commande = st.text_input("N° Commande")
        tissu = st.text_input("Tissu")
        code_rouleau = st.text_input("Code Rouleau")
    with col2:
        longueur_matelas = st.text_input("Longueur Matelas (m)")
        nombre_plis = st.text_input("Nombre de Plis")
        heure_debut = st.time_input("Heure Début")
        heure_fin = st.time_input("Heure Fin")
        temps_matelas = st.text_input("Temps de Matelas (hh:mm)")
    
    nom_operateur = st.text_input("Nom Opérateur")

    submit = st.form_submit_button("✅ Valider")

# --- Connexion à la base SQLite ---
conn = sqlite3.connect("donnees.db")
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS donnees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Client TEXT,
        Commande TEXT,
        Tissu TEXT,
        CodeRouleau TEXT,
        LongueurMatelas TEXT,
        NombrePlis TEXT,
        HeureDebut TEXT,
        HeureFin TEXT,
        TempsMatelas TEXT,
        Operateur TEXT,
        Matricule TEXT
    )
""")
conn.commit()

# --- Enregistrement dans la base ---
if submit:
    cursor.execute("""
        INSERT INTO donnees (
            Date, Client, Commande, Tissu, CodeRouleau,
            LongueurMatelas, NombrePlis, HeureDebut, HeureFin,
            TempsMatelas, Operateur, Matricule
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(date), client, commande, tissu, code_rouleau,
        longueur_matelas, nombre_plis, str(heure_debut), str(heure_fin),
        temps_matelas, nom_operateur, "1234"  # Matricule fixe
    ))
    conn.commit()
    st.success("✅ Données enregistrées avec succès !")

# --- Affichage des données enregistrées ---
st.subheader("📊 Toutes les données")
df = pd.read_sql_query("SELECT * FROM donnees", conn)
st.dataframe(df)

conn.close()
