import streamlit as st
import os

# Créer un répertoire pour simuler la carte SD
SD_CARD_DIR = "sd_card"

# Initialiser la carte SD (créer un répertoire si non présent)
if not os.path.exists(SD_CARD_DIR):
    os.makedirs(SD_CARD_DIR)

# Fonction pour écrire dans un fichier "sur la carte SD"
def write_to_sd(filename, data):
    with open(os.path.join(SD_CARD_DIR, filename), 'a') as file:
        file.write(data + '\n')

# Fonction pour lire un fichier "de la carte SD"
def read_from_sd(filename):
    try:
        with open(os.path.join(SD_CARD_DIR, filename), 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Fichier non trouvé."

# Fonction pour lister les fichiers dans la carte SD
def list_files_on_sd():
    return os.listdir(SD_CARD_DIR)

# Interface Streamlit
st.title("Simulation Arduino avec Carte SD")

# Liste des fichiers sur la carte SD
st.header("Fichiers sur la carte SD")
files = list_files_on_sd()
if files:
    st.write(files)
else:
    st.write("Aucun fichier sur la carte SD pour l'instant.")

# Section pour écrire dans un fichier
st.header("Écrire dans un fichier")
filename = st.text_input("Nom du fichier")
data = st.text_area("Données à écrire")

if st.button("Écrire sur la carte SD"):
    if filename and data:
        write_to_sd(filename, data)
        st.success(f"Écrit dans le fichier {filename}")
    else:
        st.error("Veuillez entrer un nom de fichier et des données.")

# Section pour lire un fichier
st.header("Lire un fichier")
file_to_read = st.selectbox("Choisir un fichier à lire", files)
if st.button("Lire le fichier"):
    content = read_from_sd(file_to_read)
    st.write(f"Contenu du fichier {file_to_read}:")
    st.code(content)

# Section pour montrer l'état actuel des fichiers
st.header("État de la carte SD")
if st.button("Rafraîchir la liste des fichiers"):
    files = list_files_on_sd()
    st.write(files)
