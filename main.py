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

# Interface de l'apprentissage
st.title("Apprendre à utiliser Ouichefs sur Arduino avec une carte SD")

st.write("""
Dans cette interface interactive, nous allons vous guider pour comprendre comment installer et utiliser un système de fichiers comme **ouichefs** sur un **Arduino** connecté à une carte SD pour stocker des données.

### Matériel requis :
- Un Arduino (Uno, Mega, etc.).
- Une carte SD et son module lecteur pour l'Arduino.
- Des câbles pour connecter la carte SD à l'Arduino.
- La bibliothèque SD pour Arduino.
""")

st.subheader("Étape 1 : Configuration matérielle")
st.write("""
Vous devez connecter votre module carte SD à l'Arduino en utilisant les broches suivantes :
- **MISO** : Connecter à la broche 12 de l'Arduino.
- **MOSI** : Connecter à la broche 11 de l'Arduino.
- **SCK** : Connecter à la broche 13 de l'Arduino.
- **CS (Chip Select)** : Connecter à la broche 4 de l'Arduino (ou une autre, selon la configuration).
- **VCC** : Connecter au 5V de l'Arduino.
- **GND** : Connecter à la masse de l'Arduino.

""")


st.subheader("Étape 2 : Installer la bibliothèque SD dans l'IDE Arduino")
st.write("""
L'Arduino nécessite la bibliothèque SD pour interagir avec la carte SD. Suivez ces étapes pour l'installer :

1. Ouvrez l'IDE Arduino.
2. Allez dans **Sketch** > **Include Library** > **Manage Libraries**.
3. Recherchez la bibliothèque **SD** et installez-la.

Une fois installée, vous êtes prêt à commencer à interagir avec la carte SD.
""")

st.subheader("Étape 3 : Initialiser la carte SD dans le code Arduino")
st.write("""
Voici un exemple de code pour initialiser la carte SD dans votre Arduino. Ce code vérifie si la carte SD est correctement connectée et fonctionne.

''' cpp
#include <SPI.h>
#include <SD.h>

const int chipSelect = 4;  // Pin CS pour la carte SD
const int blockSize = 256; // Taille maximale d'un bloc de données

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Attendre l'ouverture du port série
  }

  if (!SD.begin(chipSelect)) {
    Serial.println("Échec de l'initialisation de la carte SD.");
    return;
  }
  Serial.println("Carte SD initialisée.");

  // Créer un fichier avec des blocs de données
  String data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.";

  // Découper les données en blocs de 256 octets
  for (int i = 0; i < data.length(); i += blockSize) {
    String block = data.substring(i, i + blockSize);
    saveBlock("data.txt", block);
  }

  // Lire les blocs et les afficher
  readBlocks("data.txt");
}

void saveBlock(const char* filename, String block) {
  File dataFile = SD.open(filename, FILE_WRITE);
  if (dataFile) {
    dataFile.println(block);
    dataFile.close();
    Serial.println("Bloc enregistré.");
  } else {
    Serial.println("Erreur d'ouverture du fichier.");
  }
}

void readBlocks(const char* filename) {
  File dataFile = SD.open(filename);
  if (dataFile) {
    Serial.println("Lecture des blocs :");
    while (dataFile.available()) {
      Serial.write(dataFile.read());
    }
    dataFile.close();
  } else {
    Serial.println("Erreur d'ouverture du fichier.");
  }
}

void loop() {
  // Boucle vide
}
cpp '''
""")


# Interface Streamlit
st.title("Simulation Ouichefs et Visualisation de Stockage")

# Explication du fonctionnement d'Ouichefs
st.header("Explication du système de fichiers Ouichefs")
st.write("""
**Ouichefs** est un système de fichiers simplifié conçu pour un environnement embarqué. Voici comment cela fonctionne :
- **Nom des fichiers** : Limité à 8 caractères pour simplifier la gestion.
- **Blocs de données** : Les fichiers sont découpés en blocs de 256 octets. Si un fichier dépasse cette taille, il sera divisé en plusieurs blocs.
- **Limite des fichiers** : Le système ne peut gérer que 128 fichiers dans le répertoire racine.
- Chaque fichier a des métadonnées associées (taille du fichier, nombre de blocs, etc.), qui sont stockées dans un répertoire appelé `root`.
- Lors de la création d'un fichier, les données sont stockées sous forme de blocs de 256 octets dans la mémoire.
- Lorsqu'un fichier est lu, les blocs de données sont rassemblés pour reconstituer le fichier complet.
""")

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
                # Explication du stockage des blocs
                st.subheader("Explication du stockage des blocs de données")
                st.write(f"""
                Le fichier **{filename}** a été découpé en {len(data_blocks)} bloc(s). Voici comment les données sont stockées :
                - Taille totale du fichier : {len(data)} octets
                - Chaque bloc est de 256 octets maximum.
                - Voici les détails des blocs :
                """)

                # Afficher les détails des blocs
                for i, block in enumerate(data_blocks):
                    st.write(f"Bloc {i+1} : {len(block)} octets")

                # Créer un diagramme avec Plotly pour visualiser les blocs
                nodes = [f'File: {filename}']
                edges = []
                
                # Ajouter les blocs de données comme nœuds et lier aux fichiers
                for i, block in enumerate(data_blocks):
                    block_name = f'Bloc {i+1} ({len(block)} octets)'
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

