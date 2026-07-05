import customtkinter as ctk
from tkinter import messagebox
from database.database import db
from gui.dashboard import Dashboard
from config.constants import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Smart Attendance - Login")
        self.geometry("400x500")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.create_widgets()
    
    def create_widgets(self):
        ctk.CTkLabel(self, text="AI Smart Attendance System", font=("Arial", 24, "bold")).pack(pady=50)
        ctk.CTkLabel(self, text="Login to continue", font=("Arial", 14)).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=300, height=40)
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=300, height=40, show="*")
        self.password_entry.pack(pady=10)
        self.login_btn = ctk.CTkButton(self, text="Login", width=300, height=45, command=self.login, font=("Arial", 14, "bold"))
        self.login_btn.pack(pady=20)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin WHERE username = ? AND password_hash = ?", (username, password))
        if cursor.fetchone():
            self.destroy()
            Dashboard().mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")