import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['student_db']
collection = db['students']

# Setup main window
root = tk.Tk()
root.title("🎓 Student Data Entry Panel")
root.geometry("550x550")
root.configure(bg="#f0f4f7")  # light background

# === Styling ===
LABEL_FONT = ("Arial", 11)
ENTRY_FONT = ("Arial", 11)
BUTTON_FONT = ("Arial", 11, "bold")

# === Frames ===
form_frame = tk.Frame(root, bg="#f0f4f7")
form_frame.pack(pady=15)

table_frame = tk.Frame(root, bg="#f0f4f7")
table_frame.pack()

# === Input Fields ===
def create_labeled_entry(label_text, row):
    tk.Label(form_frame, text=label_text, font=LABEL_FONT, bg="#f0f4f7").grid(row=row, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(form_frame, font=ENTRY_FONT, width=30)
    entry.grid(row=row, column=1, padx=10, pady=5)
    return entry

name_entry = create_labeled_entry("Name:", 0)
age_entry = create_labeled_entry("Age:", 1)
email_entry = create_labeled_entry("Email:", 2)
course_entry = create_labeled_entry("Course:", 3)

# === Treeview Table ===
columns = ("Name", "Age", "Email", "Course")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")
tree.pack(padx=10, pady=10)

# === MongoDB Functions ===
def add_student():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    email = email_entry.get().strip()
    course = course_entry.get().strip()

    if not name or not age or not email or not course:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    try:
        age = int(age)
    except ValueError:
        messagebox.showerror("Input Error", "Age must be a number.")
        return

    student = {
        "name": name,
        "age": age,
        "email": email,
        "course": course
    }

    collection.insert_one(student)
    messagebox.showinfo("Success", "Student added successfully.")
    clear_inputs()
    refresh_data()

def refresh_data():
    tree.delete(*tree.get_children())
    docs = list(collection.find())
    if not docs:
        messagebox.showinfo("Info", "No student records found.")
    for doc in docs:
        tree.insert("", tk.END, iid=str(doc["_id"]), values=(doc["name"], doc["age"], doc["email"], doc["course"]))

def delete_selected():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Select Record", "Please select a record to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected student?")
    if not confirm:
        return

    item_id = selected_item[0]  # Get _id string from Treeview item
    from bson import ObjectId
    collection.delete_one({"_id": ObjectId(item_id)})
    messagebox.showinfo("Deleted", "Record deleted successfully.")
    refresh_data()

def clear_inputs():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)

# === Buttons ===
btn_frame = tk.Frame(root, bg="#f0f4f7")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="➕ Add Student", command=add_student,
          font=BUTTON_FONT, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=5)

tk.Button(btn_frame, text="🔄 Refresh", command=refresh_data,
          font=BUTTON_FONT, bg="#2196F3", fg="white", width=15).grid(row=0, column=1, padx=5)

tk.Button(btn_frame, text="❌ Delete Record", command=delete_selected,
          font=BUTTON_FONT, bg="#f44336", fg="white", width=15).grid(row=0, column=2, padx=5)

# === Initialize ===
refresh_data()
root.mainloop()
