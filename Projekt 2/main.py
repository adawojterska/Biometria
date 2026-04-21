import tkinter as tk
from gui import IrisGUI

def main():
    # 1. Tworzenie głównego okna aplikacji
    root = tk.Tk()
    
    # 2. Inicjalizacja Twojej klasy interfejsu
    # Przekazujemy 'root' jako rodzica dla wszystkich elementów GUI
    app = IrisGUI(root)
    
    # 3. Uruchomienie pętli głównej (oczekiwanie na interakcję użytkownika)
    root.mainloop()

if __name__ == "__main__":
    main()