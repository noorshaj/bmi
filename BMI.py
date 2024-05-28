import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import sqlite3
import datetime
import matplotlib.pyplot as plt

# Database setup
conn = sqlite3.connect('bmi_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bmi_data (
                id INTEGER PRIMARY KEY,
                user TEXT,
                date TEXT,
                weight REAL,
                height REAL,
                bmi REAL)''')
conn.commit()

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI CALCULATOR")
        self.root.geometry("500x400")

        # User selection or creation
        self.current_user = tk.StringVar()
        self.users = self.get_users()
        if not self.users:
            self.create_user()
        else:
            self.select_user()

        # Variables
        self.weight = tk.DoubleVar()
        self.height = tk.DoubleVar()
        self.bmi = tk.StringVar()
        self.bmi_category = tk.StringVar()

        # GUI Components
        self.create_widgets()
        self.update_user_list()

    def create_widgets(self):
        # User management
        tk.Label(self.root, text="User:").pack(anchor="w", padx=10, pady=5)
        self.user_combobox = ttk.Combobox(self.root, textvariable=self.current_user)
        self.user_combobox.pack(anchor="w", padx=10, pady=5)
        tk.Button(self.root, text="New User", command=self.create_user).pack(anchor="w", padx=10, pady=5)

        # Input fields
        tk.Label(self.root, text="Weight (kg):").pack(anchor="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.weight).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.root, text="Height (cm):").pack(anchor="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.height).pack(anchor="w", padx=10, pady=5)

        # Buttons
        tk.Button(self.root, text="Calculate BMI", command=self.calculate_bmi).pack(padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.bmi, state='readonly').pack(fill='x', padx=10, pady=5)
        self.bmi_category_label = tk.Label(self.root, textvariable=self.bmi_category)
        self.bmi_category_label.pack(fill='x', padx=10, pady=5)
        tk.Button(self.root, text="View History", command=self.view_history).pack(padx=10, pady=5)
        tk.Button(self.root, text="View Trends", command=self.view_trends).pack(padx=10, pady=5)

    def get_users(self):
        c.execute("SELECT DISTINCT user FROM bmi_data")
        users = [row[0] for row in c.fetchall()]
        return users

    def create_user(self):
        new_user = simpledialog.askstring("New User", "Enter new user name:")
        if new_user:
            self.current_user.set(new_user)
            self.update_user_list()

    def select_user(self):
        self.current_user.set(self.users[0])

    def update_user_list(self):
        self.users = self.get_users()
        self.user_combobox['values'] = self.users
        if self.current_user.get() not in self.users:
            self.current_user.set('')

    def calculate_bmi(self):
        weight = self.weight.get()
        height_cm = self.height.get()
        height_m = height_cm / 100

        if weight <= 0 or height_cm <= 0:
            messagebox.showerror("Invalid Input", "Weight and Height must be greater than 0.")
            return

        bmi = weight / (height_m ** 2)
        self.bmi.set(f"BMI: {bmi:.2f}")

        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 24.9:
            category = "Normal weight"
        elif 25 <= bmi < 29.9:
            category = "Overweight"
        else:
            category = "Obesity"

        self.bmi_category.set(f"Category: {category}")

        c.execute("INSERT INTO bmi_data (user, date, weight, height, bmi) VALUES (?, ?, ?, ?, ?)",
                  (self.current_user.get(), datetime.date.today(), weight, height_cm, bmi))
        conn.commit()

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")
        history_window.geometry("400x300")
        
        tree = ttk.Treeview(history_window, columns=('date', 'weight', 'height', 'bmi'), show='headings')
        tree.heading('date', text='Date')
        tree.heading('weight', text='Weight (kg)')
        tree.heading('height', text='Height (cm)')
        tree.heading('bmi', text='BMI')
        tree.pack(fill='both', expand=True)

        c.execute("SELECT date, weight, height, bmi FROM bmi_data WHERE user=? ORDER BY date DESC", (self.current_user.get(),))
        for row in c.fetchall():
            tree.insert('', 'end', values=row)

    def view_trends(self):
        c.execute("SELECT date, bmi FROM bmi_data WHERE user=? ORDER BY date", (self.current_user.get(),))
        data = c.fetchall()
        if not data:
            messagebox.showinfo("No Data", "No data available for trend analysis.")
            return

        dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d') for row in data]
        bmis = [row[1] for row in data]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, bmis, marker='o')
        plt.xlabel('Date')
        plt.ylabel('BMI')
        plt.title('BMI Trend Over Time')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()

# Close the database connection when done
conn.close()
