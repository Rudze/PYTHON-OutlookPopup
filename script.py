from pathlib import Path
import tkinter as tk
import time

POLL_SECONDS = 20
PATH = Path("C:/")

def main():

    # Check si le dossier existe
    if not PATH.exists():
        print(f"Le dossier {PATH} n'existe pas.")
        return
    
    # Boucle infinie pour surveiller les nouveaux files
    while True:
        for f in PATH.glob("*.txt"):
            alerter(f)
                        
        time.sleep(POLL_SECONDS)



def alerter(file):

    contenu = file.read_text(encoding="utf-8")

    fenetre = tk.Tk()
    fenetre.title("Nouveau ticket")
    fenetre.attributes("-topmost", True)
    fenetre.focus_force()
    fenetre.configure(bg="red")
    tk.Label(fenetre, text=contenu, padx=20, pady=20, bg="red", fg="white", font=("Segoe UI", 14, "bold")).pack()     
    fenetre.update_idletasks()
    fenetre.geometry(f"+{(fenetre.winfo_screenwidth() - fenetre.winfo_width()) // 2}+{(fenetre.winfo_screenheight() - fenetre.winfo_height()) // 2}")

    #tk.Label(fenetre, text=contenu, padx=20, pady=20, bg="red", fg="white").pack()

    fenetre.protocol("WM_DELETE_WINDOW", lambda: [fenetre.destroy(), reminder(file)])

    tk.Button(fenetre, text="Me le rappeler", command=lambda: [fenetre.destroy(), reminder(file)]).pack(side="left", padx=10, pady=10)
    tk.Button(fenetre, text="Supprimer", command=lambda: [fenetre.destroy(), delete(file)]).pack(side="right", padx=10, pady=10)

    fenetre.mainloop()

def delete(file):
    file.unlink()
    
    print(f"Le fichier {file} a été supprimé.")

def reminder(file):

    print(f"Le rappel pour le fichier {file} a été activé. Vous serez alerté dans 5 minutes.")

    time.sleep(300)
    alerter(file)

main()