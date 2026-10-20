# <h2 align="center">🔔 PYTHON OutlookMonitoring</h2>

---

<div align="center">
  <img alt="Demo" src="./assets_readme/images/alerte.png" />
</div>

<br/>

<div align="center">

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)  
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)  
[![forthebadge](https://forthebadge.com/images/badges/open-source.svg)](https://forthebadge.com)  

</div>

---

## 📖 À propos du projet

**PYTHON OutlookMonitoring** est un petit outil qui empêche de louper les tickets qui arrivent par mail.

Dès qu'un mail tombe dans un dossier Outlook choisi, une fenêtre rouge s'ouvre au milieu de l'écran, par-dessus toutes les autres applications, et reste là tant qu'on ne l'a pas traitée.

Le projet combine :

* 📬 Une règle Outlook qui trie les mails de ticket
* ⚙️ Un flow Power Automate qui transforme chaque mail en fichier
* ☁️ OneDrive qui synchronise ces fichiers sur le PC
* 🐍 Un script Python qui surveille le dossier et déclenche l'alerte
* 🔁 Le Planificateur de tâches Windows pour un lancement automatique

---

## 🧠 Fonctionnement

Le nouvel Outlook ne permet pas à un script de lire la boîte mail directement (pas de COM). On passe donc par Power Automate et OneDrive :

```
Mail reçu → Règle Outlook → Dossier "Ticket"
         → Power Automate → fichier .txt dans OneDrive/Alerts
         → Synchro OneDrive → script Python → 🔴 popup
```

Le script n'a besoin d'aucune authentification : il ne fait que lire des fichiers sur le disque. Le même principe marche pour Teams en ajoutant un flow qui écrit dans le même dossier.

---

## 🚀 Technologies utilisées

* Python 3 (bibliothèque standard uniquement)
* Tkinter
* Pathlib
* Power Automate
* OneDrive
* Planificateur de tâches Windows

---

## 📦 Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/Rudze/PYTHON-OutlookMonitoring.git
cd PYTHON-OutlookMonitoring
```

Aucune dépendance à installer.

### 2. Créer le dossier Alerts

Créer un dossier Alerts à la racine de son OneDrive, puis adapter la constante PATH dans script.py :

```python
PATH = Path("C:/Users/<utilisateur>/OneDrive - <organisation>/Alerts")
```

### 3. Créer la règle Outlook

Créer une règle qui déplace les mails de ticket (par expéditeur et mots-clés dans l'objet) vers un dossier Ticket.

### 4. Créer le flow Power Automate

Sur [make.powerautomate.com](https://make.powerautomate.com), créer un **flux de cloud automatisé** :

* **Déclencheur** : Office 365 Outlook, « À l'arrivée d'un nouvel e-mail (V3) », dossier Ticket
* **Action** : OneDrive Entreprise, « Créer un fichier », dossier /Alerts
* **Nom du fichier** : mail- + l'expression ci-dessous + .txt

```
formatDateTime(utcNow(),'yyyyMMdd-HHmmss-fff')
```

* **Contenu du fichier** : Objet, retour à la ligne, De

---

## ▶️ Lancer le projet

### Lancement manuel

```bash
py script.py
```

### Lancement automatique

Le Planificateur de tâches Windows relance le script toutes les 5 minutes. Si le script tourne déjà, aucune deuxième instance n'est créée. Le script démarre donc tout seul après l'allumage du PC et redémarre s'il s'arrête.

```powershell
schtasks /Create /TN "OutlookMonitoring" /SC MINUTE /MO 5 /F /TR "'C:\chemin\vers\pythonw.exe' 'C:\chemin\vers\script.py'"
```

Pour trouver le chemin de Python :

```powershell
py -c "import sys; print(sys.executable)"
```

On utilise pythonw.exe (même dossier que python.exe) pour ne pas garder de console ouverte.

Commandes utiles :

```powershell
# Lancer tout de suite
schtasks /Run /TN "OutlookMonitoring"

# Supprimer la tâche
schtasks /Delete /TN "OutlookMonitoring" /F
```

Pour arrêter le script, terminer pythonw.exe dans le Gestionnaire des tâches. Ne pas lancer le script à la main en même temps que la tâche, sinon les alertes apparaissent en double.

---

## ✨ Fonctionnalités

* Popup rouge centrée, toujours au premier plan
* Bouton **Supprimer** : l'alerte est traitée et ne revient plus
* Bouton **Me le rappeler** : l'alerte revient 20 secondes plus tard
* Fermer avec la croix ne supprime rien, l'alerte revient au tour suivant
* Redémarrage automatique en cas d'arrêt
* Aucune authentification ni dépendance externe

---

## 📁 Structure du projet

```bash
PYTHON-OutlookMonitoring/
│
├── assets_readme/
├── script.py
└── README.md
```

---

## 🔍 Le code

* **main()** vérifie que le dossier existe, puis boucle à l'infini : à chaque tour, il liste les fichiers .txt et appelle alerter pour chacun, puis attend POLL_SECONDS secondes.
* **alerter(file)** lit le fichier et construit la fenêtre tkinter (premier plan, rouge, centrée), puis attend un clic.
* **delete(file)** supprime le fichier d'alerte et remet le rappel à zéro.
* **reminder(file)** attend 20 secondes, puis réaffiche l'alerte.

---

## 🛠️ Personnalisation

On peut facilement modifier :

* L'intervalle de vérification (POLL_SECONDS)
* Le dossier surveillé (PATH)
* Les couleurs et la police de la fenêtre
* Le délai du rappel
* Les mails surveillés, via la règle Outlook

---

## ⚠️ Limites connues

* Pas de gestion d'erreur : un fichier verrouillé par OneDrive fait planter le script (relancé par la tâche dans les 5 minutes)
* Pendant un rappel, le script est bloqué 20 secondes et ne voit pas les nouveaux tickets
* Le centrage est calculé avant l'ajout des boutons, d'où un léger décalage
* En multi-écran, la fenêtre s'ouvre sur l'écran principal
* Délai mail → alerte de quelques secondes à une ou deux minutes (Power Automate + synchro OneDrive)

---

## 🗺️ Évolutions prévues

* Alertes Teams via un second flow Power Automate
* Rappels gérés sans bloquer le script
* Gestion d'erreur avec try/except
* Fichier de log

---

## 🤝 Contribution

Les contributions, idées et améliorations sont les bienvenues.

N'hésitez pas à forker le projet et à ouvrir une pull request.

---

## 📬 Contact

Pour me contacter :

📧 [rudy@galaxynetwork.fr](mailto:rudy@galaxynetwork.fr)

---

## ⭐ Soutien

Si le projet vous plaît, n'oubliez pas de laisser une ⭐ sur le repository.

---

## 📄 Licence

Ce projet est distribué sous licence MIT.