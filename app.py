import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Atelier de Coupe",
    page_icon="✂️",
    layout="wide"
)

# File paths
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"
CLIENTS_FILE = "clients.json"

# Chef de coupe credentials
CHEF_MATRICULE = "chef123"  # Customize this

# CSS styling
st.markdown("""
    <style>
    .main {
        padding: 1rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
        border-bottom: 2px solid #4c9aff;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "clients" not in st.session_state:
    default_clients = ["HAVEP", "PWG", "Protec", "IS3", "MOERMAN", "TOYOTA", "Autre"]
    
    if os.path.exists(CLIENTS_FILE):
        try:
            with open(CLIENTS_FILE, "r") as f:
                st.session_state.clients = json.load(f)
        except:
            st.session_state.clients = default_clients.copy()
    else:
        st.session_state.clients = default_clients.copy()
        with open(CLIENTS_FILE, "w") as f:
            json.dump(st.session_state.clients, f)

# Initialize Excel file if needed
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
        "Longueur Matelas", "Nombre de Plis", "Heure Début", 
        "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"
    ])
    df_init.to_excel(DATA_FILE, index=False)

# Load operator config
default_operator = {"nom": "", "matricule": ""}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            default_operator = json.load(f)
    except:
        pass  # Use default if file is corrupted

# Title with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# ✂️")
with col2:
    st.title("Interface - Atelier de Coupe")

# Authentication
with st.container():
    input_matricule = st.text_input("Entrer votre matricule", type="password", help="Entrez votre code d'identification")

# Function to save clients list
def save_clients():
    with open(CLIENTS_FILE, "w") as f:
        json.dump(st.session_state.clients, f)

# Function to calculate time difference
def calculate_time_difference(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    
    # Handle if end time is on the next day
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    diff = end_dt - start_dt
    
    # Format as HH:MM
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}"

# Chef de coupe access (read-only)
if input_matricule == CHEF_MATRICULE:
    st.success("Bienvenue Chef de Coupe (accès lecture seule)")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📊 Visualisation des données", "📝 Gestion des clients", "📤 Exportation"])
    
    with tab1:
        # Data filtering
        st.subheader("Filtrer les données")
        col1, col2 = st.columns(2)
        
        with col1:
            client_filter = st.selectbox("Filtrer par client", 
                                        options=["Tous"] + st.session_state.clients[:-1])
        
        with col2:
            date_filter = st.date_input("Filtrer par date", 
                                       value=datetime.today(), 
                                       max_value=datetime.today())
        
        # Read data
        try:
            df = pd.read_excel(DATA_FILE)
            
            # Data filtering based on selections
            if client_filter != "Tous":
                df = df[df['Client'] == client_filter]
            
            df['Date'] = pd.to_datetime(df['Date'])
            filtered_df = df[df['Date'].dt.date == date_filter]
            
            # Display filtered data
            st.subheader("Données enregistrées")
            
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
                
                # Quick stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre d'enregistrements", len(filtered_df))
                with col2:
                    total_length = filtered_df["Longueur Matelas"].sum()
                    st.metric("Longueur totale (m)", f"{total_length:.1f}")
                with col3:
                    total_plis = filtered_df["Nombre de Plis"].sum()
                    st.metric("Nombre total de plis", total_plis)
            else:
                st.info("Aucune donnée trouvée pour les critères sélectionnés.")
        
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier: {e}")
    
    with tab2:
        st.subheader("Gestion des clients")
        
        # Display and edit clients
        st.write("Liste des clients actuels:")
        clients_without_autre = st.session_state.clients[:-1]  # Remove "Autre" for display
        
        for i, client in enumerate(clients_without_autre):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(client)
            with col2:
                if st.button("Supprimer", key=f"delete_{i}"):
                    clients_without_autre.pop(i)
                    st.session_state.clients = clients_without_autre + ["Autre"]
                    save_clients()
                    st.experimental_rerun()
        
        # Add new client
        st.write("Ajouter un nouveau client:")
        new_client = st.text_input("Nom du nouveau client")
        if st.button("Ajouter"):
            if new_client and new_client not in st.session_state.clients:
                clients_without_autre = st.session_state.clients[:-1]
                clients_without_autre.append(new_client)
                st.session_state.clients = clients_without_autre + ["Autre"]
                save_clients()
                st.success(f"Client '{new_client}' ajouté avec succès!")
                st.experimental_rerun()
            elif new_client in st.session_state.clients:
                st.warning(f"Le client '{new_client}' existe déjà.")
            else:
                st.warning("Veuillez entrer un nom de client valide.")
    
    with tab3:
        st.subheader("Exportation des données")
        
        # Read data for export
        try:
            df = pd.read_excel(DATA_FILE)
            
            # Export options
            export_client = st.selectbox("Client pour exportation", 
                                        options=["Tous"] + st.session_state.clients[:-1])
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date de début", value=datetime.today() - timedelta(days=7))
            with col2:
                end_date = st.date_input("Date de fin", value=datetime.today())
            
            # Filter data for export
            df['Date'] = pd.to_datetime(df['Date'])
            mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
            filtered_df = df[mask]
            
            if export_client != "Tous":
                filtered_df = filtered_df[filtered_df['Client'] == export_client]
            
            if not filtered_df.empty:
                st.write(f"Données à exporter ({len(filtered_df)} enregistrements):")
                st.dataframe(filtered_df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger en CSV",
                        data=csv,
                        file_name=f"export_coupe_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                with col2:
                    # Create Excel file in memory for download
                    buffer = pd.ExcelWriter("buffer.xlsx", engine='xlsxwriter')
                    filtered_df.to_excel(buffer, index=False, sheet_name='Data')
                    buffer.close()
                    
                    with open("buffer.xlsx", "rb") as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="📥 Télécharger en Excel",
                        data=excel_data,
                        file_name=f"export_coupe_{start_date}_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # Remove the temporary file
                    if os.path.exists("buffer.xlsx"):
                        os.remove("buffer.xlsx")
            else:
                st.info("Aucune donnée à exporter pour les critères sélectionnés.")
        except Exception as e:
            st.error(f"Erreur lors de la préparation de l'exportation: {e}")

# Operator access
elif input_matricule and input_matricule == default_operator.get("12345"):
    st.success(f"Bienvenue {default_operator.get('nom')}! Accès opérateur autorisé.")
    
    tab1, tab2 = st.tabs(["📝 Saisie des données", "📋 Consultation"])
    
    with tab1:
        st.subheader("Enregistrement d'une nouvelle coupe")
        
        with st.form("form_saisie"):
            today = datetime.now()
            date = st.date_input("Date", value=today, max_value=today)
            
            # Client selection
            client_selection = st.selectbox("Client", options=st.session_state.clients)
            
            # Handle "Autre" client option
            if client_selection == "Autre":
                nouveau_client = st.text_input("Nom du nouveau client")
                if nouveau_client:
                    client = nouveau_client
                else:
                    client = ""
            else:
                client = client_selection
            
            # Form fields
            col1, col2 = st.columns(2)
            with col1:
                commande = st.text_input("N° Commande", help="Numéro de la commande client")
                tissu = st.text_input("Tissu", help="Type ou référence du tissu")
            
            with col2:
                rouleau = st.text_input("Code Rouleau", help="Code d'identification du rouleau")
            
            col1, col2 = st.columns(2)
            with col1:
                longueur = st.number_input("Longueur Matelas (m)", 
                                          min_value=0.1, value=1.0, step=0.1,
                                          help="Longueur du matelas en mètres")
            with col2:
                plis = st.number_input("Nombre de Plis", 
                                      min_value=1, value=1, step=1,
                                      help="Nombre de plis du matelas")
            
            col1, col2 = st.columns(2)
            with col1:
                debut = st.time_input("Heure Début", value=datetime.now().time(),
                                     help="Heure de début de la coupe")
            with col2:
                fin = st.time_input("Heure Fin", value=datetime.now().time(),
                                   help="Heure de fin de la coupe")
            
            # Auto-calculate time difference
            temps = calculate_time_difference(debut, fin)
            st.info(f"Temps calculé: {temps}")
            
            # Operator info
            operateur = st.text_input("Nom Opérateur", value=default_operator.get("nom", ""))
            matricule = input_matricule
            
            submitted = st.form_submit_button("✅ Valider")
            
            if submitted:
                # Form validation
                error = False
                if not client:
                    st.error("Veuillez entrer un nom de client valide.")
                    error = True
                if not commande:
                    st.error("Le numéro de commande est obligatoire.")
                    error = True
                if not tissu:
                    st.error("Le type de tissu est obligatoire.")
                    error = True
                if not rouleau:
                    st.error("Le code rouleau est obligatoire.")
                    error = True
                
                if not error:
                    try:
                        # Add new client if needed
                        if client_selection == "Autre" and nouveau_client and nouveau_client not in st.session_state.clients:
                            st.session_state.clients.insert(-1, nouveau_client)
                            save_clients()
                        
                        # Add data row
                        new_row = pd.DataFrame([[
                            date, client, commande, tissu, rouleau, longueur, plis, 
                            debut, fin, temps, operateur, matricule
                        ]], columns=[
                            "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
                            "Longueur Matelas", "Nombre de Plis", "Heure Début", 
                            "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"
                        ])
                        
                        # Read existing data and append
                        df = pd.read_excel(DATA_FILE)
                        df = pd.concat([df, new_row], ignore_index=True)
                        df.to_excel(DATA_FILE, index=False)
                        
                        # Update operator config
                        with open(CONFIG_FILE, "w") as f:
                            json.dump({"nom": operateur, "matricule": matricule}, f)
                        
                        st.success("✅ Données enregistrées avec succès !")
                        
                        # Add a small delay to show success message
                        time.sleep(0.5)
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"Erreur lors de l'enregistrement: {e}")
    
    with tab2:
        # View today's entries for this operator
        st.subheader("Vos saisies du jour")
        
        try:
            df = pd.read_excel(DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter by current date and operator
            today_entries = df[(df['Date'].dt.date == datetime.today().date()) & 
                              (df['Matricule'] == matricule)]
            
            if not today_entries.empty:
                st.dataframe(today_entries, use_container_width=True)
                
                # Quick stats for operator
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre d'enregistrements", len(today_entries))
                with col2:
                    total_length = today_entries["Longueur Matelas"].sum()
                    st.metric("Longueur totale (m)", f"{total_length:.1f}")
                with col3:
                    total_plis = today_entries["Nombre de Plis"].sum()
                    st.metric("Nombre total de plis", total_plis)
            else:
                st.info("Vous n'avez pas encore d'enregistrements pour aujourd'hui.")
        
        except Exception as e:
            st.error(f"Erreur lors de la lecture des données: {e}")

# No valid authentication provided
elif input_matricule:
    st.error("❌ Matricule incorrect. Accès refusé.")
    st.info("Veuillez entrer un matricule valide pour accéder à l'application.")
else:
    st.info("👋 Bienvenue ! Veuillez saisir votre matricule pour vous connecter.")
    
    # About section
    with st.expander("À propos de cette application"):
        st.write("""
        Cette application permet de suivre les opérations de coupe de l'atelier.
        
        **Fonctionnalités:**
        - Interface opérateur pour la saisie des données de coupe
        - Interface superviseur pour la consultation et l'exportation des données
        - Gestion des clients
        
        **Pour toute assistance, contactez votre administrateur système.**
        """)
