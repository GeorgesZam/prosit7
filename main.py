import os
import json
import streamlit as st
import plotly.graph_objects as go

# Créer un répertoire pour simuler la carte SD
SD_CARD_DIR = "ouichefs_sd_card"

# Initialiser la carte SD (créer un répertoire si non présent)
if not os.path.exists(SD_CARD_DIR):
    os.makedirs(SD_CARD_DIR)

# Fichier pour stocker la structure de répertoires (ouichefs)
filesystem_structure = os.path.join(SD_CARD_DIR, "ouichefs_fs.json")

# Initialiser la structure si elle n'existe pas déjà
if not os.path.exists(filesystem_structure):
    # Structure de répertoires sous format ouichefs
    fs_structure = {
        "root": {
            "type": "directory",
            "files": {}
        }
    }
    with open(filesystem_structure, 'w') as fs_file:
        json.dump(fs_structure, fs_file)

# Charger la structure actuelle
def load_fs():
    with open(filesystem_structure, 'r') as fs_file:
        return json.load(fs_file)

# Sauvegarder la structure actuelle
def save_fs(fs_structure):
    with open(filesystem_structure, 'w') as fs_file:
        json.dump(fs_structure, fs_file)

# Fonction pour découper les données en blocs de 256 octets (simulant des blocs sur la carte SD)
def split_data_into_blocks(data, block_size=256):
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]

# Fonction pour créer un fichier dans "ouichefs"
def ouichefs_create_file(filename, data):
    fs = load_fs()

    # Limite de 8 caractères pour les noms de fichiers
    if len(filename) > 8:
        return "Erreur : Nom de fichier trop long (limite : 8 caractères)", None
    
    # Vérifier si le fichier existe déjà
    if filename in fs['root']['files']:
        return "Erreur : Fichier existe déjà", None
    
    # Stocker les données sous un format simplifié
    if len(fs['root']['files']) >= 128:
        return "Erreur : Répertoire plein (128 fichiers max)", None

    # Découper les données en blocs de 256 octets
    data_blocks = split_data_into_blocks(data)

    # Enregistrer les informations du fichier dans la structure
    fs['root']['files'][filename] = {
        "size": len(data),
        "blocks": len(data_blocks),
        "content": data_blocks
    }
    save_fs(fs)
    return f"Fichier {filename} créé avec succès", data_blocks

# Fonction pour lire un fichier dans "ouichefs"
def ouichefs_read_file(filename):
    fs = load_fs()
    if filename not in fs['root']['files']:
        return "Erreur : Fichier non trouvé"
    return fs['root']['files'][filename]['content']

# Fonction pour lister les fichiers dans ouichefs
def ouichefs_list_files():
    fs = load_fs()
    return list(fs['root']['files'].keys())

# Interface Streamlit
st.title("Simulation Ouichefs et Visualisation de Stockage")

# Liste des fichiers dans ouichefs
st.header("Fichiers sur le système ouichefs")
files = ouichefs_list_files()
if files:
    st.write(files)
else:
    st.write("Aucun fichier sur le système de fichiers pour l'instant.")

# Section pour créer un fichier
st.header("Créer un fichier")
filename = st.text_input("Nom du fichier (8 caractères max)")
data = st.text_area("Données à écrire (max 1024 caractères)")

if st.button("Écrire dans ouichefs"):
    if filename and data:
        if len(data) > 1024:
            st.error("Données trop volumineuses. Limite de 1024 caractères.")
        else:
            result, data_blocks = ouichefs_create_file(filename, data)
            st.success(result)

            if data_blocks:  # Vérifier si la création du fichier a réussi
                # Create a Plotly diagram
                nodes = [f'File: {filename}']
                edges = []
                
                # Ajouter les blocs de données comme nœuds et lier aux fichiers
                for i, block in enumerate(data_blocks):
                    block_name = f'Block {i+1} ({len(block)} bytes)'
                    nodes.append(block_name)
                    edges.append((f'File: {filename}', block_name))
                
                # Créer un diagramme avec Plotly
                fig = go.Figure()

                for edge in edges:
                    fig.add_trace(go.Scatter(
                        x=[nodes.index(edge[0]), nodes.index(edge[1])],
                        y=[1, 0],
                        mode='lines+markers+text',
                        text=[edge[0], edge[1]],
                        line=dict(width=2, color='blue')
                    ))

                fig.update_layout(showlegend=False)
                st.plotly_chart(fig)
    else:
        st.error("Veuillez entrer un nom de fichier et des données.")

# Section pour lire un fichier
st.header("Lire un fichier")
file_to_read = st.selectbox("Choisir un fichier à lire", files)
if st.button("Lire le fichier"):
    content = ouichefs_read_file(file_to_read)
    if isinstance(content, list):
        st.write(f"Contenu du fichier {file_to_read}:")
        for i, block in enumerate(content):
            st.code(f"Block {i+1}: {block}")
    else:
        st.error(content)

# Section pour rafraîchir la liste des fichiers
st.header("État du système de fichiers ouichefs")
if st.button("Rafraîchir la liste des fichiers"):
    files = ouichefs_list_files()
    st.write(files)
