from PyQt5.QtWidgets import (
    QVBoxLayout, QDialog, QTabWidget, QTextBrowser, QDialogButtonBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aide")
        self.setMinimumSize(800, 550)

        self.setStyleSheet("""
            QTextBrowser {
                font-size: 16px;
                padding: 15px;
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                font-size: 16px;
                padding: 10px 20px;
                min-width: 160px;
                margin-right: 5px;
                background-color: #e0e0e0;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                font-weight: bold;
            }
            QDialogButtonBox {
                padding: 12px;
            }
        """)

        layout = QVBoxLayout()

        # Create tab widget
        tabs = QTabWidget()

        # === Tab 1: Comment utiliser ===
        how_to_use = QTextBrowser()
        how_to_use.setMarkdown("""
# 🧭 Comment utiliser l'éditeur de graphe

---

## 1. 🎨 Création et édition de graphes

### ➕ Ajouter des nœuds
- **Clic gauche** n'importe où sur le canevas pour créer un nouveau nœud.
- **Maintenir le clic gauche** et glisser pour déplacer un nœud.

### 🔗 Ajouter des arêtes
- **Clic droit** sur un nœud pour le sélectionner comme source.
- **Clic droit** sur un autre nœud pour créer une arête entre eux.
- Une invite vous demandera **le poids de l’arête**.

### ❌ Supprimer des éléments
- Activez le **mode gomme** (dans le panneau latéral) pour :
  - **Clic gauche** sur un nœud pour le supprimer ainsi que ses arêtes.
  - **Clic gauche** sur une arête pour la supprimer.
- **Clic du milieu** sur un nœud ou une arête pour les supprimer (fonctionne même sans le mode gomme).

---

## 2. 📂 Importation et exportation de graphes

### 🗂️ Charger un graphe prédéfini
- Cliquez sur **"Charger un graphe prédéfini"** pour choisir parmi des exemples.

### 🔄 Importer un graphe personnalisé
- Cliquez sur **"Importer un graphe personnalisé"** et entrez les arêtes au format suivant :

[(src, dst, poids), (0, 1, 5), (1, 2, 3), ...].
                               
### 💾 Exporter le graphe
- Cliquez sur **"Exporter le graphe"** pour copier la structure actuelle du graphe (arêtes avec poids) afin de la réutiliser.

---

## 3. 🛠️ Options et outils du graphe

### ⚙️ Paramètres du graphe
- **Autoriser les boucles** : permet aux nœuds de se connecter à eux-mêmes.
- **Autoriser les arêtes dupliquées** : permet plusieurs arêtes entre les mêmes nœuds.

### 🧽 Mode gomme
- Active/désactive l'outil de suppression rapide pour les nœuds et les arêtes.

---

## 4. 👁️ Retour visuel

- **Survoler** un nœud le met en évidence.
- Les **actions invalides** (comme les boucles ou doublons non autorisés) font clignoter les nœuds en **rouge**.
- Les **nœuds sélectionnés** pour la création d’une arête sont affichés en **bleu**.

---

## 5. ❓ Aide et raccourcis

- Cliquez sur le bouton **"?"** pour plus d’aide.
- **Clic droit** : créer une arête.
- **Clic du milieu** : supprimer un nœud ou une arête (même sans le mode gomme).
""")


        tabs.addTab(how_to_use, "Utilisation")

        # === Tab 2: Algorithme ===
        algorithm = QTextBrowser()
        algorithm.setMarkdown("""
## Algorithme de Dijkstra

### Aperçu
L’algorithme de Dijkstra permet de trouver les plus courts chemins dans un graphe avec des poids positifs.

### Étapes
1. Assigner des distances provisoires (0 pour le départ, ∞ pour les autres).
2. Choisir le nœud de départ comme actuel.
3. Pour le nœud actuel :
   - Étudier tous les voisins non visités.
   - Calculer les distances provisoires via ce nœud.
   - Mettre à jour si une distance est plus courte.
4. Marquer le nœud comme visité.
5. Choisir le nœud non visité avec la plus petite distance provisoire.
6. Répéter jusqu'à atteindre le but ou avoir visité tous les nœuds atteignables.

### Caractéristiques
- **Complexité temporelle** : O(|E| + |V| log |V|) avec file de priorité
- **Complexité mémoire** : O(|V|)
- **Limite** : Ne fonctionne qu’avec des poids positifs
""")
        tabs.addTab(algorithm, "Algorithme")

        # === Tab 3: Contexte ===
        context = QTextBrowser()
        context.setMarkdown("""
## Contexte du projet

Cette application a été développée dans le cadre du cours de **Théorie des graphes** encadré par **Madame Yosr Slama** à **Facculté de sciences de tunis**.

### Équipe de développement
- **Ayyoub Mkadmi**
- **Yassine Arfaoui**
- **Hela Zouch**
- **Linda Chrigui**

### Objectifs du projet
- Visualiser des structures de graphes et des algorithmes
- Fournir un outil pédagogique interactif pour l’algorithme de Dijkstra
- Illustrer l'application pratique des concepts de la théorie des graphes
""")
        tabs.addTab(context, "Contexte")

        # === OK Button ===
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)

        layout.addWidget(tabs)
        layout.addWidget(buttons)
        self.setLayout(layout)
