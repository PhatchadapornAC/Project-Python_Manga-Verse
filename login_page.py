#login_page
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk # type: ignore
from tkcalendar import DateEntry # type: ignore
import sqlite3
import subprocess
import os
from datetime import datetime
import json

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width/2) - (width/2))
    y = int((screen_height/2) - (height/2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_home_page():
    try:
        subprocess.Popen(['python', r'D:\Project Pythonnnnnn\home_page.py'])
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเปิด Home Page ได้\n{e}")

signup_window = None
contact_image_label = None

def show_contact_image(parent_window):
    global contact_image_label
    if contact_image_label is not None and contact_image_label.winfo_exists():
        contact_image_label.lift()
        return

    contact_image_label = tk.Label(parent_window, image=contact_image, bg="#fff")
    contact_image_label.place(x=200, y=160)

    close_button = tk.Button(parent_window, text="❌", font=("Wonderful Future", 14), bg="#fd5c70", fg="white",
                             command=lambda: close_contact_image(contact_image_label, close_button), cursor="hand2")
    close_button.place(x=990, y=170)

def close_contact_image(contact_label, close_button):
    contact_label.destroy()
    close_button.destroy()

def open_main_page():
    main_window = tk.Toplevel(root)
    main_window.title("Main Page")
    center_window(main_window, 800, 600)

    label = tk.Label(main_window, text="Welcome to the Main Page", font=("Arial", 20))
    label.pack(pady=20)

    exit_button = tk.Button(main_window, text="Exit", command=main_window.destroy)
    exit_button.pack(pady=20)

# ฟังก์ชันนี้ใช้สำหรับบันทึกกิจกรรมของผู้ใช้ (เช่น การเข้าสู่ระบบ, การสั่งซื้อ)
def log_user_activity(username, action):
    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        c = conn.cursor()

        # บันทึกกิจกรรมการเข้าสู่ระบบหรือกิจกรรมอื่นๆ
        c.execute('''
            INSERT INTO user_activity (username, action, timestamp)
            VALUES (?, ?, ?)
        ''', (username, action, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")
        
# ประกาศ current_user ให้เป็น global  
current_user = None

# ฟังก์ชันสำหรับบันทึก current_user ลงในไฟล์ JSON
def save_current_user(username):
    data = {"current_user": username}
    with open("current_user.json", "w") as f:
        json.dump(data, f)

# ฟังก์ชันนี้จะถูกเรียกเมื่อผู้ใช้ล็อกอินสำเร็จ
def login():
    global current_user  # ประกาศให้สามารถเข้าถึงตัวแปร current_user ได้

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        return

    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        c = conn.cursor()

        # อ่านรหัสผ่านจาก DB
        c.execute("SELECT password, role FROM mangauser WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        if result:
            stored_password, user_role = result
            if stored_password == password:
                current_user = username  # ✅ เก็บในตัวแปร global
                log_user_activity(current_user, 'login')  # บันทึกกิจกรรมการเข้าสู่ระบบ
                save_current_user(current_user)  # บันทึก current_user ลงในไฟล์ JSON

                if user_role == 'admin':
                    messagebox.showinfo("Login Success", "คุณเข้าสู่ระบบ Admin แล้ว!")
                    open_admin_page()
                else:
                    messagebox.showinfo("Login Success", "คุณเข้าสู่ระบบสำเร็จแล้ว!")
                    open_home_page()  # เปิดหน้า home_page.py
            else:
                messagebox.showerror("Login Error", "รหัสผ่านของคุณไม่ถูกต้อง")
                password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Login Error", "ไม่พบชื่อผู้ใช้ในระบบ")
            username_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

# ฟังก์ชันที่เปิดหน้า home_page.py
def open_home_page():
    try:
        subprocess.Popen(['python', r'D:\Project Pythonnnnnn\home_page.py'])  # เปิดหน้า home_page.py
        root.destroy()  # ปิดหน้าต่าง Login
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเปิด Home Page ได้\n{e}")

# การใช้งาน log_user_activity() ในการบันทึกกิจกรรมที่เกิดขึ้น เช่น การสั่งซื้อ
def log_order_activity(username, action, order_id, total_price):
    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        c = conn.cursor()

        # บันทึกกิจกรรมการสั่งซื้อสินค้า
        c.execute('''
            INSERT INTO user_activity (username, action, timestamp)
            VALUES (?, ?, ?)
        ''', (username, f"Order ID: {order_id} - {action} - Total Price: {total_price}", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging order activity: {e}")

def forgot_password():
    reset_window = tk.Toplevel(root)
    reset_window.title("Reset Password")
    center_window(reset_window, 700, 480)

    reset_window.configure(bg="#e0f7ff")
    reset_window.transient(root)
    reset_window.grab_set()

    background_image = load_image(r"C:\Users\acer\Pictures\PJ\repass11.png", (700, 480))
    if background_image:
        bg_label = tk.Label(reset_window, image=background_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = background_image

    username_label = tk.Label(reset_window, text="Username :", font=("Wonderful Future", 15), bg="white")
    username_label.place(x=100, y=170)

    username_entry_reset = tk.Entry(reset_window, font=("KhanoonThin", 14), width=25, bg="#c9e0ff")
    username_entry_reset.place(x=260, y=170)

    password_label = tk.Label(reset_window, text="New Password :", font=("Wonderful Future", 15), bg="white")
    password_label.place(x=100, y=250)

    password_frame_reset = tk.Frame(reset_window, bg="white")
    password_frame_reset.place(x=260, y=250)

    new_password_entry = tk.Entry(password_frame_reset, show="*", font=("KhanoonThin", 14), width=20, bg="#c9e0ff")
    new_password_entry.pack(side="left", fill="x", expand=True)
    
    def toggle_password_reset():
        if new_password_entry.cget('show') == "*":
            new_password_entry.config(show="")
            toggle_button_reset.config(image=eye_open_icon)
        else:
            new_password_entry.config(show="*")
            toggle_button_reset.config(image=eye_closed_icon)

    toggle_button_reset = tk.Button(password_frame_reset, image=eye_closed_icon, bg="white", relief="flat",
                                    command=toggle_password_reset, cursor="hand2")
    toggle_button_reset.pack(side="right", padx=5)

    def save_new_password():
        username = username_entry_reset.get().strip()
        new_password = new_password_entry.get().strip()

        if not username or not new_password:
            messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            reset_window.lift()
            return

        if len(new_password) < 10:
            messagebox.showwarning("Password Error", "กรุณากรอกรหัสผ่านให้ครบ 10 ตัวขึ้นไป")
            reset_window.lift()
            return

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            c = conn.cursor()
            c.execute("SELECT * FROM mangauser WHERE username = ?", (username,))
            result = c.fetchone()

            if not result:
                messagebox.showwarning("Username Error", "ไม่พบชื่อผู้ใช้ของคุณในระบบ")
                conn.close()
                reset_window.lift()
                return

            # อัปเดตรหัสผ่าน plain text
            c.execute("UPDATE mangauser SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"รีเซ็ตรหัสผ่าน '{username}' เรียบร้อย")
            reset_window.destroy()
            root.deiconify()

        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")
            reset_window.lift()

    back_button = tk.Button(reset_window, text="Back", font=("Wonderful Future", 14), bg="#f15267", fg="white",
                            command=reset_window.destroy)
    back_button.place(x=270, y=320)

    submit_button = tk.Button(reset_window, text="Submit", font=("Wonderful Future", 14), bg="#4ab662", fg="white",
                              command=save_new_password)
    submit_button.place(x=380, y=320)

def open_signup_window():
    global signup_window
    if signup_window is not None and tk.Toplevel.winfo_exists(signup_window):
        signup_window.lift()
        return

    signup_window = tk.Toplevel(root)
    signup_window.title("Mangaverse Book Shop - Sign Up")
    center_window(signup_window, 1200, 800)
    signup_window.configure(bg="#e0f7ff")
    signup_window.transient(root)
    signup_window.grab_set()

    def sign_up():
        username   = username_entry_signup.get().strip()
        first_name = first_name_entry.get().strip()
        last_name  = last_name_entry.get().strip()
        dob        = dob_entry.get().strip()
        email      = email_entry.get().strip()
        phone      = phone_entry.get().strip()
        password   = password_entry_signup.get().strip()
        role       = 'admin' if username == 'admin' else 'user'

        if not username or not first_name or not last_name or not dob or not email or not phone or not password:
            messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        if '@' not in email:
            messagebox.showwarning("Email Error", "อีเมลของคุณไม่ถูกต้อง กรุณาใส่ @")
            return

        if len(phone) != 10 or not phone.isdigit():
            messagebox.showwarning("Phone Error", "เบอร์โทรไม่ถูกต้อง (ต้องเป็นตัวเลข 10 หลัก)")
            return

        if len(password) < 10:
            messagebox.showwarning("Password Error", "รหัสผ่านต้อง >= 10 ตัวอักษร")
            return

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            c = conn.cursor()
            # บันทึกรหัสผ่านเป็น plaintext (ไม่แฮช) เพื่อให้เห็นได้ใน DB
            c.execute("""
                INSERT INTO mangauser (username, fname, lname, birth, email, phonenum, password, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, first_name, last_name, dob, email, phone, password, role))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sign Up Success", "คุณลงทะเบียนสำเร็จแล้ว")
            signup_window.destroy()
            root.deiconify()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ชื่อผู้ใช้ถูกใช้แล้ว")
        except Exception as e:
            messagebox.showerror("DB Error", f"เกิดข้อผิดพลาด: {e}")

    background_image = load_image(r"C:\Users\acer\Pictures\PJ\12456.png", (1200, 800))
    user_icon = load_image(r"C:\Users\acer\Pictures\PJ\username.png", (80, 80))

    if background_image:
        bg_label = tk.Label(signup_window, image=background_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = background_image

    signup_frame = tk.Frame(signup_window, bg="#5271ff", bd=0, relief="groove")
    signup_frame.place(x=200, y=240, width=800, height=360)

    if user_icon:
        user_icon_label = tk.Label(signup_frame, image=user_icon, bg="#5271ff")
        user_icon_label.place(x=20, y=35)
        user_icon_label.image = user_icon

    def create_entry(label_text, frame, x, y, placeholder=""):
        label = tk.Label(frame, text=label_text, bg="#5271ff",
                         font=("Wonderful Future", 15, "bold"), fg="white")
        label.place(x=x, y=y)
        entry = tk.Entry(frame, font=("KhanoonThin", 15), width=20, relief="solid")
        entry.place(x=x + 130, y=y)
        entry.insert(0, placeholder)
        return entry

    username_entry_signup = create_entry("Username :", signup_frame, 120, 60)
    first_name_entry      = create_entry("First name :", signup_frame, 35, 140)
    last_name_entry       = create_entry("Last name :", signup_frame, 440, 140)

    dob_label = tk.Label(signup_frame, text="Date of birth :", bg="#5271ff",
                         font=("Wonderful Future", 15, "bold"), fg="white")
    dob_label.place(x=35, y=210)
    dob_entry = DateEntry(signup_frame, width=18, font=("KhanoonThin", 15),
                          date_pattern='dd/MM/yyyy', background='#004aad', foreground='white', borderwidth=2)
    dob_entry.place(x=190, y=210)

    email_entry = create_entry("E-mail :", signup_frame, 440, 210)
    phone_label = tk.Label(signup_frame, text="Phone number :", bg="#5271ff",
                           font=("Wonderful Future", 15, "bold"), fg="white")
    phone_label.place(x=35, y=280)
    phone_entry = tk.Entry(signup_frame, font=("KhanoonThin", 15),
                           width=20, relief="solid")
    phone_entry.place(x=200, y=280)

    password_label = tk.Label(signup_frame, text="Password :", bg="#5271ff",
                              font=("Wonderful Future", 15, "bold"), fg="white")
    password_label.place(x=440, y=280)
    password_frame = tk.Frame(signup_frame, bg="#5271ff")
    password_frame.place(x=560, y=280)
    password_entry_signup = tk.Entry(password_frame, show="*", font=("KhanoonThin", 15), width=18, relief="solid")
    password_entry_signup.pack(side="left")

    toggle_button_signup = tk.Button(password_frame, image=eye_closed_icon, bg="#5271ff", relief="flat", command=lambda: toggle_password(password_entry_signup, toggle_button_signup))
    toggle_button_signup.pack(side="right", padx=5)
    toggle_button_signup.image = eye_closed_icon

    sign_up_button = tk.Button(signup_window, text="Sign up", font=("Wonderful Future", 15),
                               bg="#482188", fg="white", width=10, command=sign_up)
    sign_up_button.place(x=920, y=650)

    contact_button_signup = tk.Button(signup_window, text="Contact us", font=("Wonderful Future", 14),
                                      bg="#004aad", fg="white", command=lambda: show_contact_image(signup_window))
    contact_button_signup.place(x=100, y=750)
    
    exit_button_signup = tk.Button(signup_window, text="Exit", font=("Wonderful Future", 14),
                                   bg="#004aad", fg="white", command=signup_window.destroy)
    exit_button_signup.place(x=1120, y=750)

    back_button = tk.Button(signup_window, text="Back", font=("Wonderful Future", 14),
                            bg="#004aad", fg="white", command=signup_window.destroy)
    back_button.place(x=20, y=750)

def toggle_password(entry, button):
    if entry.cget('show') == "*":
        entry.config(show="")
        button.config(image=eye_open_icon)
    else:
        entry.config(show="*")
        button.config(image=eye_closed_icon)

def open_admin_page():
    try:
        subprocess.Popen(['python', r'D:\Project Pythonnnnnn\admin_page.py'])
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเปิด Admin Page ได้\n{e}")

def load_image(path, size):
    try:
        from PIL import Image # type: ignore
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def on_closing():
    root.destroy()

# ========================== MAIN PROGRAM START ==========================
root = tk.Tk()
root.withdraw()
root.title("Mangaverse Book Shop")

# สร้าง/ตรวจสอบตารางใน bookstore.db
db_path = r"D:\Project Pythonnnnnn\bookstore.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# สร้างตาราง mangauser ถ้ายังไม่มี
c.execute('''
    CREATE TABLE IF NOT EXISTS mangauser (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        fname TEXT,
        lname TEXT,
        birth TEXT,
        email TEXT,
        phonenum TEXT,
        -- เก็บรหัสผ่านเป็น TEXT (plain) เพื่อให้เห็นได้ใน DB
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
''')

# สร้างบัญชี admin หากยังไม่มี
def ensure_admin_user():
    try:
        # รหัสผ่านเป็น plain text
        admin_password = "admin12345"
        c.execute("INSERT INTO mangauser (username, fname, lname, birth, email, phonenum, password, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  ('admin', 'Admin', 'User', '01/01/04', 'admin@gmail.com', '0123456789', admin_password, 'admin'))
        conn.commit()
        print("Admin account created successfully!")
    except sqlite3.IntegrityError:
        # บัญชี admin มีอยู่แล้ว
        c.execute("UPDATE mangauser SET password = ? WHERE username = 'admin'",
                  ("admin12345",))  # reset เป็น admin12345
        conn.commit()
        print("Admin account updated successfully!")

ensure_admin_user()
conn.close()

root.configure(bg="#e0f7ff")

bg_photo = load_image(r"C:\Users\acer\Pictures\PJ\226.png", (1200, 800))
eye_open_icon = load_image(r"C:\Users\acer\Pictures\PJ\open eye.png", (35, 20))
eye_closed_icon = load_image(r"C:\Users\acer\Pictures\PJ\closed eye.png", (35, 20))
contact_image = load_image(r"C:\Users\acer\Pictures\PJ\contact us.png", (850, 580))

if bg_photo:
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.image = bg_photo

# ส่วนของ Login Frame
# ส่วนของ Login Frame
login_frame = tk.Frame(root, bg="#5271ff", bd=0, relief="groove")
login_frame.place(x=400, y=330, width=450, height=240)

username_label = tk.Label(login_frame, text="Username", bg="#5271ff", font=("Wonderful Future", 25), fg="white")
username_label.pack(pady=5)
username_entry = tk.Entry(login_frame, font=("KhanoonThin", 20), width=30, relief="solid", bd=2, highlightthickness=2)
username_entry.pack(pady=5)

password_label = tk.Label(login_frame, text="Password", bg="#5271ff", font=("Wonderful Future", 25), fg="white")
password_label.pack(pady=5)

password_frame = tk.Frame(login_frame, bg="#5271ff")
password_frame.pack(pady=5)
password_entry = tk.Entry(password_frame, show="*", font=("KhanoonThin", 20), width=30, relief="solid", bd=2, highlightthickness=2)
password_entry.pack(side="left", fill="x", expand=True)

toggle_button = tk.Button(password_frame, image=eye_closed_icon, bg="#5271ff",
                          relief="flat", command=lambda: toggle_password(password_entry, toggle_button))
toggle_button.pack(side="right", padx=5)
toggle_button.image = eye_closed_icon

sign_in_button = tk.Button(root, text="Sign In", font=("Wonderful Future", 15),
                           bg="#482188", fg="white", width=10, command=login)
sign_in_button.place(x=450, y=600)

sign_up_button_main = tk.Button(root, text="Sign Up", font=("Wonderful Future", 15),
                                bg="#482188", fg="white", width=10, command=open_signup_window)
sign_up_button_main.place(x=650, y=600)

forgot_password_link = tk.Label(root, text="Forgot password?", fg="grey", bg="#e0f7ff",
                                font=("KhanoonThin", 12), cursor="hand2")
forgot_password_link.place(x=550, y=660)
forgot_password_link.bind("<Button-1>", lambda e: forgot_password())

contact_button = tk.Button(root, text="Contact us", font=("Wonderful Future", 14),
                           bg="#004aad", fg="white", command=lambda: show_contact_image(root))
contact_button.place(x=20, y=750)

exit_button = tk.Button(root, text="Exit", font=("Wonderful Future", 14),
                        bg="#004aad", fg="white", command=root.quit)
exit_button.place(x=1120, y=750)

root.protocol("WM_DELETE_WINDOW", on_closing)

# ทำหน้าต่างไม่ให้ปรากฏชั่วคราว (overrideredirect) เพื่อไม่ให้เห็นตอนขยาย
root.overrideredirect(True)
center_window(root, 1200, 800)
root.update()
root.overrideredirect(False)

# แสดงหน้าต่าง
root.deiconify()
root.mainloop()