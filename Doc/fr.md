# PYTHON-OutlookMonitoring

Petit outil pour ne plus louper les tickets qui arrivent par mail. Quand un mail tombe dans le dossier Ticket d'Outlook, une fenêtre rouge s'ouvre au milieu de l'écran, par-dessus toutes les autres applications, jusqu'à ce qu'on la traite.

## Fonctionnement général

Le nouvel Outlook ne permet pas à un script Python de lire la boîte mail directement. On passe donc par Power Automate et OneDrive :

1. Une règle Outlook range les mails de ticket (expéditeur MyThales, objet contenant « a été affecté au groupe ») dans le dossier Ticket.
2. Un flow Power Automate se déclenche à chaque nouveau mail dans ce dossier et crée un fichier texte dans le dossier Alerts de OneDrive. Le fichier contient l'objet et l'expéditeur du mail.
3. OneDrive synchronise ce fichier sur le PC.
4. Le script Python surveille le dossier Alerts en local et ouvre une alerte pour chaque fichier qu'il y trouve.

L'avantage de ce montage, c'est que le script n'a besoin d'aucune authentification : il ne fait que lire des fichiers sur le disque. Le même principe peut servir pour Teams, en ajoutant un flow qui écrit dans le même dossier.

## Prérequis

- Windows avec Python installé (testé avec Python 3.14). Aucune librairie externe : tout vient de la bibliothèque standard.
- OneDrive Thales synchronisé sur le poste, avec un dossier Alerts à la racine.
- Accès à Power Automate avec le compte Thales.

## Mise en place du flow Power Automate

Sur make.powerautomate.com, créer un flux de cloud automatisé :

- Déclencheur : Office 365 Outlook, « À l'arrivée d'un nouvel e-mail (V3) », avec le dossier Ticket.
- Action : OneDrive Entreprise, « Créer un fichier », dans le dossier /Alerts.
- Nom du fichier : mail- suivi de l'expression ci-dessous, puis .txt, pour que chaque fichier ait un nom unique.

```
formatDateTime(utcNow(),'yyyyMMdd-HHmmss-fff')
```

- Contenu du fichier : l'objet du mail, un retour à la ligne, puis l'expéditeur.

Si la popup de connexion à OneDrive affiche une erreur de connexion fermée, c'est le réseau qui bloque la page d'authentification Microsoft. Il suffit en général de réessayer.

## Lancement automatique

Le script est lancé par le Planificateur de tâches Windows, toutes les 5 minutes. Si le script tourne déjà, Windows ne lance pas de deuxième instance. Il démarre donc tout seul après l'allumage du PC et redémarre s'il s'arrête.

```powershell
schtasks /Create /TN "OutlookMonitoring" /SC MINUTE /MO 5 /F /TR "'C:\Users\RudyDAVID\AppData\Local\Programs\Python\Python314\pythonw.exe' 'C:\Users\RudyDAVID\OneDrive - Thales Digital Factory\Documents\Github\Rudze\PYTHON-OutlookMonitoring\script.py'"
```

On utilise pythonw.exe plutôt que python.exe pour ne pas avoir de console ouverte en permanence. Les messages print ne s'affichent donc nulle part quand le script tourne via la tâche.

Une tâche au démarrage de session (ONLOGON) aurait été plus rapide, mais elle demande les droits admin, refusés sur le poste.

Commandes utiles :

```powershell
# Lancer le script tout de suite sans attendre la tâche
schtasks /Run /TN "OutlookMonitoring"

# Supprimer la tâche
schtasks /Delete /TN "OutlookMonitoring" /F
```

Pour arrêter le script, par exemple avant de le modifier, il faut terminer pythonw.exe dans le Gestionnaire des tâches (onglet Détails). Il ne faut pas lancer le script à la main en même temps que la tâche, sinon deux instances tournent et les alertes apparaissent en double.

## Utilisation

Quand un ticket arrive, une fenêtre rouge s'ouvre au centre de l'écran avec l'objet et l'expéditeur du mail. Elle propose deux boutons :

- Supprimer : la fenêtre se ferme et le fichier d'alerte est supprimé. L'alerte ne reviendra pas.
- Me le rappeler : la fenêtre se ferme et revient 20 secondes plus tard.

Fermer la fenêtre avec la croix ne supprime pas le fichier, l'alerte revient donc au tour suivant. C'est voulu : on ne peut pas faire disparaître un ticket sans l'avoir traité.

## Le code

### Configuration

En haut du fichier, deux constantes à adapter si besoin. POLL_SECONDS est l'intervalle en secondes entre deux vérifications du dossier. PATH est le chemin du dossier Alerts synchronisé par OneDrive.

La variable globale Reminder indique qu'un rappel est en cours. Tant qu'elle vaut True, la boucle principale ne déclenche pas de nouvelle alerte.

### main()

C'est le point d'entrée. La fonction vérifie d'abord que le dossier Alerts existe et s'arrête avec un message s'il est introuvable. Ensuite, elle tourne en boucle infinie : à chaque tour, elle liste les fichiers .txt du dossier avec glob et appelle alerter pour chacun, puis attend POLL_SECONDS secondes avant de recommencer. Le sleep évite de faire tourner le processeur à fond pour rien.

### alerter(file)

Cette fonction lit le contenu du fichier, puis construit la fenêtre avec tkinter, la bibliothèque d'interface graphique fournie avec Python :

- l'attribut topmost garde la fenêtre au-dessus de toutes les autres, et focus_force lui donne le focus ;
- le fond et le texte sont colorés en rouge et blanc pour qu'on ne puisse pas la rater ;
- update_idletasks force tkinter à calculer la taille de la fenêtre, ce qui permet ensuite de la centrer avec geometry, en prenant (taille de l'écran − taille de la fenêtre) / 2 ;
- chaque bouton ferme la fenêtre puis appelle delete ou reminder.

mainloop bloque l'exécution tant que la fenêtre est ouverte. Le script attend donc une réponse avant de passer à la suite.

### delete(file)

Supprime le fichier d'alerte du disque (unlink) et remet Reminder à False.

### reminder(file)

Passe Reminder à True, attend 20 secondes, puis rappelle alerter sur le même fichier.

## Limites connues

- Il n'y a pas de gestion d'erreur dans la boucle. Si un fichier est verrouillé par OneDrive au moment de la lecture, le script plante. La tâche planifiée le relance dans les 5 minutes, mais les alertes sont suspendues entre-temps.
- Pendant les 20 secondes d'un rappel, le script est complètement bloqué par le sleep. Un nouveau ticket arrivé pendant ce temps ne sera affiché qu'après.
- Chaque rappel appelle alerter depuis l'intérieur de reminder. Si on reporte plusieurs fois le même ticket, les appels s'empilent.
- Le centrage est calculé avant l'ajout des boutons, donc la fenêtre est légèrement décalée vers le bas.
- Sur un poste à deux écrans, la fenêtre s'ouvre au centre de l'écran principal.
- Le délai entre l'arrivée du mail et l'alerte dépend de Power Automate et de la synchro OneDrive. Il faut compter de quelques secondes à une ou deux minutes.

## Pistes d'évolution

- Ajouter un flow Teams (« Lorsqu'un nouveau message de canal est ajouté ») qui écrit dans le même dossier Alerts.
- Gérer les rappels avec un dictionnaire fichier → heure de rappel dans main(), plutôt qu'avec un sleep, pour que le script reste réactif.
- Entourer la boucle d'un try/except pour qu'une erreur ponctuelle n'arrête pas tout.
- Écrire les messages dans un fichier de log, puisque print ne s'affiche pas avec pythonw.