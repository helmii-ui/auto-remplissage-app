import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auto-remplissage Commande", layout="centered")

# Fonction pour charger le fichier Excel
@st.cache_data
def load_data():
    df = pd.read_excel("Commandes.xlsx")
    # Nettoyer les noms de colonnes (supprimer les espaces, tout en minuscules)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()
st.title("🔁 Formulaire avec Auto-remplissage")
st.write("📄 Colonnes trouvées :", df.columns.tolist())

# Saisie du numéro de commande (OF)
commande_num = st.text_input("🔢 Entrez le numéro de commande (OF)")

if commande_num:
    commande_info = df[df["OF"].astype(str) == commande_num.strip()]
    if not commande_info.empty:
        commande_info = commande_info.iloc[0]

        # Champs remplis automatiquement
        st.text_input("Client", value=commande_info.get("client", ""), disabled=True)
        st.text_input("Tissu", value=commande_info.get("tissu", ""), disabled=True)
        st.text_input("Code Rouleau", value=commande_info.get("code rouleau", ""), disabled=True)
        st.text_input("Longueur", value=commande_info.get("longueur", ""), disabled=True)
        st.text_input("Nombre de plis", value=commande_info.get("nombre de plis", ""), disabled=True)

        # Saisie libre pour autres champs
        operateur = st.text_input("Nom de l'opérateur")
        matricule = st.text_input("Matricule")
        heure_debut = st.time_input("Heure de début")
        heure_fin = st.time_input("Heure de fin")

        if st.button("✅ Enregistrer"):
            st.success("Données enregistrées avec succès (fonction de sauvegarde à ajouter).")
    else:
        st.error("❌ Commande non trouvée. Vérifiez le numéro (OF) saisi.")
