import tkinter as tk

def main_menu():
    """
    Purpose: Display main menu after successful login.
    """
    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("400x300")

    tk.Label(root, text="Main Menu", font=("Arial", 16)).pack(pady=20)

    tk.Button(root, text="Users Module").pack(pady=5)
    tk.Button(root, text="Clients Module").pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=20)

    root.mainloop()
