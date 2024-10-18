import os
import json
from graphviz import Digraph
import streamlit as st
import tempfile

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
        return "Erreur : Nom de fichier trop long (limite : 8 caractères)"
    
    # Vérifier si le fichier existe déjà
    if filename in fs['root']['files']:
        return "Erreur : Fichier existe déjà"
    
    # Stocker les données sous un format simplifié
    if len(fs['root']['files']) >= 128:
        return "Erreur : Répertoire plein (128 fichiers max)"

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

            # Initialize a new Digraph for the file system and memory structure
            diagram = Digraph('FileSystemDiagram', comment='Ouichefs File System and RAM Structure')

            # Create subgraphs for SD Card (File system) and RAM
            with diagram.subgraph(name='cluster_sd') as sd_card:
                sd_card.attr(label="SD Card (Ouichefs)")
                sd_card.node('root', 'Root Directory')
                sd_card.node(f'file_{filename}', f'File: {filename}')
                
                # Add data blocks as nodes
                for i, block in enumerate(data_blocks):
                    sd_card.node(f'block_{i+1}', f'Data Block {i+1} ({len(block)} bytes)')
                    sd_card.edge(f'file_{filename}', f'block_{i+1}', label=f"Data Pointer {i+1}")

            with diagram.subgraph(name='cluster_ram') as ram:
                ram.attr(label="RAM (Directory and Metadata)")
                ram.node('directory_metadata', 'Directory Structure in RAM')
                ram.node(f'file_metadata_{filename}', f'File Metadata ({filename})')

                # Add pointers to each data block in RAM
                for i in range(len(data_blocks)):
                    ram.node(f'pointer_block{i+1}', f'Pointer to Block {i+1}')
                    ram.edge(f'file_metadata_{filename}', f'pointer_block{i+1}', label=f"Pointer to Block {i+1}")

            # Add an edge between the SD Card and RAM to represent loading the directory structure
            diagram.edge('root', 'directory_metadata', label="Load into RAM")
            diagram.edge(f'file_{filename}', f'file_metadata_{filename}', label="Load File Metadata into RAM")

            # Utilisation d'un fichier temporaire pour rendre le diagramme
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                diagram.render(tmpfile.name, format='png', cleanup=False)
                tmpfile_path = tmpfile.name

            # Afficher l'image générée dans Streamlit
            st.image(tmpfile_path)
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
