import customtkinter as ctk
from tkinter import messagebox
from gui.register_student import RegisterStudentWindow
from gui.attendance_window import AttendanceWindow
from database.student_model import StudentModel
from database.attendance_model import AttendanceModel

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Smart Attendance - Dashboard")
        self.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.create_widgets()
        self.update_stats()
    
    def create_widgets(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(header, text="AI Smart Attendance System", font=("Arial", 20, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkButton(header, text="Logout", width=100, command=self.logout).pack(side="right", padx=20, pady=10)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_labels = {}
        stats_data = [("Total Students", "0"), ("Today's Present", "0"), ("Total Attendance", "0")]
        
        for i, (title, value) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_frame, width=200, height=100)
            card.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 0))
            label = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"))
            label.pack(pady=(5, 10))
            self.stats_labels[title] = label
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        buttons = [
            ("📝 Register Student", self.open_register),
            ("📷 Start Attendance", self.open_attendance),
            ("👥 View Students", self.view_students),
            ("📊 Reports", self.view_reports)
        ]
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(buttons_frame, text=text, width=200, height=50, font=("Arial", 14), command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def update_stats(self):
        try:
            students = StudentModel.get_all()
            self.stats_labels["Total Students"].configure(text=str(len(students)))
            today = AttendanceModel.get_today()
            self.stats_labels["Today's Present"].configure(text=str(len(today)))
            self.stats_labels["Total Attendance"].configure(text=str(len(today)))
        except:
            pass
    
    def open_register(self):
        RegisterStudentWindow(self)
    
    def open_attendance(self):
        AttendanceWindow(self)
    
    def view_students(self):
        students = StudentModel.get_all()
        if students:
            msg = "\n".join([f"{s['student_id']}: {s['name']} ({s['department']})" for s in students[:10]])
            if len(students) > 10:
                msg += f"\n... and {len(students)-10} more"
            messagebox.showinfo("Students", f"Total: {len(students)}\n\n{msg}")
        else:
            messagebox.showinfo("Students", "No students registered")
    
    def view_reports(self):
        from attendance.report_generator import ReportGenerator
        from datetime import datetime, timedelta
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        gen = ReportGenerator()
        df = gen.generate_report(start, end)
        if not df.empty:
            filepath = gen.export_to_csv(df)
            if filepath:
                messagebox.showinfo("Reports", f"Report exported: {filepath}")
        else:
            messagebox.showinfo("Reports", "No data found")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.destroy()
            from gui.login_window import LoginWindow
            LoginWindow().mainloop()