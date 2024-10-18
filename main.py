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

```cpp
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
