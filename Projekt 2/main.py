import tkinter as tk
from gui import IrisGUI

def main():

    root = tk.Tk()
    
    app = IrisGUI(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()