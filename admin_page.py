#admin_page
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk # type: ignore
from tkcalendar import DateEntry # type: ignore
import sqlite3
import os
import re
from datetime import datetime
import customtkinter as ctk # type: ignore
from io import BytesIO
import json
def load_current_user():
    try:
        with open("current_user.json", "r") as f:
            data = json.load(f)
            return data["current_user"]
    except FileNotFoundError:
        return None  # หรือค่าเริ่มต้นอื่นๆ

# ใช้งานที่ไหนก็ได้ใน home_page.py
current_user = load_current_user()

# ตรวจสอบค่าจาก current_user
def show_admin_page():
    global current_user  # ใช้ตัวแปร global เพื่อเข้าถึงค่าจาก login.py

    # ตัวอย่างการแสดงชื่อผู้ใช้ที่ล็อกอิน
    print("ผู้ใช้ที่ล็อกอิน:", current_user)  # จะแสดงในคอนโซล

    # ถ้าต้องการแสดงใน GUI เช่น Label ใน tkinter
    label = tk.Label(root, text=f"ยินดีต้อนรับ {current_user}", font=("Arial", 16))
    label.pack(pady=20)

# ------------------ ฟังก์ชันจัดตำแหน่งหน้าต่างกลางหน้าจอ ------------------
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

# ------------------ ฟังก์ชันโหลดรูปภาพและปรับขนาด ------------------
def load_image(path, size):
    try:
        image = Image.open(path)
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# =============================================================================
#                    Main Admin Page / Home Admin Panel
# =============================================================================

class AdminPage:
    """
    หน้าต่างหลักของฝั่ง Admin
    - จัดการผู้ใช้ (User)
    - จัดการที่อยู่จัดส่ง (Delivery address)
    - จัดการสินค้า (Product)
    - รายการสินค้าที่ซื้อ
    - สรุปยอดขาย (Sales Summary)
    - สลิปการชำระเงินเมื่อคลิกที่ชื่อผู้ใช้
    - user activity
    """
    
    def __init__(self, root):
        # สร้างหน้าต่างใหม่
        self.root = tk.Toplevel(root)
        self.root.title("Admin Panel")
        self.center_window(self.root, 1200, 800)  # Call the center_window method here
        self.root.configure(bg="#e0f7ff")
        

        # แถบเมนูด้านบน (Navigation Bar)
        self.nav_frame = tk.Frame(self.root, bg="#004aad", height=30)
        self.nav_frame.pack(fill="x")
        

        # ปุ่มต่างๆ บน Nav Bar
        self.buttons = {
            "ข้อมูลผู้ใช้": self.show_user_info,
            "รายการสินค้าที่ซื้อ": self.show_order_items,
            "สินค้า": self.show_products,
            "ประวัติการซื้อ": self.show_purchase_history,
            "สรุปยอดการขาย": self.show_sales_summary,
            "สลิปการชำระเงิน": self.show_payment_slips,  # Added button for payment slips
            "กิจกรรมผู้ใช้": self.show_user_activity  # Added button for user activity
        }

        for text, command in self.buttons.items():
            btn = tk.Button(
                self.nav_frame,
                text=text,
                font=("KhanoonThin", 15),
                bg="#004aad",
                fg="white",
                bd=0,
                command=command,
                activebackground="#003366",
                cursor="hand2",
                padx=10, pady=5
            )
            btn.pack(side="left", padx=10, pady=5)

        # เฟรมหลัก แสดงตาราง / เนื้อหา
        self.content_frame = tk.Frame(self.root, bg="#e0f7ff")
        self.content_frame.pack(fill="both", expand=True)

        # ส่วนล่างสำหรับปุ่ม Log Out และ Exit
        self.bottom_frame = tk.Frame(self.root, bg="#e0f7ff", height=50)
        self.bottom_frame.pack(fill="x", side="bottom")

        logout_button = tk.Button(
            self.bottom_frame,
            text="Log Out",
            font=("Wonderful Future", 14),
            bg="#f39c12",
            fg="white",
            command=self.logout,
            cursor="hand2",
            padx=10, pady=5
        )
        logout_button.pack(side="left", padx=20, pady=10)

        exit_button = tk.Button(
            self.bottom_frame,
            text="Exit",
            font=("Wonderful Future", 14),
            bg="#c0392b",
            fg="white",
            command=self.root.destroy,
            cursor="hand2",
            padx=10, pady=5
        )
        exit_button.pack(side="right", padx=20, pady=10)

        # เริ่มต้นด้วยการแสดง "ข้อมูลผู้ใช้"
        self.show_user_info()

    def center_window(self, window, width, height):
        """ตั้งค่าตำแหน่งหน้าต่างให้ตรงกลาง"""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

    def clear_content(self):
        """เคลียร์วิดเจ็ตทั้งหมดใน content_frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # -------------------------------------------------------------------------
    #                          1) จัดการผู้ใช้ (User Info)
    # -------------------------------------------------------------------------
    # ปรับในส่วนของการแสดงข้อมูลผู้ใช้ใน Treeview
    def show_user_info(self):
        """แสดงตารางข้อมูลผู้ใช้ (mangauser) พร้อมปุ่มเพิ่ม/แก้ไข/ลบ"""
        self.clear_content()

        # แถบค้นหา
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 14),
            bg="#2980b9",
            fg="white",
            command=self.search_user,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # ปุ่ม เพิ่ม/แก้ไข/ลบ
        action_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        action_frame.pack(pady=5)

        tk.Button(
            action_frame,
            text="เพิ่มผู้ใช้",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.add_user,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="แก้ไขผู้ใช้",
            font=("KhanoonThin", 12),
            bg="#f1c40f",
            fg="white",
            command=self.edit_user,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="ลบผู้ใช้",
            font=("KhanoonThin", 12),
            bg="#e74c3c",
            fg="white",
            command=self.delete_user,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        # Treeview
        columns = ("ID", "Username", "First Name", "Last Name", "Birth Date", "Email", "Phone Number", "Password")
        self.user_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.user_tree.heading(col, text=col)
            if col == "ID":
                self.user_tree.column(col, width=50, anchor='center')
            elif col == "Username":
                self.user_tree.column(col, width=100, anchor='center')
            elif col in ["First Name", "Last Name"]:
                self.user_tree.column(col, width=100, anchor='center')
            elif col == "Birth Date":
                self.user_tree.column(col, width=100, anchor='center')
            elif col == "Email":
                self.user_tree.column(col, width=200, anchor='center')
            elif col == "Phone Number":
                self.user_tree.column(col, width=120, anchor='center')
            elif col == "Password":
                self.user_tree.column(col, width=150, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.user_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 11), rowheight=25)

        # ดึงข้อมูลจาก DB มาแสดง
        self.populate_user_info()

    def populate_user_info(self, query=None):
        """แสดงรายการผู้ใช้ทั้งหมดใน treeview"""
        for row in getattr(self, "user_tree", []).get_children():
            self.user_tree.delete(row)

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            if query:
                cursor.execute(""" 
                    SELECT id, username, fname, lname, birth, email, phonenum, password, role
                    FROM mangauser
                    WHERE username LIKE ? OR fname LIKE ? OR lname LIKE ?
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cursor.execute(""" 
                    SELECT id, username, fname, lname, birth, email, phonenum, password, role 
                    FROM mangauser
                """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                # แสดงข้อมูลใน Treeview โดยไม่แสดง password ที่แท้จริง
                display_row = row[:-1]  # ลบรหัสผ่านออกจากการแสดง
                self.user_tree.insert("", tk.END, values=display_row)
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")


    def search_user(self):
        query = self.search_var.get().strip()
        self.populate_user_info(query)

    def add_user(self):
        AddEditUserWindow(self, "add")

    def edit_user(self):
        selected_item = self.user_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "กรุณาเลือกผู้ใช้ที่ต้องการแก้ไข")
            return
        user_data = self.user_tree.item(selected_item)['values']
        AddEditUserWindow(self, "edit", user_data)

    def delete_user(self):
        selected_item = self.user_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "กรุณาเลือกผู้ใช้ที่ต้องการลบ")
            return
        user_data = self.user_tree.item(selected_item)['values']
        confirm = messagebox.askyesno("Confirm Delete", f"คุณแน่ใจว่าต้องการลบผู้ใช้ '{user_data[1]}' หรือไม่?")
        if confirm:
            try:
                conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mangauser WHERE id = ?", (user_data[0],))
                conn.commit()
                conn.close()
                self.populate_user_info()
                messagebox.showinfo("Success", "ลบผู้ใช้เรียบร้อยแล้ว")
            except Exception as e:
                messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")
    
    # -------------------------------------------------------------------------
    #                          2) สลิปการชำระเงิน (Payment Slips)
    # -------------------------------------------------------------------------
    def show_payment_slips(self):
        """Display payment slips in the Treeview."""
        self.clear_content()
        self.display_payment_slips()
        
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา id:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("KhanoonThin",15), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
        search_frame,
        text="🔍",
        font=("KhanoonThin", 15),
        bg="#2980b9",
        fg="white",
        command=self.search_order,  # 
        cursor="hand2",
        padx=15, pady=10
        ).pack(side="left", padx=5)


    def clear_content(self):
        """Clear previous content before displaying new data."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def display_payment_slips(self):
        """Set up Treeview for displaying payment slip data."""
        columns = ("Slip ID", "Order ID", "Upload Time")
        self.payment_slip_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.payment_slip_tree.heading(col, text=col)
            self.payment_slip_tree.column(col, width=150, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.payment_slip_tree.yview)
        self.payment_slip_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.payment_slip_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Canvas สำหรับแสดงรูปสลิป
        self.image_canvas = tk.Canvas(self.content_frame, width=330, height=400, bg="#e0f7ff", highlightthickness=0)
        self.image_canvas.pack(pady=20)

        # Fetch payment slip data and populate the Treeview
        self.populate_payment_slips()

    def populate_payment_slips(self, order_id_filter=None):
        """โหลดข้อมูลใบเสร็จจากฐานข้อมูล และกรองด้วย Order ID ถ้ามี"""
        if not hasattr(self, "payment_slip_tree"):
            return  # ✅ ป้องกัน error ถ้า Treeview ยังไม่ถูกสร้าง

        for row in self.payment_slip_tree.get_children():
            self.payment_slip_tree.delete(row)

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            # 🔎 กรองเฉพาะ Order ID ที่ต้องการ
            if order_id_filter:
                cursor.execute("SELECT slip_id, order_id, upload_time FROM payment_slips WHERE order_id = ?", (order_id_filter,))
            else:
                cursor.execute("SELECT slip_id, order_id, upload_time FROM payment_slips")

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                messagebox.showinfo("ผลลัพธ์", "ไม่มี Order ID ที่ท่านกรอก")
                return

            for row in rows:
                slip_id, order_id, upload_time = row
                item = self.payment_slip_tree.insert("", "end", values=(slip_id, order_id, upload_time))

                # ✅ เลือกแถบอัตโนมัติ และโหลดรูปภาพทันที
                if order_id_filter:
                    self.payment_slip_tree.selection_set(item)
                    self.payment_slip_tree.focus(item)
                    self.display_selected_payment_slip(order_id_filter)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching payment slips: {e}")

        # 📌 คลิกเลือกข้อมูล -> แสดงรูปภาพ
        self.payment_slip_tree.bind("<ButtonRelease-1>", self.display_selected_payment_slip)


    def display_selected_payment_slip(self, event_or_order_id):
        """Display the selected payment slip as an image (จากคลิก หรือจากการค้นหา)."""
        if isinstance(event_or_order_id, str):  # 🔍 ค้นหาจาก Order ID
            order_id = event_or_order_id
        else:  # 📌 คลิกที่ Treeview
            selected_item = self.payment_slip_tree.focus()
            if not selected_item:
                return
            slip_data = self.payment_slip_tree.item(selected_item)['values']
            if not slip_data:
                return
            order_id = slip_data[1]  # ดึง Order ID จากรายการที่เลือก

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            cursor.execute("SELECT slip FROM payment_slips WHERE order_id = ?", (order_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                slip_image_data = result[0]
                self.show_image_from_data(slip_image_data)
            else:
                messagebox.showwarning("No Image", "ไม่มีรูปสลิปสำหรับ Order ID นี้")

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading image: {e}")

    def show_image_from_data(self, image_data):
        """Convert binary data to image and display in the canvas."""
        try:
            # Convert binary data to an image
            image = Image.open(BytesIO(image_data))
            image = image.resize((350, 400), Image.LANCZOS)  
            photo = ImageTk.PhotoImage(image)

            # อัปเดตภาพใน Canvas
            self.image_canvas.delete("all")  # ลบรูปเก่าออกก่อน
            self.image_canvas.create_image(0, 0, image=photo, anchor="nw")
            self.image_canvas.image = photo  # ป้องกัน garbage collection

        except Exception as e:
            messagebox.showerror("Image Error", f"Error displaying image: {e}")

    def search_order(self):
        """ค้นหาข้อมูล Order ID และแสดงเฉพาะแถบนั้น"""
        order_id = self.search_var.get().strip()  
        if order_id:
            self.populate_payment_slips(order_id_filter=order_id)
        else:
            self.populate_payment_slips()  # รีเซ็ตแสดงทั้งหมด


    # -------------------------------------------------------------------------
    #                          3) กิจกรรมผู้ใช้ (User Activity)
    # -------------------------------------------------------------------------
    def show_user_activity(self):
        """แสดงตารางกิจกรรมของผู้ใช้"""
        self.clear_content()
        self.display_user_activity()

        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา Username:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 14),
            bg="#2980b9",
            fg="white",
            command=self.search_user_activity,  
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        self.display_user_activity()
    
    def clear_content(self):
        """Clear previous content before displaying new data."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def display_user_activity(self, username_filter=None):
        """ดึงข้อมูลจากตาราง `user_activity` และแสดงใน Treeview"""
        
        # ตรวจสอบว่ามี self.user_activity_tree หรือยัง
        if not hasattr(self, "user_activity_tree") or not self.user_activity_tree.winfo_exists():
            self.clear_content()
            
            columns = ("ID", "Username", "Action", "Timestamp")
            self.user_activity_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)

            for col in columns:
                self.user_activity_tree.heading(col, text=col)
                self.user_activity_tree.column(col, width=150, anchor="center")

            scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.user_activity_tree.yview)
            self.user_activity_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.user_activity_tree.pack(fill="both", expand=True, padx=20, pady=10)
            
        # ล้างข้อมูลเก่าออกก่อนเติมข้อมูลใหม่
        for row in self.user_activity_tree.get_children():
            self.user_activity_tree.delete(row)
        try:
            conn = sqlite3.connect("D:/Project Pythonnnnnn/bookstore.db")
            cursor = conn.cursor()
            if username_filter:
                cursor.execute("SELECT id, username, action, timestamp FROM user_activity WHERE username LIKE ?", (f"%{username_filter}%",))
            else:
                cursor.execute("SELECT id, username, action, timestamp FROM user_activity")
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                messagebox.showinfo("ผลลัพธ์", "ไม่พบกิจกรรมสำหรับ Username นี้")
                return
            # 🔹 เติมข้อมูลใหม่
            for row in rows:
                self.user_activity_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
            return
        if not hasattr(self, "user_activity_tree"):
            columns = ("ID", "Username", "Action", "Timestamp")
            self.user_activity_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)

            for col in columns:
                self.user_activity_tree.heading(col, text=col)
                self.user_activity_tree.column(col, width=150, anchor="center")

            scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.user_activity_tree.yview)
            self.user_activity_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.user_activity_tree.pack(fill="both", expand=True, padx=20, pady=10)

        for row in self.user_activity_tree.get_children():
            self.user_activity_tree.delete(row)

        # เพิ่มข้อมูลลง Treeview
        for row in rows:
            self.user_activity_tree.insert("", "end", values=row)

    def search_user_activity(self):
        """ค้นหาและแสดงเฉพาะกิจกรรมของ Username ที่ระบุ"""
        username = self.search_var.get().strip()
        if not hasattr(self, "user_activity_tree") or not self.user_activity_tree.winfo_exists():
            self.display_user_activity()  
        self.display_user_activity(username_filter=username)

    # -------------------------------------------------------------------------
    #                    2) จัดการที่อยู่จัดส่ง (Delivery Addresses)
    # -------------------------------------------------------------------------
    def show_order_items(self):
        """Display the order items."""
        self.clear_content()
        
        # แถบค้นหา
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา Order ID:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 14),
            bg="#2980b9",
            fg="white",
            command=self.search_user,  # ฟังก์ชันค้นหาตาม Order ID
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # Define a Treeview for order items
        self.order_tree = ttk.Treeview(self.content_frame, columns=("order_item_id", "order_id", "book_code", "quantity", "username"), show="headings")
        
        self.order_tree.heading("order_item_id", text="Order Item ID")
        self.order_tree.heading("order_id", text="Order ID")
        self.order_tree.heading("book_code", text="Book Code")
        self.order_tree.heading("quantity", text="Quantity")
        self.order_tree.heading("username", text="Username")
        
        # Set column alignment to center
        for col in ("order_item_id", "order_id", "book_code", "quantity", "username"):
            self.order_tree.column(col, anchor='center')  # Align all columns to the center
        
        # Add Scrollbar
        vertical_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.order_tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(self.content_frame, orient="horizontal", command=self.order_tree.xview)
        
        self.order_tree.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
        
        vertical_scrollbar.pack(side='right', fill='y')
        horizontal_scrollbar.pack(side='bottom', fill='x')
        self.order_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Style for the Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 11), rowheight=25)

        # Load data from the database
        self.populate_order_items()

    def search_user(self):
        """Search for order items by Order ID."""
        order_id = self.search_var.get().strip()  # ดึงค่า Order ID ที่ผู้ใช้กรอก
        if order_id:
            self.populate_order_items(order_id)  # ค้นหาข้อมูลตาม Order ID ที่กรอก
        else:
            self.populate_order_items()  # หากไม่ได้กรอก Order ID ให้แสดงข้อมูลทั้งหมด

    def populate_order_items(self, order_id=None):
        """Retrieve order item data from the database and display in treeview."""
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            # กรองข้อมูลตาม Order ID หากมีการระบุ Order ID
            if order_id:
                cursor.execute("SELECT * FROM order_item1 WHERE order_id LIKE ?", (f'%{order_id}%',))
            else:
                cursor.execute("SELECT * FROM order_item1")  # ดึงข้อมูลทั้งหมดหากไม่มีการกรอง

            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                self.order_tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")


    # -------------------------------------------------------------------------
    #                          3) จัดการสินค้า (Products)
    # -------------------------------------------------------------------------
    
    def show_products(self):
        self.clear_content()

        # แถบค้นหา
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา:", font=("KhanoonThin", 14), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_product_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_product_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 12),
            bg="#2980b9",
            fg="white",
            command=self.search_product,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # ปุ่ม เพิ่ม/แก้ไข/ลบ
        action_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        action_frame.pack(pady=5)

        tk.Button(
            action_frame,
            text="เพิ่มสินค้า",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.add_product,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="แก้ไขสินค้า",
            font=("KhanoonThin", 12),
            bg="#f1c40f",
            fg="white",
            command=self.edit_product,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="ลบสินค้า",
            font=("KhanoonThin", 12),
            bg="#e74c3c",
            fg="white",
            command=self.delete_product,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=10)

        # Treeview
        # *** ลบคอลัมน์ 'Image' ออกจาก Treeview ***
        columns = ("Code", "Name", "Genre", "Price", "Quantity")
        self.product_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.product_tree.heading(col, text=col)
            if col == "Code":
                self.product_tree.column(col, width=80, anchor='center')
            elif col == "Name":
                self.product_tree.column(col, width=250, anchor='w')
            elif col == "Genre":
                self.product_tree.column(col, width=100, anchor='center')
            elif col == "Price":
                self.product_tree.column(col, width=100, anchor='center')
            elif col == "Quantity":
                self.product_tree.column(col, width=80, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.product_tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # *** เพิ่ม Canvas สำหรับแสดงรูปภาพ ***
        self.image_canvas = tk.Canvas(self.content_frame, bg="#e0f7ff", width=290, height=400)
        self.image_canvas.pack(side="right", padx=20, pady=10)

        # *** Binding เพื่อแสดงรูปภาพเมื่อเลือกสินค้า ***
        self.product_tree.bind("<<TreeviewSelect>>", self.display_selected_product_image)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 11), rowheight=25)

        # ดึงข้อมูลจาก DB มาแสดง
        self.populate_products()

    def populate_products(self, query=None):
        """แสดงรายการสินค้าทั้งหมดใน treeview และเก็บ image_path"""
        for row in getattr(self, "product_tree", []).get_children():
            self.product_tree.delete(row)

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            if query:
                cursor.execute("""
                    SELECT code, name, genre, price, quantity, image_path
                    FROM products
                    WHERE code LIKE ? OR name LIKE ? OR genre LIKE ?
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("""
                    SELECT code, name, genre, price, quantity, image_path
                    FROM products
                """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                # ตัด image_path ออกจากการแสดงใน Treeview
                display_row = row[:-1]  
                self.product_tree.insert("", tk.END, values=display_row)
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

    def display_selected_product_image(self, event):
        """แสดงรูปภาพของสินค้าที่เลือกใน Canvas"""
        selected_item = self.product_tree.focus()
        if not selected_item:
            return

        product_data = self.product_tree.item(selected_item)['values']
        code = product_data[0]

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            cursor.execute("SELECT image_path FROM products WHERE code = ?", (code,))
            result = cursor.fetchone()
            conn.close()

            img_path = result[0] if result else None

            # ลบรูปภาพเก่า
            self.image_canvas.delete("all")

            if img_path and os.path.exists(img_path):
                img = load_image(img_path, (300, 300))
                if img:
                    self.image_canvas.create_image(150, 150, image=img, anchor="center")
                    self.image_canvas.image = img  # เก็บ reference เพื่อป้องกัน garbage collection
                else:
                    self.image_canvas.create_text(150, 150, text="ไม่สามารถโหลดรูปภาพ", font=("KhanoonThin", 14))
            else:
                self.image_canvas.create_text(150, 150, text="ไม่มีรูปภาพ", font=("KhanoonThin", 14))

        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

    def search_product(self):
        query = self.search_product_var.get().strip()
        self.populate_products(query)

    def add_product(self):
        AddEditProductWindow(self, "add")

    def edit_product(self):
        selected_item = self.product_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "กรุณาเลือกสินค้าที่ต้องการแก้ไข")
            return
        product_data = self.product_tree.item(selected_item)['values']
        # *** ดึง image_path จากฐานข้อมูล ***
        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            cursor.execute("SELECT image_path FROM products WHERE code = ?", (product_data[0],))
            result = cursor.fetchone()
            conn.close()
            image_path = result[0] if result else ""
            # *** รวม image_path เข้ากับ product_data ***
            full_product_data = list(product_data) + [image_path]
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")
            return

        AddEditProductWindow(self, "edit", full_product_data)

    def delete_product(self):
        selected_item = self.product_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "กรุณาเลือกสินค้าที่ต้องการลบ")
            return
        product_data = self.product_tree.item(selected_item)['values']
        confirm = messagebox.askyesno("Confirm Delete", f"คุณแน่ใจว่าต้องการลบสินค้า '{product_data[1]}' หรือไม่?")
        if confirm:
            try:
                conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE code = ?", (product_data[0],))
                conn.commit()
                conn.close()
                self.populate_products()
                messagebox.showinfo("Success", "ลบสินค้าเรียบร้อยแล้ว")
            except Exception as e:
                messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")
    
    
    # -------------------------------------------------------------------------
    #                        5) ประวัติการซื้อ (Purchase History)
    # -------------------------------------------------------------------------

    def show_purchase_history(self):
        self.clear_content()

        # แถบค้นหา
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา:", font=("KhanoonThin", 14), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_purchase_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_purchase_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 12),
            bg="#2980b9",
            fg="white",
            command=self.search_purchase_history,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # ตัวเลือกช่วงเวลา (วัน, เดือน, ปี)
        filter_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        filter_frame.pack(pady=10)

        # ตัวเลือกวัน
        tk.Label(filter_frame, text="วัน:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_day = tk.StringVar()
        self.filter_day.set("ทั้งหมด")
        day_options = ["ทั้งหมด"] + [str(i) for i in range(1, 32)]
        day_menu = ttk.Combobox(filter_frame, textvariable=self.filter_day, values=day_options, state="readonly")
        day_menu.pack(side="left", padx=5)

        # ตัวเลือกเดือน
        tk.Label(filter_frame, text="เดือน:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_month = tk.StringVar()
        self.filter_month.set("ทั้งหมด")
        month_options = ["ทั้งหมด"] + [str(i) for i in range(1, 13)]
        month_menu = ttk.Combobox(filter_frame, textvariable=self.filter_month, values=month_options, state="readonly")
        month_menu.pack(side="left", padx=5)

        # ตัวเลือกปี (จำกัด 2024-2026)
        tk.Label(filter_frame, text="ปี:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_year = tk.StringVar()
        self.filter_year.set("ทั้งหมด")
        year_options = ["ทั้งหมด", "2024", "2025", "2026"]
        year_menu = ttk.Combobox(filter_frame, textvariable=self.filter_year, values=year_options, state="readonly")
        year_menu.pack(side="left", padx=5)

        # ปุ่มกรองข้อมูล
        tk.Button(
            filter_frame,
            text="กรองข้อมูล",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.filter_purchase_history,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # Treeview
        columns = ("Order ID", "Username", "fullname","วันที่", "การรับ", "ยอดรวม", "ส่วนลด", "รายละเอียดการรับ")
        self.purchase_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            if col == "Order ID":
                self.purchase_tree.column(col, width=15, anchor='center')
            elif col == "Username":
                self.purchase_tree.column(col, width=10, anchor='center')
            elif col == "fullname":
                self.purchase_tree.column(col, width=30, anchor='center')
            elif col == "วันที่":
                self.purchase_tree.column(col, width=80, anchor='center')
            elif col == "การรับ":
                self.purchase_tree.column(col, width=60, anchor='center')
            elif col == "ยอดรวม":
                self.purchase_tree.column(col, width=25, anchor='center')
            elif col == "ส่วนลด":
                self.purchase_tree.column(col, width=10, anchor='center')
            elif col == "รายละเอียดการรับ":
                self.purchase_tree.column(col, width=130, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.purchase_tree.yview)
        self.purchase_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.purchase_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 10), rowheight=25)

        # ดึงข้อมูลจาก DB มาแสดง
        self.populate_purchase_history()

    def populate_purchase_history(self, day=None, month=None, year=None, query=None):
        """แสดงรายการประวัติการซื้อทั้งหมดใน treeview"""
        for row in getattr(self, "purchase_tree", []).get_children():
            self.purchase_tree.delete(row)

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            base_query = """
                SELECT 
                    o.order_id, 
                    o.username, 
                    m.fname || ' ' || m.lname AS fullname,  -- รวม fname และ lname เป็น fullname
                    o.order_time, 
                    o.pickup_method, 
                    o.total_price, 
                    o.discount, 
                    o.delivery_address
                FROM 
                    orders o
                JOIN 
                    mangauser m ON o.username = m.username
            """
            conditions = []
            params = []

            # เพิ่มการกรองตาม query ที่กรอกเข้ามา (ถ้ามี)
            if query:
                conditions.append("(o.username LIKE ? OR m.fname LIKE ? OR m.lname LIKE ?)")
                params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])

            # กรองตามปี
            if year and year != "ทั้งหมด":
                conditions.append("strftime('%Y', o.order_time) = ?")
                params.append(year)

            # กรองตามเดือน
            if month and month != "ทั้งหมด":
                conditions.append("strftime('%m', o.order_time) = ?")
                params.append(month.zfill(2))  # เติม 0 ข้างหน้า (01, 02, ..., 12)

            # กรองตามวัน
            if day and day != "ทั้งหมด":
                conditions.append("strftime('%d', o.order_time) = ?")
                params.append(day.zfill(2))  # เติม 0 ข้างหน้า (01, 02, ..., 31)

            # เพิ่มเงื่อนไขการกรองถ้ามี
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            base_query += " ORDER BY o.order_time DESC"

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            conn.close()

            # เพิ่มข้อมูลลงใน Treeview
            for row in rows:
                self.purchase_tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

    def search_purchase_history(self):
        query = self.search_purchase_var.get().strip()
        day = self.filter_day.get()
        month = self.filter_month.get()
        year = self.filter_year.get()
        self.populate_purchase_history(day, month, year, query)

    def filter_purchase_history(self):
        day = self.filter_day.get()
        month = self.filter_month.get()
        year = self.filter_year.get()
        query = self.search_purchase_var.get().strip()
        self.populate_purchase_history(day, month, year, query)

    # -------------------------------------------------------------------------
    #                           6) สรุปยอดขาย (Sales Summary)
    # -------------------------------------------------------------------------
        
    def show_sales_summary(self):
        self.clear_content()

        # แถบค้นหา
        search_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="ค้นหา:", font=("KhanoonThin", 14), bg="#e0f7ff").pack(side="left", padx=5)
        self.search_summary_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_summary_var, font=("KhanoonThin", 12), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="🔍",
            font=("KhanoonThin", 12),
            bg="#2980b9",
            fg="white",
            command=self.search_show_sales_summary,
            cursor="hand2",
            padx=10, pady=5
        ).pack(side="left", padx=5)

        # ตัวเลือกช่วงเวลา (วัน, เดือน, ปี)
        filter_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        filter_frame.pack(pady=10)

        # ตัวเลือกวัน
        tk.Label(filter_frame, text="วัน:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_day = tk.StringVar()
        self.filter_day.set("ทั้งหมด")
        day_options = ["ทั้งหมด"] + [str(i) for i in range(1, 32)]
        day_menu = ttk.Combobox(filter_frame, textvariable=self.filter_day, values=day_options, state="readonly")
        day_menu.pack(side="left", padx=5)

        # ตัวเลือกเดือน
        tk.Label(filter_frame, text="เดือน:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_month = tk.StringVar()
        self.filter_month.set("ทั้งหมด")
        month_options = ["ทั้งหมด"] + [str(i) for i in range(1, 13)]
        month_menu = ttk.Combobox(filter_frame, textvariable=self.filter_month, values=month_options, state="readonly")
        month_menu.pack(side="left", padx=5)

        # ตัวเลือกปี (จำกัด 2024-2026)
        tk.Label(filter_frame, text="ปี:", font=("KhanoonThin", 12), bg="#e0f7ff").pack(side="left", padx=5)
        self.filter_year = tk.StringVar()
        self.filter_year.set("ทั้งหมด")
        year_options = ["ทั้งหมด", "2024", "2025", "2026"]
        year_menu = ttk.Combobox(filter_frame, textvariable=self.filter_year, values=year_options, state="readonly")
        year_menu.pack(side="left", padx=5)

        # ปุ่มกรองข้อมูล
        self.filter_button = tk.Button(filter_frame, 
            text="กรองข้อมูล", 
            font=("KhanoonThin", 12), 
            command=self.apply_filters,
            bg="#27ae60", 
            fg="white",     
            padx=10, pady=5)
        self.filter_button.grid(row=0, column=4, padx=10)


        # Treeview
        columns = ("รหัสสินค้า", "ชื่อสินค้า","หมวดหมู่", "ราคาสินค้า", "จำนวนที่ขาย", "ยอดรวม")
        self.summary_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.summary_tree.heading(col, text=col)
            if col == "รหัสสินค้า":
                self.summary_tree.column(col, width=15, anchor='center')
            elif col == "ชื่อสินค้า":
                self.summary_tree.column(col, width=50, anchor='center')
            elif col == "หมวดหมู่":
                self.summary_tree.column(col, width=50, anchor='center')
            elif col == "ราคาสินค้า":
                self.summary_tree.column(col, width=80, anchor='center')
            elif col == "จำนวนที่ขาย":
                self.summary_tree.column(col, width=60, anchor='center')
            elif col == "ยอดรวม":
                self.summary_tree.column(col, width=30, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.summary_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 10), rowheight=25)

        # ดึงข้อมูลยอดขายจากฐานข้อมูล
        self.populate_sales_summary()

    def populate_sales_summary(self, day=None, month=None, year=None, query=None):
        """แสดงรายการประวัติการซื้อทั้งหมดใน treeview พร้อมรวมยอดรวมและจำนวนสินค้าทั้งหมด"""
        for row in getattr(self, "summary_tree", []).get_children():
            self.summary_tree.delete(row)

        total_quantity = 0  # รวมจำนวนสินค้าทั้งหมด
        total_sales = 0  # รวมยอดขายทั้งหมด

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            query_str = """
                SELECT code, name, genre, price, quantity_removed, (price * quantity_removed) AS total
                FROM products
                WHERE 1=1
            """
            params = []

            # กรองตาม query ที่กรอกเข้ามา
            if query:
                query_str += " AND (code LIKE ? OR name LIKE ? OR genre LIKE ?)"
                params += (f'%{query}%', f'%{query}%', f'%{query}%')

            # กรองตามปี
            if year and year != "ทั้งหมด":
                query_str += " AND strftime('%Y', sold_at) = ?"
                params += (year,)

            # กรองตามเดือน
            if month and month != "ทั้งหมด":
                query_str += " AND strftime('%m', sold_at) = ?"
                params += (month.zfill(2),)

            # กรองตามวัน
            if day and day != "ทั้งหมด":
                query_str += " AND strftime('%d', sold_at) = ?"
                params += (day.zfill(2),)

            query_str += " ORDER BY sold_at DESC"
            cursor.execute(query_str, params)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                self.summary_tree.insert("", tk.END, values=row)
                total_quantity += row[4]  # จำนวนที่ขาย
                total_sales += row[5]  # ยอดรวม

            # แสดงผลรวมด้านล่างในสีเหลืองและสีแดง
            self.total_quantity_label.config(text=f"รวมจำนวนสินค้า: {total_quantity:,.2f}", fg="blue",)
            self.total_sales_label.config(text=f"ยอดรวมทั้งหมด: {total_sales:,.2f}", fg="red")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

    def show_sales_summary(self):
        """แสดง UI และผลรวม"""
        self.clear_content()

        # ส่วนแสดงผลรวม
        total_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        total_frame.pack(pady=10, fill="x", anchor="s")  # จัดให้ตรงด้านล่างสุด

        self.total_quantity_label = tk.Label(total_frame, text="รวมจำนวนสินค้า: 0", font=("KhanoonThin", 14), bg="#e0f7ff", fg="blue")
        self.total_quantity_label.pack(side="left", padx=20)

        self.total_sales_label = tk.Label(total_frame, text="ยอดรวมทั้งหมด: 0", font=("KhanoonThin", 14), bg="#e0f7ff", fg="red")
        self.total_sales_label.pack(side="left", padx=20)
        

        # ส่วน Treeview แสดงข้อมูลยอดขาย
        columns = ("รหัสสินค้า", "ชื่อสินค้า", "หมวดหมู่", "ราคาสินค้า", "จำนวนที่ขาย", "ยอดรวม")
        self.summary_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.summary_tree.heading(col, text=col)
            if col == "รหัสสินค้า":
                self.summary_tree.column(col, width=15, anchor='center')
            elif col == "ชื่อสินค้า":
                self.summary_tree.column(col, width=50, anchor='center')
            elif col == "หมวดหมู่":
                self.summary_tree.column(col, width=50, anchor='center')
            elif col == "ราคาสินค้า":
                self.summary_tree.column(col, width=80, anchor='center')
            elif col == "จำนวนที่ขาย":
                self.summary_tree.column(col, width=60, anchor='center')
            elif col == "ยอดรวม":
                self.summary_tree.column(col, width=30, anchor='center')

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.summary_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("KhanoonThin", 12, "bold"))
        style.configure("Treeview", font=("KhanoonThin", 10), rowheight=25)

        # ฟอร์มกรองข้อมูล
        filter_frame = tk.Frame(self.content_frame, bg="#e0f7ff")
        filter_frame.pack(pady=10, fill="x")

        # Filter: ปี
        self.year_filter = ttk.Combobox(filter_frame, values=["ทั้งหมด", "2024", "2025", "2026"], state="readonly")
        self.year_filter.set("ทั้งหมด")
        self.year_filter.grid(row=0, column=0, padx=10)

        # Filter: เดือน
        self.month_filter = ttk.Combobox(filter_frame, values=["ทั้งหมด", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], state="readonly")
        self.month_filter.set("ทั้งหมด")
        self.month_filter.grid(row=0, column=1, padx=10)

        # Filter: วัน
        self.day_filter = ttk.Combobox(filter_frame, values=["ทั้งหมด", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"], state="readonly")
        self.day_filter.set("ทั้งหมด")
        self.day_filter.grid(row=0, column=2, padx=10)

        # Filter: คำค้น
        self.query_filter = tk.Entry(filter_frame, font=("KhanoonThin", 12))
        self.query_filter.grid(row=0, column=3, padx=10)

        # ปุ่มกรองข้อมูล
        # ปุ่มกรองข้อมูล
        self.filter_button = tk.Button(filter_frame, 
                                    text="กรองข้อมูล", 
                                    font=("KhanoonThin", 12), 
                                    command=self.apply_filters,
                                    bg="#27ae60",  # สีเขียว
                                    fg="white",     # สีตัวอักษรเป็นขาว
                                    padx=10, pady=15)
        self.filter_button.grid(row=0, column=4, padx=12)
        

        # ดึงข้อมูลยอดขายจากฐานข้อมูล
        self.populate_sales_summary()

    def apply_filters(self):
        """ฟังก์ชันสำหรับใช้กรองข้อมูลตามที่เลือก"""
        day = self.day_filter.get()
        month = self.month_filter.get()
        year = self.year_filter.get()
        query = self.query_filter.get()
        self.populate_sales_summary(day=day, month=month, year=year, query=query)


    def search_show_sales_summary(self):
        query = self.search_summary_var.get().strip()
        day = self.filter_day.get()
        month = self.filter_month.get()
        year = self.filter_year.get()
        self.populate_sales_summary(day, month, year, query)

    def filter_show_sales_summary(self):
        day = self.filter_day.get()
        month = self.filter_month.get()
        year = self.filter_year.get()
        query = self.search_summary_var.get().strip()
        self.populate_sales_summary(day, month, year, query)

    
    # -------------------------------------------------------------------------
    #                          4) อื่น ๆ
    # -------------------------------------------------------------------------
    def logout(self):
        self.root.destroy()
        messagebox.showinfo("Log Out", "คุณได้ออกจากระบบแล้ว")
    

# =============================================================================
#               (1) AddEditUserWindow : จัดการผู้ใช้ (mangauser)
# =============================================================================
class AddEditUserWindow:
    def __init__(self, admin_page, mode, user_data=None):
        self.admin_page = admin_page
        self.mode = mode  # 'add' / 'edit'
        self.user_data = user_data

        self.window = tk.Toplevel(admin_page.root)
        self.window.title("เพิ่มผู้ใช้" if mode == "add" else "แก้ไขผู้ใช้")
        center_window(self.window, 700, 600)  # ปรับขนาดหน้าต่างเป็น 700x600
        self.window.configure(bg="#e0f7ff")

        # ปุ่ม Back
        tk.Button(
            self.window,
            text="Back",
            font=("KhanoonThin", 12),
            bg="#7f8c8d",
            fg="white",
            command=self.window.destroy,
            cursor="hand2",
            padx=10, pady=5
        ).pack(anchor='nw', padx=10, pady=10)

        # ฟอร์ม
        form_frame = tk.Frame(self.window, bg="#e0f7ff")
        form_frame.pack(pady=20)

        # 1. ปรับช่องเบอร์โทรให้รับ 10 หลัก และเพิ่มการตรวจสอบ
        def create_label_entry(label_text, row, is_password=False):
            label = tk.Label(form_frame, text=label_text, font=("KhanoonThin", 12), bg="#e0f7ff")
            label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            if is_password:
                entry = tk.Entry(form_frame, font=("KhanoonThin", 12), width=30)  # รหัสผ่านไม่ใช้ * แต่แสดงรหัสจริง
            else:
                entry = tk.Entry(form_frame, font=("KhanoonThin", 12), width=30)
            entry.grid(row=row, column=1, padx=10, pady=10)
            return entry

        # ปรับเบอร์โทรให้ตรวจสอบจำนวนเลข
        def validate_phone_number(phone):
            if len(phone) != 10 or not phone.isdigit():
                return False
            return True

        # เปลี่ยนจาก DateEntry เป็น Entry สำหรับกรอกวันเกิดในรูปแบบ DD/MM/YYYY
        self.username_entry = create_label_entry("Username:", 0)
        self.fname_entry    = create_label_entry("First Name:", 1)
        self.lname_entry    = create_label_entry("Last Name:", 2)
        self.birth_entry = create_label_entry("Birth Date (DD/MM/YYYY):", 3)  # ปรับเป็น Entry แทน DateEntry
        self.email_entry    = create_label_entry("Email:", 4)
        self.phone_entry    = create_label_entry("Phone Number:", 5)
        self.password_entry = create_label_entry("Password:", 6, is_password=True)

        if mode == "edit" and user_data:
            # user_data = [id, username, fname, lname, birth, email, phone, ...]
            self.username_entry.insert(0, user_data[1])
            self.fname_entry.insert(0,    user_data[2])
            self.lname_entry.insert(0,    user_data[3])
            self.birth_entry.insert(0,    user_data[4])  # แสดงวันเกิดในรูปแบบ DD/MM/YYYY
            self.email_entry.insert(0,    user_data[5])
            self.phone_entry.insert(0,    user_data[6])
            # ถ้ามี password ใน user_data index 7
            if len(user_data) > 7:
                self.password_entry.insert(0, user_data[7])

        # ปุ่ม Save
        save_button = tk.Button(
            self.window,
            text="Save",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.save_user,
            cursor="hand2",
            padx=10, pady=5
        )
        save_button.pack(pady=20)

    def save_user(self):
        username = self.username_entry.get().strip()
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        birth = self.birth_entry.get().strip()  # รับค่าจาก Entry (วันเกิด)
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate and format birth date (check if it's in DD/MM/YYYY format)
        try:
            formatted_birth = datetime.strptime(birth, "%d/%m/%Y").strftime("%d/%m/%Y")  # Convert to DD/MM/YYYY format
        except ValueError:
            messagebox.showwarning("Birth Date Error", "กรุณากรอกวันเกิดในรูปแบบ DD/MM/YYYY")
            return

        # ตรวจสอบข้อมูลที่กรอก
        if not username or not fname or not lname or not birth or not email or not phone or not password:
            messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        if '@' not in email or not email.endswith('.com'):
            messagebox.showwarning("Email Error", "อีเมลไม่ถูกต้อง (ต้องมี @ และลงท้าย .com)")
            return

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.com$'
        if not re.match(email_pattern, email):
            messagebox.showwarning("Email Error", "รูปแบบอีเมลไม่ถูกต้อง")
            return

        if len(phone) != 10 or not phone.isdigit():
            messagebox.showwarning("Phone Error", "เบอร์โทรต้องมี 10 หลัก และเป็นตัวเลขเท่านั้น")
            return

        if len(password) < 10:
            messagebox.showwarning("Password Error", "รหัสผ่านต้อง >= 10 ตัวอักษร")
            return

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            if self.mode == "add":
                # ตรวจสอบ username ซ้ำ
                cursor.execute("SELECT * FROM mangauser WHERE username = ?", (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username ถูกใช้แล้ว")
                    conn.close()
                    return

                cursor.execute("""
                    INSERT INTO mangauser (username, fname, lname, birth, email, phonenum, password, role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, fname, lname, formatted_birth, email, phone, password, 'user'))
                messagebox.showinfo("Success", "เพิ่มผู้ใช้เรียบร้อยแล้ว")

            elif self.mode == "edit" and self.user_data:
                user_id = self.user_data[0]
                cursor.execute("""
                    UPDATE mangauser
                    SET username=?, fname=?, lname=?, birth=?, email=?, phonenum=?, password=?
                    WHERE id=?
                """, (username, fname, lname, formatted_birth, email, phone, password, user_id))
                messagebox.showinfo("Success", "แก้ไขผู้ใช้เรียบร้อยแล้ว")

            conn.commit()
            conn.close()
            self.admin_page.populate_user_info()
            self.window.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username ซ้ำในระบบ")
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")

# =============================================================================
#         (2) AddEditDeliveryAddressWindow : จัดการที่อยู่จัดส่ง (orders)
# =============================================================================
class AddEditDeliveryAddressWindow:
    def __init__(self, admin_page, mode, address_data=None):
        self.admin_page = admin_page
        self.mode = mode
        self.address_data = address_data
        self.current_user = current_user

        self.window = tk.Toplevel(admin_page.root)
        self.window.title("เพิ่มที่อยู่จัดส่ง" if mode == "add" else "แก้ไขที่อยู่จัดส่ง")
        center_window(self.window, 700, 600)
        self.window.configure(bg="#e0f7ff")

        # ปุ่มกลับ
        tk.Button(
            self.window,
            text="Back",
            font=("KhanoonThin", 12),
            bg="#7f8c8d",
            fg="white",
            command=self.window.destroy,
            cursor="hand2",
            padx=10, pady=5
        ).pack(anchor='nw', padx=10, pady=10)

        # ฟอร์มสำหรับกรอกข้อมูล
        form_frame = tk.Frame(self.window, bg="#e0f7ff")
        form_frame.pack(pady=20)

        def create_label_entry(label_text, row):
            label = tk.Label(form_frame, text=label_text, font=("KhanoonThin", 12), bg="#e0f7ff")
            label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            entry = tk.Entry(form_frame, font=("KhanoonThin", 12), width=30)
            entry.grid(row=row, column=1, padx=10, pady=10)
            return entry

        self.fullname_entry = create_label_entry("Full Name:", 1)
        self.house_number_entry = create_label_entry("House Number:", 2)
        self.subdistrict_entry = create_label_entry("Subdistrict:", 3)
        self.district_entry = create_label_entry("District:", 4)
        self.province_entry = create_label_entry("Province:", 5)
        self.postal_code_entry = create_label_entry("Postal Code:", 6)
        self.phone_entry = create_label_entry("Phone Number:", 7)

        if mode == "edit" and address_data:
            self.fullname_entry.insert(0, address_data[2])
            self.house_number_entry.insert(0, address_data[3])
            self.subdistrict_entry.insert(0, address_data[4])
            self.district_entry.insert(0, address_data[5])
            self.province_entry.insert(0, address_data[6])
            self.postal_code_entry.insert(0, address_data[7])
            self.phone_entry.insert(0, address_data[8])

        # ปุ่ม Save
        save_button = tk.Button(
            self.window,
            text="Save",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.save_address,
            cursor="hand2",
            padx=10, pady=5
        )
        save_button.pack(pady=20)

    def save_address(self):
        if not self.current_user:  
            messagebox.showerror("Error", "ไม่พบชื่อผู้ใช้")
            return

        # รับข้อมูลจากฟอร์ม
        fullname = self.fullname_entry.get().strip()
        house_number = self.house_number_entry.get().strip()
        subdistrict = self.subdistrict_entry.get().strip()
        district = self.district_entry.get().strip()
        province = self.province_entry.get().strip()
        postal_code = self.postal_code_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not fullname or not house_number or not subdistrict or not district or not province or not postal_code or not phone:
            messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        try:
            conn = sqlite3.connect("bookstore.db")
            cursor = conn.cursor()

            if self.mode == "add":
                # ✅ เพิ่มที่อยู่ใหม่
                cursor.execute("""
                    INSERT INTO user_address_new (username, fullname, house_number, subdistrict, district, province, postal_code, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.current_user, fullname, house_number, subdistrict, district, province, postal_code, phone))
            
            elif self.mode == "edit":
                # ✅ อัปเดตที่อยู่ที่มีอยู่แล้ว
                address_id = self.address_data[0]  # ดึงไอดีจาก address_data
                cursor.execute("""
                    UPDATE user_address_new
                    SET fullname = ?, house_number = ?, subdistrict = ?, district = ?, province = ?, postal_code = ?, phone = ?
                    WHERE id = ? AND username = ?
                """, (fullname, house_number, subdistrict, district, province, postal_code, phone, address_id, self.current_user))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "ที่อยู่ถูกบันทึกเรียบร้อยแล้ว")
            self.admin_page.populate_delivery_addresses()  # อัพเดตตารางที่อยู่
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")


# =============================================================================
#   (3) AddEditProductWindow : จัดการสินค้า (products ใน bookstock.db)
# =============================================================================
class AddEditProductWindow:
    """
    ฟอร์มสำหรับ 'เพิ่ม' หรือ 'แก้ไข' ข้อมูลสินค้าในตาราง products (DB: bookstock.db)
    """
    
    def initialize_database():
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()
    
        # ตรวจสอบว่า 'image_path' มีอยู่ในตาราง products หรือยัง
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if "image_path" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
            print("Added 'image_path' column to 'products' table.")

        conn.commit()
        conn.close()

    def __init__(self, admin_page, mode, product_data=None):
        self.admin_page = admin_page
        self.mode = mode
        self.product_data = product_data

        self.window = tk.Toplevel(admin_page.root)
        self.window.title("เพิ่มสินค้า" if mode == "add" else "แก้ไขสินค้า")
        center_window(self.window, 700, 600)  # ปรับขนาดหน้าต่างเป็น 700x600
        self.window.configure(bg="#e0f7ff")

        # ปุ่ม Back
        tk.Button(
            self.window,
            text="Back",
            font=("KhanoonThin", 12),
            bg="#7f8c8d",
            fg="white",
            command=self.window.destroy,
            cursor="hand2",
            padx=10, pady=5
        ).pack(anchor='nw', padx=10, pady=10)

        # ฟอร์ม
        form_frame = tk.Frame(self.window, bg="#e0f7ff")
        form_frame.pack(pady=20)

        def create_label_entry(label_text, row):
            label = tk.Label(form_frame, text=label_text, font=("KhanoonThin", 12), bg="#e0f7ff")
            label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            entry = tk.Entry(form_frame, font=("KhanoonThin", 12), width=30)
            entry.grid(row=row, column=1, padx=10, pady=10)
            return entry

        self.code_entry     = create_label_entry("Code:", 0)
        self.name_entry     = create_label_entry("Name:", 1)
        self.genre_entry    = create_label_entry("Genre:", 2)
        self.price_entry    = create_label_entry("Price:", 3)
        self.quantity_entry = create_label_entry("Quantity:", 4)
        self.image_path_entry = create_label_entry("Image Path:", 5)

        # ปุ่มเลือกภาพ
        choose_image_button = tk.Button(
            form_frame,
            text="เลือกภาพ",
            font=("KhanoonThin", 10),
            bg="#2980b9",
            fg="white",
            command=self.choose_image,
            cursor="hand2",
            padx=5, pady=2
        )
        choose_image_button.grid(row=5, column=2, padx=5, pady=10)

        # ถ้าเป็น edit ให้เติมข้อมูล
        if mode == "edit" and product_data:
            self.code_entry.insert(0,       product_data[0])
            self.name_entry.insert(0,       product_data[1])
            self.genre_entry.insert(0,      product_data[2])
            self.price_entry.insert(0,      product_data[3])
            self.quantity_entry.insert(0,   product_data[4])
            if len(product_data) > 5:
                self.image_path_entry.insert(0, product_data[5])

        # ปุ่ม Save
        save_button = tk.Button(
            self.window,
            text="Save",
            font=("KhanoonThin", 12),
            bg="#27ae60",
            fg="white",
            command=self.save_product,
            cursor="hand2",
            padx=10, pady=5
        )
        save_button.pack(pady=20)

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            title="เลือกภาพสินค้า",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)

    def save_product(self):
        code     = self.code_entry.get().strip()
        name     = self.name_entry.get().strip()
        genre    = self.genre_entry.get().strip()
        price    = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        img_path = self.image_path_entry.get().strip()

        # ตรวจสอบ
        if not code or not name or not genre or not price or not quantity:
            messagebox.showwarning("Input Error", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        # ตรวจสอบราคา: ต้องเป็นตัวเลข >=0 และสามารถมีทศนิยมได้
        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Price Error", "ราคาต้องเป็นตัวเลขไม่ติดลบ")
            return

        # ตรวจสอบจำนวน: ต้องเป็นตัวเลขจำนวนเต็ม >=0
        if not quantity.isdigit():
            messagebox.showwarning("Quantity Error", "จำนวนสินค้าต้องเป็นตัวเลขจำนวนเต็มไม่ติดลบ")
            return
        quantity_val = int(quantity)

        # ตรวจสอบรูปภาพ: ในโหมด 'add' ต้องเลือกไฟล์รูปภาพ และในโหมด 'edit' ถ้าไม่ได้เลือกใหม่ ให้เก็บรูปเดิม
        if self.mode == "add":
            if not img_path:
                messagebox.showwarning("Image Error", "กรุณาเลือกไฟล์รูปภาพ")
                return
            if not os.path.exists(img_path):
                messagebox.showwarning("Image Error", "ไม่พบไฟล์รูปภาพ")
                return
        elif self.mode == "edit":
            if not img_path:
                # ไม่ได้เลือกภาพใหม่ ให้ใช้รูปเดิม
                img_path = self.product_data[5] if len(self.product_data) > 5 else ""
            else:
                if not os.path.exists(img_path):
                    messagebox.showwarning("Image Error", "ไม่พบไฟล์รูปภาพ")
                    return

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            if self.mode == "add":
                # ตรวจสอบ code ซ้ำ
                cursor.execute("SELECT * FROM products WHERE code = ?", (code,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "รหัสสินค้านี้ถูกใช้งานแล้ว")
                    conn.close()
                    return

                cursor.execute("""
                    INSERT INTO products (code, name, genre, price, quantity, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, name, genre, price_val, quantity_val, img_path))
                messagebox.showinfo("Success", "เพิ่มสินค้าเรียบร้อยแล้ว")

            elif self.mode == "edit" and self.product_data:
                old_code = self.product_data[0]
                cursor.execute("""
                    UPDATE products
                    SET code=?, name=?, genre=?, price=?, quantity=?, image_path=?
                    WHERE code=?
                """, (code, name, genre, price_val, quantity_val, img_path, old_code))
                messagebox.showinfo("Success", "แก้ไขสินค้าเรียบร้อยแล้ว")

            conn.commit()
            conn.close()
            self.admin_page.populate_products()
            self.window.destroy()
            messagebox.showinfo("Success", "บันทึกข้อมูลสินค้าเรียบร้อยแล้ว")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "รหัสสินค้านี้ถูกใช้งานแล้ว")
        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาด: {e}")
    def save_order(self, total_price, discount, pickup_method):
        global current_user  # ใช้ชื่อผู้ใช้ที่ล็อกอินจากตัวแปร global

        # ตรวจสอบว่าผู้ใช้ที่ล็อกอินมีค่า username หรือไม่
        if not current_user:
            messagebox.showerror("Error", "ไม่พบข้อมูลผู้ใช้ที่ล็อกอิน")
            return

        try:
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()

            # เก็บเวลาการสั่งซื้อ
            order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # สั่งซื้อใหม่โดยการเพิ่มข้อมูลลงในตาราง orders
            cursor.execute("""
                INSERT INTO orders (username, order_time, pickup_method, total_price, discount)
                VALUES (?, ?, ?, ?, ?)
            """, (current_user, order_time, pickup_method, total_price, discount))
            
            conn.commit()
            conn.close()

            # แสดงข้อความแจ้งเตือนเมื่อบันทึกข้อมูลสำเร็จ
            messagebox.showinfo("Success", "คำสั่งซื้อถูกบันทึกเรียบร้อยแล้ว")

        except Exception as e:
            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาดในการบันทึกคำสั่งซื้อ: {e}")


# =============================================================================
#                         MAIN PROGRAM START
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ซ่อนหน้าต่างหลัก
    admin_page = AdminPage(root)  # สร้างหน้า Admin
    root.mainloop()
