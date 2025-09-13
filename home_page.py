import tkinter as tk
from tkinter import messagebox, PhotoImage, ttk
from PIL import Image, ImageTk # type: ignore
from fpdf import FPDF # type: ignore
import sqlite3
import os 
import subprocess
import customtkinter as ctk # type: ignore
import datetime
import time
from datetime import datetime
from tempfile import NamedTemporaryFile
from tkinter import filedialog
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator # type: ignore
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
def load_current_user():
    try:
        with open("current_user.json", "r") as f:
            data = json.load(f)
            return data["current_user"]
    except FileNotFoundError:
        return None  # หรือค่าเริ่มต้นอื่นๆ

# ใช้งานที่ไหนก็ได้ใน home_page.py
current_user = load_current_user()

if current_user:
    # ใช้ current_user ในการแสดงข้อมูลหรือปรับ UI
    print(f"Current user is: {current_user}")
else:
    messagebox.showwarning("Error", "ไม่พบผู้ใช้ที่ล็อกอิน")
    # หรือแสดงหน้าให้ผู้ใช้ล็อกอินใหม่
# --------------------- Database Setup ---------------------
def initialize_database():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    
    #user_activity
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES mangauser(username)
            )
        ''')  
    
    # ตารางสินค้า
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            genre TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            image_path TEXT NOT NULL
        )
    ''')
    
    # ตารางข้อมูลผู้ใช้
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mangauser (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            fname TEXT,
            lname TEXT,
            birth TEXT,
            email TEXT,
            phonenum TEXT,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # ตารางคำสั่งซื้อ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            order_time TEXT NOT NULL,
            pickup_method TEXT NOT NULL,
            delivery_address TEXT,
            total_price REAL NOT NULL,
            discount REAL NOT NULL,
            FOREIGN KEY(username) REFERENCES mangauser(username)
        )
    ''')

    # ตารางรายการสินค้าภายในคำสั่งซื้อ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(product_code) REFERENCES products(code)
        )
    ''')

    # ตารางสำหรับเก็บยอดขาย
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            username TEXT PRIMARY KEY,
            total_sales REAL DEFAULT 0,
            FOREIGN KEY(username) REFERENCES mangauser(username)
        )
    ''')

    # ตารางที่อยู่ของผู้ใช้ (รวมอยู่ในไฟล์ DB เดียวกัน)
    # 1. สร้างตารางใหม่ที่มี `fullname` แทน `fname` และ `lname`
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_address_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            fullname TEXT NOT NULL,  
            house_number TEXT NOT NULL,
            subdistrict TEXT NOT NULL,
            district TEXT NOT NULL,
            province TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES mangauser(username)
        )
    ''')

    # ตรวจสอบว่าตาราง products มีข้อมูลหรือยัง
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # เพิ่มข้อมูลสินค้าตัวอย่าง
        products = [
            # Action
            ("A01", "KAGURABACHI คากุระบาจิ", "Action", 115, 50, r"c:\Users\acer\Pictures\PJ\book\Action\A01.png"),
            ("A02", "TOKYO ALIENS โตเกียวเอเลี่ยน", "Action", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Action\A02.png"),
            ("A03", "SAKAMOTO DAYS ซาคาโมโตะเดส์", "Action", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Action\A03.png"),
            ("A04", "WIND BREAKER วินด์เบรกเกอร์", "Action", 165, 50, r"C:\Users\acer\Pictures\PJ\book\Action\A04.png"),
            ("A05", "KAJUYU No.8 ไคจูหมายเลข 8", "Action", 165, 50, r"C:\Users\acer\Pictures\PJ\book\Action\A05.png"),
            # Drama
            ("D01", "Unsung Cinderella เภสัชกรสาวหัวใจแกร่ง", "Drama", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Drama\D01.png"),
            ("D02", "Stink and Poison สืบคดีปริศนา หมอยาตำรับโคมแดง", "Drama", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Drama\D02.png"),
            ("D03", "Attack on Titan ผ่าพิภพไททัน", "Drama", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Drama\D03.png"),
            ("D04", "FRIEREN คำอธิฐานในวันที่จากลา", "Drama", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Drama\D04.png"),
            ("D05", "Oshi no Ko เกิดใหม่เป็นลูกโอชิ", "Drama", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Drama\D05.png"),
            # Romance
            ("R01", "Kimi ni Todoke ฝากใจไปถึงเธอ", "Romance", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Romance\R01.png"),
            ("R02", "คุณอาเรียโต๊ะข้างๆพูดรัสเซียหวานใส่ซะหัวใจจะวาย", "Romance", 145, 50, r"C:\Users\acer\Pictures\PJ\book\Romance\R02.png"),
            ("R03", "ดอกรักผลิบานที่กลางใจ", "Romance", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Romance\R03.png"),
            ("R04", "หากว่ารักมองเห็นได้ด้วยตา", "Romance", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Romance\R04.png"),
            ("R05", "เด็กหนุ่มจอมเพ้อฝันผู้ตื่นมามองความเป็นจริง", "Romance", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Romance\R05.png"),
            # Horror
            ("H01", "หน้าร้อนที่ฮิคารุจากไป", "Horror", 145, 50, r"C:\Users\acer\Pictures\PJ\book\Horror\H01.png"),
            ("H02", "คณะประพันธกรจรจัด BEAST", "Horror", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Horror\H02.png"),
            ("H03", "Tokyo Ghoul โตเกียวกูล", "Horror", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Horror\H03.png"),
            ("H04", "Jujutsu Kaisen มหาเวทย์ผนึกมาร", "Horror", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Horror\H04.png"),
            ("H05", "Jigoku raku สุขาวดีอเวจี", "Horror", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Horror\H05.png"),
            # Fantasy
            ("F01", "Re:ZERO รีเซทชีวิต ฝ่าวิกฤตต่างโลก", "Fantasy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Fantasy\F01.png"),
            ("F02", "เกิดใหม่ทั้งทีก็เป็นสไลม์ไปซะแล้ว", "Fantasy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Fantasy\F02.png"),
            ("F03", "The Rising of the Shield Hero ผู้กล้าโล่ผงาด", "Fantasy", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Fantasy\F03.png"),
            ("F04", "Black Clover แบล็กโคลเวอร์", "Fantasy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Fantasy\F04.png"),
            ("F05", "Solo Leveling วันแมนอาร์มี", "Fantasy", 155, 50, r"C:\Users\acer\Pictures\PJ\book\Fantasy\F05.png"),
            # Comedy
            ("C01", "ขอให้โชคดีมีชัยในโลกแฟนตาซี", "Comedy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Comedy\C01.png"),
            ("C02", "One Punch Man วันพันช์แมน", "Comedy", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Comedy\C02.png"),
            ("C03", "ไซคิ หนุ่มพลังจิตอลเวง", "Comedy", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Comedy\C03.png"),
            ("C04", "Gintama กินทามะ", "Comedy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Comedy\C04.png"),
            ("C05", "ก๊วนป่วนชวนบุ๋งบุ๋ง", "Comedy", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Comedy\C05.png"),
            # Sport
            ("S01", "ไฮคิว!! คู่ตบฟ้าประทาน", "Sport", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Sport\S01.png"),
            ("S02", "คุโรโกะ นายจืดพลิกสังเวียนบาส", "Sport", 115, 50, r"C:\Users\acer\Pictures\PJ\book\Sport\S02.png"),
            ("S03", "โอตาคุน่องเหล็ก", "Sport", 95, 50, r"C:\Users\acer\Pictures\PJ\book\Sport\S03.png"),
            ("S04", "ธนูดอกแรกแห่งการร้อยเรียง", "Sport", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Sport\S04.png"),
            ("S05", "ขังดวลแข้ง", "Sport", 125, 50, r"C:\Users\acer\Pictures\PJ\book\Sport\S05.png"),
        ]
        cursor.executemany('''
        INSERT INTO products (code, name, genre, price, quantity, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', products)
        conn.commit()
    conn.close()

initialize_database()

def initialize_database():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    # (ส่วนอื่นๆ ของ initialize_database)
    conn.close()

    # เพิ่มสินค้าใหม่เมื่อเริ่มต้นโปรแกรม
    add_new_product()
def initialize_slip_table():
    """
    สร้างตารางใน SQLite สำหรับเก็บสลิป
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS payment_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            slip BLOB NOT NULL,
            upload_time TEXT NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        )
    ''')
    conn.commit()
    conn.close()

# เรียกใช้ฟังก์ชันเพื่อสร้างตาราง
initialize_slip_table() 

# --------------------- Add New Product Function ---------------------
def add_new_product():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()

    # สินค้าที่จะเพิ่ม
    new_product = ("A06", "Demon Slayer ดาบพิฆาตอสูร", "Action", 95, 20, r"C:\Users\acer\Pictures\PJ\book\Action\A06.png")

    try:
        cursor.execute('''
            INSERT INTO products (code, name, genre, price, quantity, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', new_product)
        conn.commit()
        messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าสำเร็จ")
    except sqlite3.IntegrityError:
        messagebox.showerror("ข้อผิดพลาด", "รหัสสินค้าซ้ำหรือสินค้าเพิ่มไม่สำเร็จ")
    finally:
        conn.close()

    # โหลดข้อมูลสินค้าใหม่และรีเฟรชหน้าจอ
    load_book_data()
    refresh_category_frames()
    

# --------------------- Helper Functions ---------------------
def load_image(path, size):
    if not os.path.exists(path):
        # ถ้าไม่มีรูปภาพ ใช้รูป placeholder
        path = r'c:\Users\acer\Pictures\PJ\book\placeholder.png'  # เปลี่ยนเป็น path ของ placeholder
        if not os.path.exists(path):
            return None
    try:
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None

def set_background_image(frame, image_path, size=(1200, 800)):
    bg_image = load_image(image_path, size)
    if bg_image:
        bg_label = tk.Label(frame, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_image  # เก็บอ้างอิงรูปภาพ

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_centered_window(title, width, height, bg_color="#fff"):
    window = tk.Toplevel(root)
    window.title(title)
    center_window(window, width, height)
    window.configure(bg=bg_color)
    return window

def get_product_data():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute('SELECT code, name, genre, price, quantity, image_path FROM products')
    data = cursor.fetchall()
    conn.close()
    return data

def get_books_by_genre(genre):
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute('SELECT code, name, genre, price, quantity, image_path FROM products WHERE genre = ?', (genre,))
    data = cursor.fetchall()
    conn.close()
    books = {}
    for item in data:
        code, name, genre, price, quantity, image_path = item
        books[code] = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "image": image_path
        }
    return books

def get_genre_of_book(book_code):
    for genre, books in book_data.items():
        if book_code in books:
            return genre
    return None

def get_available_quantity(book_code):
    genre = get_genre_of_book(book_code)
    if genre and book_code in book_data[genre]:
        return book_data[genre][book_code]["quantity"]
    return 0

def calculate_total_quantity():
    return sum(cart.values())

def calculate_total_price():
    total = 0
    for code, quantity in cart.items():
        product = book_data[get_genre_of_book(code)][code]
        total += product["price"] * quantity
    return total

# --------------------- Price Formatting Function ---------------------
def format_price(price):
    """
    ฟังก์ชันช่วยเหลือในการฟอร์แมตราคาให้มีจุลภาคและจุดทศนิยมสองตำแหน่ง
    เช่น 1000 -> 1000.00 (คืนค่าเป็น float)
    """
    return float(price)

# --------------------- GUI Setup ---------------------
root = tk.Tk()
root.title("Mangaverse Book Shop")
root.geometry("1200x800")
center_window(root, 1200, 800)  # จัดให้อยู่ตรงกลางหน้าจอ
root.configure(bg="#e0f7ff")

main_frame = tk.Frame(root, bg="#e0f7ff")
main_frame.pack(fill="both", expand=True)

# --------------------- Global Variables ---------------------
cart = {}
quantity_vars = {}      # สำหรับ Entry widgets ในการแสดงสินค้า
cart_quantity_vars = {} # สำหรับ Cart window

# --------------------- Load Book Data ---------------------
def load_book_data():
    global book_data
    data = get_product_data()
    book_data = {}
    for item in data:
        code, name, genre, price, quantity, image_path = item
        if genre not in book_data:
            book_data[genre] = {}
        book_data[genre][code] = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "image": image_path
        }

load_book_data()

# --------------------- Function Definitions ---------------------
def show_frame(frame):
    for widget in main_frame.winfo_children():
        widget.pack_forget()
    frame.pack(fill="both", expand=True)

def display_all_categories():
    category_labels = [
        ("Action", 125, 380, "Wonderful Future", 25, "black", "white"),
        ("Drama", 411, 380, "Wonderful Future", 25, "black", "white"),
        ("Romance", 687, 380, "Wonderful Future", 25, "black", "white"),
        ("Horror", 980, 380, "Wonderful Future", 25, "black", "white"),
        ("Fantasy", 249, 640, "Wonderful Future", 25, "black", "white"),
        ("Comedy", 556, 640, "Wonderful Future", 25, "black", "white"),
        ("Sport", 875, 640, "Wonderful Future", 25, "black", "white")
    ]

    for genre, x, y, font_name, font_size, fg_color, bg_color in category_labels:
        label = tk.Label(
            category_frame, 
            text=genre, 
            font=(font_name, font_size), 
            fg=fg_color, 
            bg=bg_color, 
            cursor="hand2"
        )
        label.place(x=x, y=y)
        label.bind("<Button-1>", lambda e, g=genre: show_category(g))

def adjust_quantity(genre, book_code, change):
    available_quantity = get_available_quantity(book_code)
    current_in_cart = cart.get(book_code, 0)
    new_quantity = current_in_cart + change

    if new_quantity < 0:
        new_quantity = 0

    if new_quantity > available_quantity:
        messagebox.showwarning("แจ้งเตือน", "สินค้าหมดแล้วหรือจำนวนที่เลือกเกินสต๊อก")
        return

    if new_quantity > 0:
        cart[book_code] = new_quantity
    else:
        cart.pop(book_code, None)

    # Update quantity in Entry
    if book_code in quantity_vars:
        quantity_vars[book_code].set(str(new_quantity))

    # Update cart ถ้ามี Cart window เปิดอยู่
    if 'cart_window' in globals() and cart_window.winfo_exists():
        update_cart()

def adjust_cart_quantity(book_code, change):
    available_quantity = get_available_quantity(book_code)
    current_qty = cart.get(book_code, 0)
    new_qty = current_qty + change

    if new_qty < 0:
        new_qty = 0
    elif new_qty > available_quantity:
        new_qty = available_quantity
        messagebox.showwarning("Stock Limit", f"ไม่สามารถเพิ่ม '{book_data[get_genre_of_book(book_code)][book_code]['name']}' ได้มากกว่าจำนวนในสต๊อกที่มี ({available_quantity})")

    if new_qty != current_qty:
        if new_qty == 0:
            cart.pop(book_code, None)
        else:
            cart[book_code] = new_qty
        
        # Update the stock in the database
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE code = ?", (change, book_code))
        conn.commit()
        conn.close()

        if book_code in cart_quantity_vars:
            cart_quantity_vars[book_code].set(str(new_qty))
        update_cart()

def set_quantity(book_code):
    try:
        # ดึงค่าจาก Entry และแปลงเป็นจำนวนเต็ม
        new_quantity = int(quantity_vars[book_code].get())
        if new_quantity < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("แจ้งเตือน", "กรุณาใส่จำนวนสินค้าเป็นจำนวนเต็มที่ไม่ติดลบ")
        # รีเซ็ต Entry เป็นจำนวนในตะกร้า
        if book_code in cart:
            quantity_vars[book_code].set(str(cart.get(book_code, 0)))
        else:
            quantity_vars[book_code].set("0")
        return

    # ตรวจสอบว่าจำนวนใหม่เกินสต๊อกหรือไม่
    available_quantity = get_available_quantity(book_code)
    if new_quantity > available_quantity:
        messagebox.showwarning("แจ้งเตือน", f"จำนวนที่สั่งเกินสต๊อก! สต๊อกที่มีอยู่: {available_quantity}")
        if book_code in cart:
            quantity_vars[book_code].set(str(cart.get(book_code, 0)))
        else:
            quantity_vars[book_code].set("0")
        return

    # อัปเดตตะกร้า
    if new_quantity > 0:
        cart[book_code] = new_quantity
    else:
        cart.pop(book_code, None)

    # อัปเดตตะกร้า ถ้ามี Cart window เปิดอยู่
    if 'cart_window' in globals() and cart_window.winfo_exists():
        update_cart()

# --------------------- Category Pagination ---------------------
# ตัวแปรเก็บข้อมูลหมายเลขหน้าและจำนวนหน้าทั้งหมด
current_pages = {}  # เก็บหน้าปัจจุบันของแต่ละหมวดหมู่

def display_products(frame, products, genre_name, background_path, page=1, items_per_page=5):
    frame.pack_forget()
    frame.config(bg="#e0f7ff")
    set_background_image(frame, background_path, size=(1200, 800))  # ปรับขนาดให้ตรงกับหน้าต่างหลัก

    # ปุ่มกลับไปยังหมวดหมู่
    back_label = tk.Label(
        frame,
        text="◀ Back",
        font=("KhanoonThin", 16),
        bg="#062a69",
        fg="white",
        cursor="hand2"
    )
    back_label.place(x=120, y=147)
    back_label.bind("<Button-1>", lambda e: show_frame(category_frame))

    # คำนวณจำนวนหน้าทั้งหมด
    total_items = len(products)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # สร้างป้ายแสดงหมายเลขหน้าปัจจุบัน
    page_label = tk.Label(
        frame,
        text=f"{page}/{total_pages}",
        font=("KhanoonThin", 16),
        bg="#f3ffff",
        fg="black"
    )
    page_label.place(x=600, y=690)

    # ปุ่มแบ่งหน้า
    def go_to_previous_page():
        nonlocal page
        if page > 1:
            page -= 1
            current_pages[genre_name] = page
            refresh_display()
        else:
            messagebox.showinfo("แจ้งเตือน", "คุณอยู่หน้าแรกแล้ว(ﾉ´ヮ`)ﾉ")

    def go_to_next_page():
        nonlocal page
        if page < total_pages:
            page += 1
            current_pages[genre_name] = page
            refresh_display()
        else:
            messagebox.showinfo("แจ้งเตือน", "ยังไม่มีหน้าถัดไป(｡•́︿•̀｡)")

    def refresh_display():
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget != back_label and widget != page_label:
                widget.destroy()
        display_current_page()  # แสดงสินค้าหน้าปัจจุบันใหม่
        page_label.config(text=f"{page}/{total_pages}")  # อัปเดตเลขหน้าที่แสดง

    def display_current_page():
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        current_products = list(products.items())[start_index:end_index]

        x_position = 75
        y_position = 250
        count = 0
        for code, product in current_products:
            remaining_quantity = product['quantity'] - cart.get(code, 0)
            card_frame = tk.Frame(frame, bg="#e0f7ff", width=200, height=400, highlightbackground="#cccccc", highlightthickness=1)
            card_frame.place(x=x_position, y=y_position)

            # โหลดรูปหนังสือ
            book_image = load_image(product["image"], (150, 200))
            if book_image:
                image_label = tk.Label(card_frame, image=book_image, bg="#e0f7ff")
                image_label.image = book_image
                image_label.pack(pady=5)
                # ผูกเหตุการณ์คลิกที่รูปภาพเพื่อดูรายละเอียด
                image_label.bind("<Button-1>", lambda e, g=genre_name, c=code: show_product_details(g, c)) # type: ignore

            # แสดงชื่อหนังสือและรหัส
            title_label = tk.Label(card_frame, text=product["name"], font=("KhanoonThin", 12, "bold"), bg="#e0f7ff", wraplength=180, cursor="hand2")
            title_label.pack()
            title_label.bind("<Button-1>", lambda e, g=genre_name, c=code: show_product_details(g, c)) # type: ignore

            code_label = tk.Label(card_frame, text=f"รหัส: {code}", font=("KhanoonThin", 11), bg="#e0f7ff")
            code_label.pack()

            # แสดงสต็อกที่เหลือ
            if remaining_quantity > 0:
                stock_label = tk.Label(card_frame, text=f"เหลือ: {remaining_quantity} เล่ม", font=("KhanoonThin", 11), bg="#e0f7ff")
                stock_label.pack()
            else:
                stock_label = tk.Label(card_frame, text="สินค้าหมดแล้ว", font=("KhanoonThin", 11), bg="#e0f7ff", fg="red")
                stock_label.pack()

            # ราคาหนังสือ
            price_label = tk.Label(card_frame, text=f"ราคา {format_price(product['price'])}", font=("KhanoonThin", 10), bg="#e0f7ff")
            price_label.pack()

            # เฟรมควบคุมจำนวนสินค้า
            quantity_frame = tk.Frame(card_frame, bg="#e0f7ff")
            quantity_frame.pack(pady=5)

            # ปุ่มลบจำนวน
            minus_button = tk.Button(
                quantity_frame,
                text="-",
                font=("KhanoonThin", 10),
                width=2,
                command=lambda book_code=code: adjust_quantity(genre_name, book_code, -1)
            )
            minus_button.grid(row=0, column=0)

            # Entry สำหรับจำนวนสินค้า
            quantity_var = tk.StringVar(value=str(cart.get(code, 0)))
            quantity_entry = tk.Entry(quantity_frame, textvariable=quantity_var, font=("KhanoonThin", 10), width=3, justify='center')
            quantity_entry.grid(row=0, column=1)
            quantity_vars[code] = quantity_var

            # ผูกการกด Enter เพื่ออัปเดตจำนวน
            quantity_entry.bind("<Return>", lambda e, book_code=code: set_quantity(book_code))

            # ปุ่มเพิ่มจำนวน
            plus_button = tk.Button(
                quantity_frame,
                text="+",
                font=("KhanoonThin", 10),
                width=2,
                command=lambda book_code=code: adjust_quantity(genre_name, book_code, 1)
            )
            plus_button.grid(row=0, column=2)

            # ปิดการใช้งานปุ่มเพิ่มและ Entry ถ้าสินค้าหมด
            if remaining_quantity <= 0:
                plus_button.config(state='disabled')
                quantity_entry.config(state='disabled')

            # ปรับตำแหน่งสำหรับสินค้าถัดไป
            count += 1
            if count % 5 == 0:
                x_position = 75
                y_position += 400
            else:
                x_position += 220

    # แสดงสินค้าหน้าปัจจุบัน
    display_current_page()

    # ปุ่มลูกศรซ้าย (ย้อนกลับ)
    left_arrow = tk.Button(frame, text="◀", font=("Arial", 18), command=go_to_previous_page, bg="#e0f7ff", cursor="hand2")
    left_arrow.place(x=550, y=690)

    # ปุ่มลูกศรขวา (ถัดไป)
    right_arrow = tk.Button(frame, text="▶", font=("Arial", 18), command=go_to_next_page, bg="#e0f7ff", cursor="hand2")
    right_arrow.place(x=650, y=690)
    
def show_category(genre):
    frame = frames[genre]
    products = book_data[genre]
    background_path = category_backgrounds.get(genre, r'c:\Users\acer\Pictures\PJ\book\placeholder.png')  # ใช้ placeholder ถ้าไม่มี background
    display_products(frame, products, genre, background_path)
    show_frame(frame)
    

# --------------------- Cart and Order Frames ---------------------

def confirm_order():
    if not cart:
        messagebox.showinfo("Empty Cart", "ตะกร้าสินค้าไม่มีรายการ")
        return

    # ตรวจสอบสต็อกก่อนสั่งซื้อ
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    for code, qty in cart.items():
        cursor.execute("SELECT quantity FROM products WHERE code = ?", (code,))
        result = cursor.fetchone()
        if result:
            available_quantity = result[0]
            if qty > available_quantity:
                messagebox.showwarning("แจ้งเตือน", f"สินค้าหมดหรือจำนวนที่สั่งเกิน: {code}")
                conn.close()
                return
        else:
            messagebox.showwarning("แจ้งเตือน", f"ไม่พบสินค้ารหัส: {code}")
            conn.close()
            return

    # ลดสต็อกในฐานข้อมูล
    for code, qty in cart.items():
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE code = ?", (qty, code))
    conn.commit()
    conn.close()

    # เตรียมข้อมูลสำหรับใบเสร็จ
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pickup_method = "จัดส่ง"  # หรือ "รับที่ร้าน" ขึ้นอยู่กับการเลือกรับสินค้า
    items = []
    total_price = 0
    total_quantity = 0
    for code, qty in cart.items():
        product = book_data[get_genre_of_book(code)][code]
        item_total = product["price"] * qty
        items.append({
            "code": code,
            "name": product["name"],
            "quantity": qty,
            "price": format_price(item_total)
        })
        total_price += item_total
        total_quantity += qty

    discount = 0
    if total_quantity >= 4:
        discount = int(total_price * 0.10)
        total_price -= discount

    # สร้างข้อมูล order_details
    order_details = {
        "username": current_user,
        "order_time": order_time,
        "items": items,
        "discount": format_price(discount),
        "total_price": format_price(total_price)
    }

    # เก็บข้อมูลใบเสร็จล่าสุด
    root.last_order_details = order_details

    # แสดงใบเสร็จ
    show_receipt(order_details)

    # เคลียร์ตะกร้า
    cart.clear()
    update_cart()

def update_quantity_sold(cart_items):
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    
    for item in cart_items:
        product_code = item['code']  # สมมติว่า cart_items เป็นลิสต์ของดิกต์ที่มี 'code' และ 'quantity'
        quantity_to_sell = item['quantity']
        
        # ดึงข้อมูลจำนวนที่ขายจากตาราง new_products
        cursor.execute("SELECT quantity_sold FROM new_products WHERE code = ?", (product_code,))
        result = cursor.fetchone()
        
        if result:
            current_quantity_sold = result[0]
            # อัปเดตจำนวนที่ขาย
            new_quantity_sold = current_quantity_sold + quantity_to_sell
            cursor.execute("UPDATE new_products SET quantity_sold = ? WHERE code = ?", (new_quantity_sold, product_code))
        
        conn.commit()

    conn.close()


def proceed_to_order():
    if not cart:
        messagebox.showinfo("Empty Cart", "ตะกร้าสินค้าไม่มีรายการ")
        return
    confirm_order()
def open_receipt_icon():
    # ตรวจสอบว่ามีใบเสร็จที่สั่งซื้อแล้วหรือยัง
    if hasattr(root, 'last_order_details'):
        show_receipt(root.last_order_details)
    else:
        messagebox.showinfo("ใบเสร็จ", "ยังไม่มีการสั่งซื้อ")

    # อัปเดตเฟรมตะกร้า ถ้ามี Cart window เปิดอยู่
    if 'cart_window' in globals() and cart_window.winfo_exists():
        update_cart()

    # รีเฟรชเฟรมหมวดหมู่เพื่ออัปเดตสต๊อก
    refresh_category_frames()

    # แสดงรายละเอียดการสั่งซื้อ
    show_order_frame(order_cart) # type: ignore

def format_price(price):
    # Format price as a string with 2 decimal points
    return "{:.2f}".format(price)

def finalize_order(pickup_method, delivery_method):
    # You can add the functionality here to finalize the order based on the selected method
    print(f"Pickup method: {pickup_method}, Delivery method: {delivery_method}")
    # Optionally, save or update order status in the database here

def show_order_frame(order_cart):
    # Clear the previous widgets in the order_frame
    for widget in order_frame.winfo_children():
        widget.destroy()

    # Connect to the SQLite database
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()

    # Calculate total price and quantity
    total_price = 0
    total_quantity = sum(order_cart.values())

    # Insert order details into orders table
    cursor.execute('''
        INSERT INTO orders (total_price, total_quantity, order_time)
        VALUES (?, ?, ?)
    ''', (total_price, total_quantity, 'current_time'))  # Use current time or dynamic time
    conn.commit()


    # สร้างเฟรมภายในพร้อมแถบเลื่อน
    inner_frame = tk.Frame(order_frame, bg="#e0f7ff")
    inner_frame.pack(pady=50, padx=100, fill="both", expand=True)

    canvas = tk.Canvas(inner_frame, bg="#e0f7ff", width=800, height=600, highlightthickness=0)
    scrollbar = tk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#e0f7ff")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ชื่อหัวข้อรายการสั่งซื้อ
    order_title = tk.Label(scrollable_frame, text="รายการสั่งซื้อ", font=("KhanoonThin", 20, "bold"), bg="#e0f7ff")
    order_title.pack(pady=10)

    # เพิ่มปุ่ม Back ในหน้าต่าง Order
    back_button = tk.Button(
        scrollable_frame,
        text="Back",
        font=("Wonderful Future", 12),
        bg="#fd5c70",
        fg="white",
        command=lambda: order_frame.pack_forget(),
        cursor="hand2"
    )
    back_button.pack(pady=5, anchor='ne')  # วางปุ่มที่มุมขวาบน

    total_price = 0
    total_quantity = sum(order_cart.values())

    for code, quantity in order_cart.items():
        if quantity > 0:
            product = book_data[get_genre_of_book(code)][code]
            item_total = product["price"] * quantity
            total_price += item_total

            item_frame = tk.Frame(scrollable_frame, bg="#e0f7ff", highlightbackground="#cccccc", highlightthickness=1)
            item_frame.pack(pady=5, padx=10, fill="x")

            # โหลดและแสดงรูปภาพสินค้า
            book_image = load_image(product['image'], (80,80))
            if book_image:
                image_label = tk.Label(item_frame, image=book_image, bg="#e0f7ff")
                image_label.image = book_image  # เก็บอ้างอิงรูปภาพ
                image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)

            # ชื่อสินค้า
            name_label = tk.Label(item_frame, text=product['name'], font=("KhanoonThin", 12, "bold"), bg="#e0f7ff", anchor="w")
            name_label.grid(row=0, column=1, sticky="w")

            # รหัสสินค้า
            code_label = tk.Label(item_frame, text=f"รหัส: {code}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="w")
            code_label.grid(row=1, column=1, sticky="w")

            # จำนวนสินค้า
            qty_label = tk.Label(item_frame, text=f"จำนวน: {quantity}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="w")
            qty_label.grid(row=0, column=2, sticky="e")

            # ราคา
            price_total = product["price"] * quantity
            price_label = tk.Label(item_frame, text=f"ราคา: {format_price(price_total)}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="e")
            price_label.grid(row=1, column=2, sticky="e")

    # คำนวณส่วนลด 10% หากซื้อครบ 4 เล่มขึ้นไป
    discount = 0
    if total_quantity >= 4:
        discount = total_price * 0.10
        discounted_price = total_price - discount
        discount_label = tk.Label(scrollable_frame, text=f"ส่วนลด 10%: -{format_price(int(discount))}", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff", fg="green")
        discount_label.pack(pady=5)
        total_price = discounted_price

    # แสดงราคารวมทั้งหมด
    total_label = tk.Label(scrollable_frame, text=f"รวมทั้งหมด: {format_price(int(total_price))}", font=("KhanoonThin", 16, "bold"), bg="#e0f7ff")
    total_label.pack(pady=10)

    # ตัวเลือกการสั่งซื้อ
    order_options = tk.Frame(scrollable_frame, bg="#e0f7ff")
    order_options.pack(pady=10)

    pickup_var = tk.IntVar()
    delivery_var = tk.IntVar()

    pickup_radio = tk.Radiobutton(order_options, text="รับสินค้าที่ร้าน", variable=pickup_var, value=1, bg="#e0f7ff")
    pickup_radio.grid(row=0, column=0, padx=10, pady=5)

    delivery_radio = tk.Radiobutton(order_options, text="จัดส่งตามที่อยู่", variable=delivery_var, value=2, bg="#e0f7ff")
    delivery_radio.grid(row=0, column=1, padx=10, pady=5)

    confirm_button = ctk.CTkButton(
        scrollable_frame,
        text="ยืนยันการสั่งซื้อ",
        font=("KhanoonThin", 14),
        fg_color="#004aad",
        text_color="white",
        command=lambda: finalize_order(pickup_var.get(), delivery_var.get())
    )
    confirm_button.pack(pady=10)

    # รีเฟรช scrollbar
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def refresh_category_frames():
    for genre, frame in frames.items():
        frame.destroy()  # ทำลายเฟรมเดิม
        frames[genre] = tk.Frame(main_frame, bg="#e0f7ff")  # สร้างเฟรมใหม่
        books = get_books_by_genre(genre)
        background = category_backgrounds.get(genre, r'c:\Users\acer\Pictures\PJ\book\placeholder.png')
        display_products(frames[genre], books, genre, background)  # แสดงสินค้าใหม่

def save_order_to_database(pickup_method):
    """
    บันทึกคำสั่งซื้อและวิธีการรับสินค้าไปยังฐานข้อมูล
    """
    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()

        if not cart:
            messagebox.showwarning("แจ้งเตือน", "ตะกร้าสินค้าไม่มีรายการ")
            return None, None  # ✅ แก้ไขให้ return ค่าเป็นคู่ (None, None)

        if not current_user:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถสั่งซื้อได้ เนื่องจากไม่ได้ล็อกอิน")
            return None, None  # ✅ แก้ไขให้ return ค่าเป็นคู่ (None, None)

        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = sum(book_data[get_genre_of_book(code)][code]["price"] * qty for code, qty in cart.items())
        discount = total_price * 0.10 if sum(cart.values()) >= 4 else 0
        total_price -= discount

        delivery_address = "ไม่มี"
        if pickup_method == "จัดส่งตามที่อยู่":
            cursor.execute("SELECT house_number, subdistrict, district, province, postal_code FROM user_address_new WHERE username = ? ORDER BY id DESC LIMIT 1",
                           (current_user,))
            address_result = cursor.fetchone()
            if not address_result:
                messagebox.showwarning("แจ้งเตือน", "กรุณากรอกที่อยู่ก่อนสั่งซื้อ")
                ask_delivery_details()
                return None, None  # ✅ แก้ไขให้ return ค่าเป็นคู่ (None, None)
            delivery_address = f"{address_result[0]}, {address_result[1]}, {address_result[2]}, {address_result[3]}, {address_result[4]}"

        # บันทึกคำสั่งซื้อในตาราง orders
        cursor.execute("INSERT INTO orders (username, order_time, pickup_method, delivery_address, total_price, discount) VALUES (?, ?, ?, ?, ?, ?)",
                       (current_user, order_time, pickup_method, delivery_address, total_price, discount))
        order_id = cursor.lastrowid  # ใช้ lastrowid เพื่อดึง order_id ของคำสั่งซื้อที่เพิ่มใหม่

        # ดึง username จาก order_id ล่าสุด
        cursor.execute("SELECT username FROM orders WHERE order_id = ?", (order_id,))
        order_user = cursor.fetchone()

        if order_user:
            username = order_user[0]
        else:
            username = None  # หากไม่พบ username

        # บันทึกรายการสินค้าทุกตัวในตะกร้าลงในตาราง order_items
        for book_code, qty in cart.items():
            cursor.execute('''
                INSERT INTO order_item1 (order_id, book_code, quantity, username)
                VALUES (?, ?, ?, ?)
            ''', (order_id, book_code, qty, username))

        conn.commit()  # บันทึกข้อมูลทั้งหมดในฐานข้อมูล
        conn.close()

        # คืนค่า order_id หลังจากบันทึกคำสั่งซื้อเสร็จสิ้น
        return order_id, total_price

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None, None

    except Exception as e:
        messagebox.showerror("Unexpected Error", f"เกิดข้อผิดพลาด: {e}")
        return None, None  # ✅ return None ถ้า error

def finalize_order(pickup, delivery):
    """
    ยืนยันคำสั่งซื้อ และบันทึกวิธีการรับสินค้า
    """
    if pickup and delivery:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกวิธีการสั่งซื้อเพียงอย่างใดอย่างหนึ่ง")
        return
    if not pickup and not delivery:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกวิธีการสั่งซื้อ")
        return

    pickup_method = "รับสินค้าที่ร้าน" if pickup else "จัดส่งตามที่อยู่"

    # บันทึกคำสั่งซื้อและดึง order_id + total_price
    order_id, total_price = save_order_to_database(pickup_method)

    if order_id:
        
        # แสดง QR Code
        show_qr_code(order_id, pickup_method, total_price)
        
        # สร้างข้อมูลใบเสร็จ
        order_details = {
            "username": current_user,
            "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{"name": book_data[get_genre_of_book(code)][code]["name"], "quantity": qty, "price": format_price(book_data[get_genre_of_book(code)][code]["price"] * qty)} for code, qty in cart.items()],
            "discount": format_price(total_price * 0.10) if sum(cart.values()) >= 4 else "0.00 บาท",
            "total_price": format_price(total_price - (total_price * 0.10)) if sum(cart.values()) >= 4 else format_price(total_price)
        }
        
        # แสดงใบเสร็จ
        show_receipt(order_details)
        
def initialize_slip_table():
    """
    สร้างตารางใน SQLite สำหรับเก็บสลิป
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            slip BLOB NOT NULL,
            upload_time TEXT NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        )
    ''')
    conn.commit()
    conn.close()

# เรียกใช้ฟังก์ชันเพื่อสร้างตาราง
initialize_slip_table() 
              
def show_qr_code(order_id, pickup_method, total_price):
    """
    แสดง QR Code และให้ผู้ใช้ทำการอัปโหลดสลิป
    """
    qr_window = tk.Toplevel(root)
    qr_window.title("QR Code")
    center_window(qr_window, 900, 650)
    qr_window.configure(bg="#e0f7ff")
    
    # นำ qr_window ขึ้นมาอยู่ด้านหน้า
    qr_window.lift()
    # เช็คว่าเป็นรับที่ร้านหรือจัดส่ง
    
    # กำหนด Path รูป QR Code
    qr_image_path = r"C:\Users\acer\Pictures\PJ\scan.png"  # เปลี่ยน Path ให้ตรงกับรูปจริง
    qr_image = load_image(qr_image_path, (900, 590))

    # สร้าง Canvas และแสดงรูป QR Code
    canvas = tk.Canvas(qr_window, width=900, height=590, bg="#e0f7ff", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    if qr_image:
        canvas.create_image(0, 0, anchor="nw", image=qr_image)
        canvas.image = qr_image

    slip_uploaded = tk.BooleanVar(value=False)

    total_price_label = tk.Label(qr_window, text=f"ยอดที่ต้องจ่าย: {total_price:,.2f} บาท",
                                 font=("KhanoonThin", 16, "bold"), bg="#e0f7ff", fg="black")
    total_price_label.place(x=225, y=523, anchor="center")

    def upload_slip():
        file_path = filedialog.askopenfilename(
            title="อัปโหลดสลิป",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            try:
                # เปิดไฟล์สลิปและอ่านข้อมูลเป็น binary
                with open(file_path, "rb") as file:
                    slip_data = file.read()
                
                # เชื่อมต่อฐานข้อมูล
                conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
                cursor = conn.cursor()
                
                # ดึง order_id ล่าสุดจากตาราง orders
                cursor.execute('''
                    SELECT order_id FROM orders
                    ORDER BY order_id DESC
                    LIMIT 1
                ''')
                latest_order = cursor.fetchone()
                
                if latest_order:
                    order_id = latest_order[0]
                    
                    # บันทึกข้อมูลสลิปลงในฐานข้อมูล
                    cursor.execute('''
                        INSERT INTO payment_slips (order_id, slip, upload_time)
                        VALUES (?, ?, ?)
                    ''', (order_id, slip_data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                
                # ดึง order_id ที่เพิ่มขึ้นใหม่
                    order_id = cursor.lastrowid

                # สร้างหน้าต่างแจ้งเตือนยืนยัน
                confirm_window = tk.Toplevel(qr_window)
                confirm_window.title("ยืนยันการอัปโหลด")
                confirm_window.geometry("300x150")
                confirm_window.configure(bg="#e0f7ff")
                confirm_window.grab_set()  # ทำให้หน้าต่างเป็น modal

                # ทำให้หน้าต่างแจ้งเตือนอยู่ตรงกลางหน้าต่าง QR Code
                confirm_window.transient(qr_window)
                qr_window.update_idletasks()  # อัปเดตหน้าต่าง QR Code เพื่อคำนวณตำแหน่ง
                x = qr_window.winfo_x() + (qr_window.winfo_width() // 2) - (300 // 2)
                y = qr_window.winfo_y() + (qr_window.winfo_height() // 2) - (150 // 2)
                confirm_window.geometry(f"+{x}+{y}")

                # ข้อความแจ้งเตือน
                tk.Label(
                    confirm_window,
                    text="คุณต้องการอัปโหลดสลิปนี้ใช่หรือไม่?",
                    font=("KhanoonThin", 12),
                    bg="#e0f7ff"
                ).pack(pady=20)

                # ฟังก์ชันยืนยันการอัปโหลด
                def confirm_upload():
                    upload_status_label.config(text="อัปโหลดสลิปแล้ว ✅", fg="green")
                    pay_button.configure(state="normal")  # ปลดล็อกปุ่มยืนยันการชำระเงิน
                    slip_uploaded.set(True)
                    confirm_window.destroy()  # ปิดหน้าต่างยืนยัน

                # ฟังก์ชันยกเลิกการอัปโหลด
                def cancel_upload():
                    upload_status_label.config(text="ยกเลิกการอัปโหลด", fg="red")
                    pay_button.configure(state="disabled")
                    slip_uploaded.set(False)
                    confirm_window.destroy()  # ปิดหน้าต่างยืนยัน

                # ปุ่มยืนยัน
                tk.Button(
                    confirm_window,
                    text="ใช่",
                    font=("KhanoonThin", 12),
                    bg="#4CAF50",
                    fg="white",
                    command=confirm_upload
                ).pack(side="left", padx=20, pady=10)

                # ปุ่มยกเลิก
                tk.Button(
                    confirm_window,
                    text="ไม่ใช่",
                    font=("KhanoonThin", 12),
                    bg="#f44336",
                    fg="white",
                    command=cancel_upload
                ).pack(side="right", padx=20, pady=10)

            except Exception as e:
                upload_status_label.config(text="การอัปโหลดล้มเหลว", fg="red")
                print(f"Error uploading file: {e}")
        else:
            upload_status_label.config(text="ยังไม่ได้อัปโหลดสลิป", fg="red")

    # ป้ายสถานะการอัปโหลดและปุ่มอัปโหลดสลิป
    upload_status_label = tk.Label(
        qr_window,
        text="ยังไม่ได้อัปโหลดสลิป",
        font=("KhanoonThin", 10),
        bg="#e0f7ff",
        fg="red",
        anchor="center",
        wraplength=300
    )
    upload_status_label.place(x=200, y=400, width=200, height=50)

    upload_button = ctk.CTkButton(
        qr_window,
        text="อัปโหลดสลิป",
        font=("KhanoonThin", 17),
        fg_color="blue",
        hover_color="light blue",
        width=100,
        height=40,
        command=upload_slip  # ฟังก์ชันสำหรับอัปโหลดไฟล์
    )
    upload_button.place(x=420, y=400)

    # ปุ่มชำระเงิน
    pay_button = ctk.CTkButton(
        qr_window,
        text="ยืนยันการชำระเงิน",
        font=("KhanoonThin", 17),
        fg_color="green",
        hover_color="light green",
        width=130,
        height=40,
        state="disabled",  # ปิดใช้งานเริ่มต้น
        command=lambda: confirm_payment(qr_window)
    )
    pay_button.place(x=300, y=530)  # วางทางซ้าย

    # ปุ่มยกเลิก
    cancel_button = ctk.CTkButton(
        qr_window,
        text="ยกเลิก",
        font=("KhanoonThin", 17),
        fg_color="red",
        hover_color="light coral",
        width=80,
        height=40,
        command=lambda: [qr_window.destroy(), open_order_window()]
    )
    cancel_button.place(x=500, y=530)  # วางทางขวา

    # จัดวางปุ่มและป้ายสถานะ
    canvas.create_window(650, 435, anchor='center', window=upload_button)
    canvas.create_window(510, 435, anchor='center', window=upload_status_label)
    canvas.create_window(510, 500, anchor='center', window=pay_button)
    canvas.create_window(650, 500, anchor='center', window=cancel_button)
    
def finalize_order(pickup, delivery):
    """
    ยืนยันคำสั่งซื้อ และบันทึกวิธีการรับสินค้า
    """
    if pickup and delivery:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกวิธีการสั่งซื้อเพียงอย่างใดอย่างหนึ่ง")
        return
    if not pickup and not delivery:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกวิธีการสั่งซื้อ")
        return

    pickup_method = "รับสินค้าที่ร้าน" if pickup else "จัดส่งตามที่อยู่"

    # ✅ บันทึกคำสั่งซื้อและดึง order_id + total_price
    order_id, total_price = save_order_to_database(pickup_method)

    if order_id:
        # ✅ เพิ่ม `total_price` ตอนเรียก show_qr_code
        show_qr_code(order_id, pickup_method, total_price)
    
def save_order(self, total_price, discount, pickup_method, cart_items):
    """
    บันทึกคำสั่งซื้อไปยังฐานข้อมูล
    - total_price (float) : ราคาสุทธิของคำสั่งซื้อ
    - discount (float) : ส่วนลดที่ได้รับ
    - pickup_method (str) : วิธีรับสินค้า (เช่น 'Delivery' หรือ 'Pick-up')
    - cart_items (dict) : รายการสินค้าที่อยู่ในตะกร้า (รหัสสินค้า -> จำนวนสินค้า)
    """

    global current_user  # ใช้ชื่อผู้ใช้ที่ล็อกอินจากตัวแปร global

    if not current_user:
        messagebox.showerror("Error", "ไม่พบข้อมูลผู้ใช้ที่ล็อกอิน")
        return

    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()

        # 🔹 เก็บเวลาการสั่งซื้อ
        order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 🔹 บันทึกลงตาราง `orders`
        cursor.execute("""
            INSERT INTO orders (username, order_time, pickup_method, total_price, discount)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user, order_time, pickup_method, total_price, discount))

        # 🔹 ดึง `order_id` ล่าสุดที่ถูกเพิ่ม
        order_id = cursor.lastrowid  # ✅ สำคัญ! ดึง `order_id` ของออเดอร์ที่เพิ่งเพิ่ม

        # 🔹 บันทึกสินค้าแต่ละรายการลง `order_items`
        for product_code, quantity in cart_items.items():
            cursor.execute("SELECT price FROM products WHERE code = ?", (product_code,))
            result = cursor.fetchone()

            if result:
                unit_price = result[0]
                total_price = unit_price * quantity  # คำนวณราคารวมของสินค้าแต่ละชิ้น

                cursor.execute("""
                    INSERT INTO order_items (order_id, product_code, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, product_code, quantity, total_price))

        # 🔹 บันทึกข้อมูลลงฐานข้อมูล
        conn.commit()
        conn.close()

        # ✅ แจ้งเตือนเมื่อบันทึกสำเร็จ
        messagebox.showinfo("Success", f"คำสั่งซื้อ {order_id} ถูกบันทึกเรียบร้อยแล้ว!")

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"เกิดข้อผิดพลาดในการบันทึกคำสั่งซื้อ: {e}")

    
def update_stock_after_order():
    """
    ฟังก์ชันสำหรับการอัปเดตสต๊อกสินค้าหลังจากการสั่งซื้อ และเก็บข้อมูลการลดจำนวนสินค้าที่ถูกสั่งซื้อ
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()

    for code, qty in cart.items():
        if qty > 0:
            # ดึงจำนวนสินค้าที่มีอยู่ในฐานข้อมูล
            cursor.execute("SELECT quantity FROM products WHERE code = ?", (code,))
            result = cursor.fetchone()
            
            if result:
                available_quantity = result[0]
                new_quantity = available_quantity - qty
                
                # คำนวณการลดจำนวนสินค้าและบันทึกลงในฐานข้อมูล
                cursor.execute(
                    "UPDATE products SET quantity = ?, quantity_removed = quantity_removed + ? WHERE code = ?",
                    (new_quantity, qty, code)
                )

    conn.commit()
    conn.close()

def confirm_payment(qr_window):
    messagebox.showinfo("ยืนยันการชำระเงิน", "การชำระเงินสำเร็จ ขอบคุณสำหรับการอุดหนุน!")
    qr_window.destroy()  # ปิดหน้าต่าง QR code
    
    # อัปเดตสต๊อก
    update_stock_after_order()

    # สร้างข้อมูลใบเสร็จ
    order_details = {
        "username": current_user,
        "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": [],
        "discount": 0.00,  # เปลี่ยนจาก "0.00 บาท" เป็น 0.00
        "total_price": 0.00  # เปลี่ยนจาก "0.00 บาท" เป็น 0.00
    }

    # เพิ่มรายการสินค้าในใบเสร็จ
    for code, quantity in cart.items():
        if quantity > 0:
            product = book_data[get_genre_of_book(code)][code]
            item_total = product["price"] * quantity
            order_details["items"].append({
                "name": product["name"],
                "quantity": quantity,
                "price": item_total  # ไม่ต้องใช้ format_price ที่นี่
            })

    # คำนวณส่วนลดและราคาสุทธิ
    total_quantity = sum(cart.values())
    total_price = sum(item["price"] for item in order_details["items"])
    if total_quantity >= 4:
        discount = total_price * 0.10
        order_details["discount"] = discount
        order_details["total_price"] = total_price - discount
    else:
        order_details["total_price"] = total_price

    # แสดงใบเสร็จ
    show_receipt(order_details)
    
def show_receipt(order_details):
    # แปลงราคาและส่วนลดเป็นสตริงที่มีหน่วย "บาท"
    order_details["discount"] = f"{float(order_details['discount']):,.2f} บาท"
    order_details["total_price"] = f"{float(order_details['total_price']):,.2f} บาท"

    receipt_window = tk.Toplevel(root)
    receipt_window.title("Receipt")
    center_window(receipt_window, 800, 600)
    receipt_window.configure(bg="#e0f7ff")

    # สร้าง Frame หลักสำหรับใส่ Scrollbar
    main_frame = tk.Frame(receipt_window, bg="#e0f7ff")
    main_frame.pack(fill="both", expand=True)

    # สร้าง Canvas สำหรับ Scrollbar
    canvas = tk.Canvas(main_frame, bg="#e0f7ff", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#e0f7ff")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # โลโก้ร้าน
    logo_path = r"C:\Users\acer\Pictures\Mangaverse\logo.png"  # เปลี่ยน Path ให้ตรงกับไฟล์โลโก้ของคุณ
    logo_image = load_image(logo_path, (150, 150))
    if logo_image:
        logo_label = tk.Label(scrollable_frame, image=logo_image, bg="#e0f7ff")
        logo_label.image = logo_image  # เก็บอ้างอิงรูปภาพ
        logo_label.pack(pady=(10, 5))

    # ดึงข้อมูลผู้ใช้จากฐานข้อมูล
    full_name = ""
    order_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # เวลาที่สั่งซื้อ
    Emaill_y = ""
    Phone_Number = ""

    try:
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()
        cursor.execute("SELECT fname, lname, email, phonenum FROM mangauser WHERE username = ?", (current_user,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            full_name = f"ชื่อ-นามสกุล: {user_data[0]} {user_data[1]}"
            Emaill_y = f"อีเมล: {user_data[2]}"
            Phone_Number = f"เบอร์โทร: {user_data[3]}"
        else:
            full_name = "ชื่อ-นามสกุล: ไม่มีข้อมูล"
            Emaill_y = "อีเมล: ไม่มีข้อมูล"
            Phone_Number = "เบอร์โทร: ไม่มีข้อมูล"
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"เกิดข้อผิดพลาดกับฐานข้อมูล: {e}")

    order_time_label = tk.Label(scrollable_frame, text=f"เวลาที่สั่งซื้อ: {order_time}", font=("KhanoonThin", 14), bg="#e0f7ff")
    order_time_label.pack(pady=(5, 10))

    user_label = tk.Label(scrollable_frame, text=current_user, font=("KhanoonThin", 14), bg="#e0f7ff")
    user_label.pack()

    full_name_label = tk.Label(scrollable_frame, text=full_name, font=("KhanoonThin", 14), bg="#e0f7ff")
    full_name_label.pack()

    email_label = tk.Label(scrollable_frame, text=Emaill_y, font=("KhanoonThin", 14), bg="#e0f7ff")
    email_label.pack()

    phonenum_label = tk.Label(scrollable_frame, text=Phone_Number, font=("KhanoonThin", 14), bg="#e0f7ff")
    phonenum_label.pack()

    # รายการสินค้า
    items_title_label = tk.Label(scrollable_frame, text="รายการสินค้า", font=("KhanoonThin", 16, "bold"), bg="#e0f7ff")
    items_title_label.pack()

    total_price = 0
    total_quantity = 0
    discount = 0

    for item in order_details["items"]:
        item_frame = tk.Frame(scrollable_frame, bg="#e0f7ff", highlightbackground="#cccccc", highlightthickness=1)
        item_frame.pack(pady=5, padx=10, fill="x")

        # แสดงชื่อสินค้า
        name_label = tk.Label(item_frame, text=item['name'], font=("KhanoonThin", 12), bg="#e0f7ff")
        name_label.grid(row=0, column=0, sticky="w")

        # แสดงจำนวน
        qty_label = tk.Label(item_frame, text=f"จำนวน: {item['quantity']}", font=("KhanoonThin", 12), bg="#e0f7ff")
        qty_label.grid(row=0, column=1, sticky="w")

        # แสดงราคา
        price_label = tk.Label(item_frame, text=f"ราคา: {float(item['price']):,.2f} บาท", font=("KhanoonThin", 12), bg="#e0f7ff")
        price_label.grid(row=0, column=2, sticky="e")

        # คำนวณราคารวม
        total_price += float(item['price'])
        total_quantity += item['quantity']

    # ราคาทั้งหมด
    total_price_label = tk.Label(scrollable_frame, text=f"ราคาทั้งหมด: {total_price:,.2f} บาท", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff")
    total_price_label.pack()

    if total_quantity >= 4:
        discount = total_price * 0.10
        discounted_price = total_price - discount
        discount_label = tk.Label(scrollable_frame, text=f"ส่วนลด 10%: -{discount:,.2f} บาท", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff", fg="green")
        discount_label.pack()
        total_price = discounted_price

    net_price_label = tk.Label(scrollable_frame, text=f"ราคาสุทธิ: {total_price:,.2f} บาท", font=("KhanoonThin", 16, "bold"), bg="#e0f7ff")
    net_price_label.pack(pady=15)

    thank_you_label = tk.Label(scrollable_frame, text="ขอบคุณที่อุดหนุนร้าน Mangaverse Book Shop", font=("KhanoonThin", 14), bg="#e0f7ff")
    thank_you_label.pack(pady=10)

    # ปุ่มดาวน์โหลดใบเสร็จ PDF
    def download_pdf():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="receipt.pdf"
        )
        if file_path:
            generate_pdf_receipt(order_details, file_path)
            messagebox.showinfo("สำเร็จ", f"ดาวน์โหลดใบเสร็จเรียบร้อยแล้วที่ {file_path}")
            
            # เปิดไฟล์ PDF โดยอัตโนมัติ
            try:
                if os.name == 'nt':  # สำหรับ Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # สำหรับ macOS และ Linux
                    subprocess.Popen(['open', file_path]) if sys.platform == 'darwin' else subprocess.Popen(['xdg-open', file_path])
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถเปิดไฟล์ PDF ได้: {e}")

    download_button = tk.Button(
        scrollable_frame,
        text="ดาวน์โหลดใบเสร็จ (PDF)",
        font=("KhanoonThin", 14),
        bg="#004aad",
        fg="white",
        command=download_pdf
    )
    download_button.pack(pady=10)

    # ปุ่มปิด
    close_button = tk.Button(scrollable_frame, text="ปิด", bg="#f44336", font=("KhanoonThin", 14), command=receipt_window.destroy)
    close_button.pack(pady=10)

    # รีเฟรช scrollbar
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


def generate_pdf_receipt(order_details, file_path):
    """
    สร้างใบเสร็จในรูปแบบ PDF และบันทึกลงในไฟล์ที่กำหนด
    """
    pdf = FPDF()
    pdf.add_page()
    
    # เพิ่มฟอนต์ภาษาไทย (THSarabunNew)
    pdf.add_font('THSarabunNew', '', r"D:\Project Pythonnnnnn\THSarabunNew\THSarabunNew.ttf", uni=True)
    pdf.set_font('THSarabunNew', '', 16)  # ใช้ฟอนต์ THSarabunNew ขนาด 16

    # ข้อมูลร้าน
    pdf.cell(200, 10, txt="Mangaverse Book Shop", ln=True, align='C')
    pdf.cell(200, 10, txt="ใบเสร็จรับเงิน", ln=True, align='C')
    pdf.ln(10)

    # ข้อมูลลูกค้า
    pdf.cell(200, 10, txt=f"ชื่อลูกค้า: {order_details['username']}", ln=True)
    pdf.cell(200, 10, txt=f"เวลาที่สั่งซื้อ: {order_details['order_time']}", ln=True)
    pdf.ln(10)

    # รายการสินค้า
    pdf.cell(200, 10, txt="รายการสินค้า", ln=True, align='L')
    pdf.ln(5)
    for item in order_details['items']:
        pdf.cell(200, 10, txt=f"{item['name']} x {item['quantity']} = {item['price']}", ln=True)
    pdf.ln(10)

    # ส่วนลด
    if float(order_details['discount'].replace(" บาท", "")) > 0:
        pdf.cell(200, 10, txt=f"ส่วนลด: {order_details['discount']}", ln=True)

    # ราคาสุทธิ
    pdf.cell(200, 10, txt=f"ราคาสุทธิ: {order_details['total_price']}", ln=True)
    pdf.ln(10)

    # ขอบคุณ
    pdf.cell(200, 10, txt="ขอบคุณที่อุดหนุนร้าน Mangaverse Book Shop", ln=True, align='C')

    # บันทึกไฟล์ PDF
    try:
        if os.path.exists(file_path):
            os.remove(file_path)  # ลบไฟล์เก่า
        pdf.output(file_path)
        print(f"บันทึกไฟล์ PDF สำเร็จที่: {file_path}")
    except PermissionError:
        print("ไม่สามารถบันทึกไฟล์ PDF ได้ เนื่องจากไฟล์ถูกเปิดอยู่หรือไม่มีสิทธิ์เขียนไฟล์")
        
def save_cart_items_to_db(receipt_id, cart, book_data):
    try:
        # Connect to the database
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()

        # Loop through the cart and insert each item into the receipt_items table
        for code, quantity in cart.items():
            if quantity > 0:
                # Retrieve product details from the book_data
                product = book_data[get_genre_of_book(code)][code]
                item_total = product["price"] * quantity

                # Insert each item into the receipt_items table
                cursor.execute('''INSERT INTO receipt_items (receipt_id, product_code, product_name, quantity, price) 
                                  VALUES (?, ?, ?, ?, ?)''', 
                               (receipt_id, code, product['name'], quantity, item_total))
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        print("✅ รายการสินค้าได้ถูกบันทึกในฐานข้อมูล")
        

    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกรายการสินค้า: {e}")

def refresh_receipt():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    
    # Clear previous receipt display
    # (Assuming you have a method to clear and reset the display on your receipt page)

    for book_code in cart:
        # Fetch the latest data from database
        cursor.execute("SELECT name, price, quantity FROM products WHERE code = ?", (book_code,))
        result = cursor.fetchone()
        if result:
            book_name, book_price, available_quantity = result
            # Add new updated stock data to receipt
            # (Add the book information with updated stock here)
            print(f"{book_name}: {available_quantity} items left in stock")
            # Display other book details like price and quantity purchased

    conn.close()

def insert_sales_log(order_id, order_items, total_price, order_time):
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    
    # บันทึกข้อมูลการขายใน sales_log
    for product_code, quantity in order_items.items():
        cursor.execute('''
            INSERT INTO sales_log (order_id, product_code, quantity, total_price, order_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, product_code, quantity, total_price, order_time))
        
        # อัปเดตยอดขายในตาราง sales
        cursor.execute('''
            INSERT OR REPLACE INTO sales (username, total_sales)
            VALUES (?, ?)
        ''', (current_user, total_price))  # อัปเดตยอดขายทั้งหมดในตาราง sales

    conn.commit()
    conn.close()

def center_window(window, width, height):
    # คำนวณตำแหน่งของหน้าต่างให้แสดงตรงกลาง
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_left = int(screen_width / 2 - width / 2)
    window.geometry(f'{width}x{height}+{position_left}+{position_top}')

# ตัวอย่างการจัดการที่อยู่ (Lock/Unlock + จำค่าที่กรอกไว้ระหว่างกลับไปกลับมา)

def initialize_address_db():
    """
    สร้าง/เชื่อมต่อฐานข้อมูล addressuser.db
    และสร้างตาราง user_address ถ้ายังไม่มี
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_address_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            fullname TEXT NOT NULL,  
            house_number TEXT NOT NULL,
            subdistrict TEXT NOT NULL,
            district TEXT NOT NULL,
            province TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES mangauser(username)
        )
    ''')
    conn.commit()
    conn.close()

# เรียกฟังก์ชันเพื่อสร้างตาราง user_address ใน addressuser.db
initialize_address_db()

# ตัวแปรสำหรับเก็บข้อมูลที่อยู่ชั่วคราว
delivery_info_data = {
    "fullname": "",
    "house_number": "",
    "subdistrict": "",
    "district": "",
    "province": "",
    "postal_code": "",
    "phone": "",
    "locked": False
}

# ฟังก์ชันเปิดหน้าต่างกรอกที่อยู่
def ask_delivery_details():
    """
    เปิดหน้าต่างกรอกที่อยู่ผู้ใช้
    - ถ้า locked=True -> lock fields
    - สามารถกด save/แก้ไข/back ได้
    """
    delivery_window = tk.Toplevel(root)
    delivery_window.title("กรอกข้อมูลการจัดส่ง")

    # กำหนดขนาดและจัดตรงกลาง
    window_width = 700
    window_height = 600
    center_window(delivery_window, window_width, window_height)
    delivery_window.configure(bg="#e0f7ff")

    entry_width = 35
    entry_font = ("KhanoonThin", 13)
    button_width = 15

    # editing = ถ้ายังไม่ locked => true
    editing = not delivery_info_data.get("locked", False)

    old_data = {
        "fullname": delivery_info_data["fullname"],
        "house_number": delivery_info_data["house_number"],
        "subdistrict": delivery_info_data["subdistrict"],
        "district": delivery_info_data["district"],
        "province": delivery_info_data["province"],
        "postal_code": delivery_info_data["postal_code"],
        "phone": delivery_info_data["phone"]
    }

    # ฟังก์ชัน lock/unlock
    def lock_fields():
        fullname_entry.config(state='disabled')
        house_number_entry.config(state='disabled')
        subdistrict_entry.config(state='disabled')
        district_entry.config(state='disabled')
        province_entry.config(state='disabled')
        postal_code_entry.config(state='disabled')
        phone_entry.config(state='disabled')
        delivery_info_data["locked"] = True

    def unlock_fields():
        fullname_entry.config(state='normal')
        house_number_entry.config(state='normal')
        subdistrict_entry.config(state='normal')
        district_entry.config(state='normal')
        province_entry.config(state='normal')
        postal_code_entry.config(state='normal')
        phone_entry.config(state='normal')
        delivery_info_data["locked"] = False


    # ส่วนสร้าง Label + Entry
    tk.Label(delivery_window, text="ชื่อ-นามสกุล", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=40)
    fullname_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    fullname_entry.place(x=200, y=50, height=30)

    tk.Label(delivery_window, text="บ้านเลขที่", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=90)
    house_number_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    house_number_entry.place(x=200, y=100, height=30)

    tk.Label(delivery_window, text="แขวง/ตำบล", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=140)
    subdistrict_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    subdistrict_entry.place(x=200, y=150, height=30)

    tk.Label(delivery_window, text="อำเภอ", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=190)
    district_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    district_entry.place(x=200, y=200, height=30)

    tk.Label(delivery_window, text="จังหวัด", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=235)
    province_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    province_entry.place(x=200, y=250, height=30)

    tk.Label(delivery_window, text="รหัสไปรษณีย์", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=285)
    postal_code_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    postal_code_entry.place(x=200, y=300, height=30)

    tk.Label(delivery_window, text="เบอร์โทร", bg="#e0f7ff", font=("KhanoonThin", 15)).place(x=55, y=335)
    phone_entry = tk.Entry(delivery_window, width=entry_width, font=entry_font)
    phone_entry.place(x=200, y=350, height=30)

    # ใส่ค่าลง Entry จาก dictionary
    fullname_entry.insert(0, delivery_info_data["fullname"])
    house_number_entry.insert(0, delivery_info_data["house_number"])
    subdistrict_entry.insert(0, delivery_info_data["subdistrict"])
    district_entry.insert(0, delivery_info_data["district"])
    province_entry.insert(0, delivery_info_data["province"])
    postal_code_entry.insert(0, delivery_info_data["postal_code"])
    phone_entry.insert(0, delivery_info_data["phone"])

    if delivery_info_data["locked"]:
        lock_fields()

    def save_address():
        nonlocal editing
        fullname = fullname_entry.get().strip()
        house = house_number_entry.get().strip()
        subd = subdistrict_entry.get().strip()
        dist = district_entry.get().strip()
        prov = province_entry.get().strip()
        post = postal_code_entry.get().strip()
        phone = phone_entry.get().strip()

        # ตรวจสอบข้อมูลที่กรอก
        if not fullname or not house or not subd or not dist or not prov or not post or not phone:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return
        if len(post) != 5 or not post.isdigit():
            messagebox.showwarning("แจ้งเตือน", "รหัสไปรษณีย์ต้องมี 5 หลัก และเป็นตัวเลขเท่านั้น")
            return
        if len(phone) != 10 or not phone.isdigit():
            messagebox.showwarning("แจ้งเตือน", "เบอร์โทรต้องมี 10 หลัก และเป็นตัวเลขเท่านั้น")
            return

        # เก็บข้อมูลใน dictionary
        delivery_info_data["fullname"] = fullname
        delivery_info_data["house_number"] = house
        delivery_info_data["subdistrict"] = subd
        delivery_info_data["district"] = dist
        delivery_info_data["province"] = prov
        delivery_info_data["postal_code"] = post
        delivery_info_data["phone"] = phone

        # เพิ่ม username ลงใน dictionary
        delivery_info_data["username"] = current_user

        # ลองเชื่อมต่อฐานข้อมูล
        retries = 3
        for attempt in range(retries):
            try:
                with sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db") as conn:
                    cursor = conn.cursor()
                    
                    # บันทึกข้อมูลที่อยู่พร้อม username ลงในฐานข้อมูล
                    cursor.execute('''
                        INSERT INTO user_address_new (username, fullname, house_number, subdistrict, district, province, postal_code, phone)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (current_user, fullname, house, subd, dist, prov, post, phone))

                    conn.commit()
                break  # สำเร็จ ให้ออกจากลูป
            except sqlite3.OperationalError as e:
                if attempt < retries - 1:
                    time.sleep(1)  # รอ 1 วินาทีแล้วลองใหม่
                    continue
                else:
                    messagebox.showerror("Error", f"ฐานข้อมูลถูกล็อก กรุณาลองใหม่ภายหลัง\nError: {e}")
                    return
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
                return

        # ล็อกฟิลด์ไม่ให้แก้ไข
        lock_fields()
        editing = False


        # ยืนยันการดำเนินการต่อ
        confirm = messagebox.askyesno("ยืนยัน", "บันทึกที่อยู่นี้แล้ว")
        if confirm:
            delivery_window.destroy()
            # เรียก show_qr_code(pickup=False) หรืออื่นๆ ตามต้องการ
            show_qr_code(pickup=True)
        
    def edit_address():
        nonlocal editing
        unlock_fields()
        editing = True

    def on_close():
        if editing and not delivery_info_data["locked"]:
            ans = messagebox.askyesno("แจ้งเตือน", "คุณยังไม่ได้บันทึกที่อยู่\nต้องการบันทึกเลยหรือไม่?")
            if ans:
                save_address()
                if not editing:
                    delivery_window.destroy()
            else:
                # revert
                delivery_info_data["fullname"] = old_data["fullname"]
                delivery_info_data["house_number"] = old_data["house_number"]
                delivery_info_data["subdistrict"] = old_data["subdistrict"]
                delivery_info_data["district"] = old_data["district"]
                delivery_info_data["province"] = old_data["province"]
                delivery_info_data["postal_code"] = old_data["postal_code"]
                delivery_info_data["phone"] = old_data["phone"]
                delivery_info_data["locked"] = False
                delivery_window.destroy()
        else:
            delivery_window.destroy()

    delivery_window.protocol("WM_DELETE_WINDOW", on_close)

    save_button = tk.Button(delivery_window, text="📁บันทึกที่อยู่",
                            bg="#4ab662", font="KhanoonThin",
                            width=button_width, command=save_address)
    save_button.place(x=460, y=500)

    edit_button = tk.Button(delivery_window, text="✎แก้ไขที่อยู่",
                            bg="#ffcc4d", font="KhanoonThin",
                            width=button_width, command=edit_address)
    edit_button.place(x=270, y=500)

    back_button = tk.Button(delivery_window, text="◀Back",
                            bg="#ee2530", font="KhanoonThin",
                            width=button_width, command=on_close)
    back_button.place(x=70, y=500)

# ฟังก์ชั่นให้หน้าต่างแสดงตรงกลาง
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_left = int(screen_width / 2 - width / 2)
    window.geometry(f'{width}x{height}+{position_left}+{position_top}')

def update_cart_and_stock():
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    for code, quantity in cart.items():
        if quantity > 0:
            cursor.execute('SELECT quantity FROM products WHERE code=?', (code,))
            result = cursor.fetchone()
            if result:
                available_quantity = result[0]
                new_quantity = available_quantity - quantity
                if new_quantity < 0:
                    new_quantity = 0
                cursor.execute('UPDATE products SET quantity=? WHERE code=?', (new_quantity, code))
    conn.commit()
    conn.close()

    # โหลดข้อมูลสินค้าจากฐานข้อมูลใหม่
    load_book_data()

    # รีเฟรชเฟรมหมวดหมู่
    refresh_category_frames()

def create_nav_button(image_path, x, y, command, bg_color="#004aad"):
    icon = load_image(image_path, (70, 70))
    if icon is None:
        # สร้างปุ่มข้อความถ้ารูปภาพโหลดไม่ได้
        button = tk.Button(root, text=os.path.basename(image_path), command=command, bg=bg_color, fg="white")
        button.place(x=x, y=y, width=70, height=70)
    else:
        button = tk.Label(root, image=icon, bg=bg_color, cursor="hand2")
        button.image = icon  # เก็บอ้างอิงรูปภาพ
        button.bind("<Button-1>", lambda e: command())
        button.place(x=x, y=y)
    return button

# --------------------- Frames ---------------------
# Category frame
category_frame = tk.Frame(main_frame, bg="#e0f7ff")
set_background_image(category_frame, r"c:\Users\acer\Pictures\PJ\ccc.png", size=(1200, 800))  # ตั้งค่ารูปพื้นหลัง

# สร้างเฟรมสำหรับแต่ละหมวดหมู่
frames = {}
background_placeholder = r"c:\Users\acer\Pictures\PJ\book\placeholder.png"  # Path ของรูป placeholder

category_backgrounds = {
    "Action": r"c:\Users\acer\Pictures\PJ\frame\ActionFrame.png",
    "Drama": r"c:\Users\acer\Pictures\PJ\frame\DramaFrame.png",
    "Romance": r"c:\Users\acer\Pictures\PJ\frame\RomanceFrame.png",
    "Horror": r"c:\Users\acer\Pictures\PJ\frame\HorrorFrame.png",
    "Fantasy": r"c:\Users\acer\Pictures\PJ\frame\FantasyFrame.png",
    "Comedy": r"c:\Users\acer\Pictures\PJ\frame\ComedyFrame.png",
    "Sport": r"c:\Users\acer\Pictures\PJ\frame\SportFrame.png",
}

for genre in book_data.keys():
    frames[genre] = tk.Frame(main_frame, bg="#e0f7ff")
    background_path = category_backgrounds.get(genre, background_placeholder)
    set_background_image(frames[genre], background_path, size=(1200, 800))

# Home frame
home_frame = tk.Frame(main_frame, bg="#e0f7ff")
set_background_image(home_frame, r"c:\Users\acer\Pictures\PJ\589.png", size=(1200, 800))  # ตั้งค่ารูปพื้นหลังหน้าแรก

# Introduce frame
introduce_frame = tk.Frame(main_frame, bg="#e0f7ff")
set_background_image(introduce_frame, r"c:\Users\acer\Pictures\PJ\111166.png", size=(1200, 800))  # ตั้งค่ารูปพื้นหลังหน้าแนะนำ

# Cart frame
cart_frame = tk.Frame(main_frame, bg="#e0f7ff")
set_background_image(cart_frame, r"c:\Users\acer\Pictures\PJ\112.png", size=(1200, 800))  # ตั้งค่ารูปพื้นหลังตะกร้า

# Order frame
order_frame = tk.Frame(main_frame, bg="#e0f7ff")
set_background_image(order_frame, r"c:\Users\acer\Pictures\PJ\112.png", size=(1200, 800))  # ตั้งค่ารูปพื้นหลังการสั่งซื้อ

# --------------------- Initialize Category Frame ---------------------
def initialize_category_frame():
    display_all_categories()

initialize_category_frame()

# --------------------- Navigation Buttons Setup ---------------------
# กำหนด path ของรูปภาพสำหรับปุ่มนำทาง
home_icon_path = r"c:\Users\acer\Pictures\PJ\a.png"
introduce_icon_path = r"c:\Users\acer\Pictures\PJ\b.png"
category_icon_path = r"c:\Users\acer\Pictures\PJ\c.png"
cart_icon_path = r"c:\Users\acer\Pictures\PJ\d.png"
order_icon_path = r"c:\Users\acer\Pictures\PJ\e.png"
receipt_icon_path = r"C:\Users\acer\Pictures\PJ\recipet_icon.png"  # Path ไอคอนใบเสร็จ

# สร้างปุ่มนำทางหลัก
create_nav_button(home_icon_path, 27, 15, lambda: show_frame(home_frame), bg_color="#c9e0ff")
create_nav_button(introduce_icon_path, 162, 15, lambda: show_frame(introduce_frame), bg_color="#004aad")
create_nav_button(category_icon_path, 295, 13, lambda: show_frame(category_frame), bg_color="#c9e0ff")
create_nav_button(cart_icon_path, 428, 15, lambda: open_cart_window(), bg_color="#004aad")
create_nav_button(order_icon_path, 560, 15, lambda: proceed_to_order(), bg_color="#c9e0ff")
create_nav_button(receipt_icon_path, 697, 15, open_receipt_icon, bg_color="#004aad")

# --------------------- Contact and Exit Buttons ---------------------
# ปุ่มติดต่อเรา
def show_contact_image_window():
    # ใช้ฟังก์ชัน create_centered_window เพื่อสร้างหน้าต่างที่จัดตรงกลาง
    contact_window = create_centered_window("Contact Us", 850, 580, bg_color="#fff")
    
    contact_image_path = r"C:\Users\acer\Pictures\PJ\contact us.png"  # เปลี่ยนเส้นทางตามจริง
    contact_image = load_image(contact_image_path, (850, 580))
    if contact_image:
        contact_label = tk.Label(contact_window, image=contact_image, bg="#fff")
        contact_label.image = contact_image
        contact_label.pack()
    
    # ปุ่มปิดแบบจัดตำแหน่งสัมพัทธ์
    close_button = tk.Button(contact_window, text="Back", font=("Wonderful Future", 10), bg="#fd5c70", fg="white",
                             command=contact_window.destroy, cursor="hand2")
    # จัดวางปุ่มให้อยู่มุมบนขวาโดยใช้ relx และ rely
    close_button.place(relx=0.98, rely=0.04, anchor='ne')  # relx=0.95 หมายถึง 95% ของความกว้าง, rely=0.05 หมายถึง 5% ของความสูง

# ปุ่มติดต่อเรา
contact_button = tk.Button(root, text="Contact us", font=("Wonderful Future", 14), bg="#004aad", fg="white",
                           command=show_contact_image_window, cursor="hand2")  
contact_button.place(x=20, y=750)  # วางปุ่มตำแหน่งที่กำหนด

# ปุ่มออกจากโปรแกรม
exit_button = tk.Button(root, text="Exit", font=("Wonderful Future", 14), bg="#004aad", fg="white", command=root.quit)
exit_button.place(x=1120, y=750)  # วางปุ่มออกจากโปรแกรม

# --------------------- Logout Button ---------------------
def confirm_logout():
    if messagebox.askyesno("Log Out", "คุณต้องการออกจากระบบใช่หรือไม่?"):
        root.destroy()
        open_login_page()

def open_login_page():
    try:
        subprocess.Popen(['python', r"D:\Project Pythonnnnnn\login_page.py"])  # เปลี่ยนเส้นทางตามจริง
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเปิด Login Page ได้\n{e}")

def logout():
    confirm_logout()

logout_button = tk.Button(
    root,
    text="Log Out",
    font=("Wonderful Future", 14),
    bg="#004aad",
    fg="white",
    command=logout
)
logout_button.place(x=1020, y=750)

# --------------------- Main Loop ---------------------
# เริ่มต้นด้วยการแสดงหน้าหลัก
show_frame(home_frame)

# จัดการเหตุการณ์ปิดหน้าต่าง
def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# --------------------- Cart Window and Functions ---------------------
def open_cart_window():
    global cart_window, scrollable_cart_frame
    try:
        if cart_window.winfo_exists():
            cart_window.lift()
            return
    except:
        pass

    cart_window = tk.Toplevel(root)
    cart_window.title("ตะกร้าสินค้า")
    center_window(cart_window, 700, 600)
    cart_window.configure(bg="#e0f7ff")

    inner_frame = tk.Frame(cart_window, bg="#e0f7ff")
    inner_frame.pack(pady=20, padx=20, fill="both", expand=True)

    canvas = tk.Canvas(inner_frame, bg="#e0f7ff", width=500, height=600, highlightthickness=0)
    scrollbar = tk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
    scrollable_cart_frame = tk.Frame(canvas, bg="#e0f7ff")

    scrollable_cart_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_cart_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Populate the cart window
    update_cart()

def adjust_cart_quantity(book_code, change):
    available_quantity = get_available_quantity(book_code)
    current_qty = cart.get(book_code, 0)
    new_qty = current_qty + change

    if new_qty < 0:
        new_qty = 0
    elif new_qty > available_quantity:
        new_qty = available_quantity
        messagebox.showwarning("Stock Limit", f"ไม่สามารถเพิ่ม '{book_data[get_genre_of_book(book_code)][book_code]['name']}' ได้มากกว่าจำนวนในสต๊อกที่มี ({available_quantity})")

    if new_qty != current_qty:
        if new_qty == 0:
            cart.pop(book_code, None)
        else:
            cart[book_code] = new_qty
        
        # Update the stock in the database
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE code = ?", (change, book_code))
        conn.commit()
        conn.close()

        if book_code in cart_quantity_vars:
            cart_quantity_vars[book_code].set(str(new_qty))
        update_cart()

def set_quantity_cart(book_code):
    try:
        # Get value from Entry
        new_quantity = int(cart_quantity_vars[book_code].get())
        if new_quantity < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("แจ้งเตือน", "กรุณาใส่จำนวนสินค้าเป็นจำนวนเต็มที่ไม่ติดลบ")
        # Reset Entry to current cart quantity
        if book_code in cart:
            cart_quantity_vars[book_code].set(str(cart.get(book_code, 0)))
        else:
            cart_quantity_vars[book_code].set("0")
        return

    # Check stock
    available_quantity = get_available_quantity(book_code)
    if new_quantity > available_quantity:
        messagebox.showwarning("แจ้งเตือน", f"จำนวนที่สั่งเกินสต๊อก! สต๊อกที่มีอยู่: {available_quantity}")
        if book_code in cart:
            cart_quantity_vars[book_code].set(str(cart.get(book_code, 0)))
        else:
            cart_quantity_vars[book_code].set("0")
        return

    # Update cart
    if new_quantity > 0:
        cart[book_code] = new_quantity
    else:
        cart.pop(book_code, None)

    # Update stock in database
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE code = ?", (new_quantity - cart.get(book_code, 0), book_code))
    conn.commit()
    conn.close()

    # Update cart UI
    update_cart()

def remove_from_cart(book_code):
    if book_code in cart:
        cart.pop(book_code)
        update_cart()

def calculate_total_quantity():
    return sum(cart.values())

def update_cart():
    global scrollable_cart_frame
    if cart_window is None or not cart_window.winfo_exists():
        return

    # Clear scrollable_cart_frame
    for widget in scrollable_cart_frame.winfo_children():
        widget.destroy()

    # Create title and back button
    cart_title = tk.Label(scrollable_cart_frame, text="🧺ตะกร้าสินค้า", font=("KhanoonThin", 20, "bold"), bg="#e0f7ff")
    cart_title.pack(pady=10)

    back_button = tk.Button(
        scrollable_cart_frame,
        text="Back",
        font=("KhanoonThin", 12),
        bg="#fd5c70",
        fg="white",
        command=cart_window.destroy,
        cursor="hand2"
    )
    back_button.pack(pady=5, anchor='ne')

    total_price = 0
    total_quantity = calculate_total_quantity()

    for code, quantity in cart.items():
        # Fetch product details
        conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
        cursor = conn.cursor()
        cursor.execute("SELECT genre, name, price, quantity, image_path FROM products WHERE code = ?", (code,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            continue
        genre, name, price, available_quantity, image_path = result

        if quantity <= 0:
            continue

        item_frame = tk.Frame(scrollable_cart_frame, bg="#e0f7ff", highlightbackground="#cccccc", highlightthickness=1)
        item_frame.pack(pady=5, padx=10, fill="x")

        # Row 0: Image, Name, Quantity Controls, Price
        # Row 1: (Empty), Code, 🗑️, Message

        # Load and display book image
        book_image = load_image(image_path, (80, 80))
        if book_image:
            image_label = tk.Label(item_frame, image=book_image, bg="#e0f7ff")
            image_label.image = book_image  # Keep a reference
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)

        # Product name
        name_label = tk.Label(item_frame, text=name, font=("KhanoonThin", 12, "bold"), bg="#e0f7ff", anchor="w")
        name_label.grid(row=0, column=1, sticky="w", padx=(0,10))

        # Quantity controls
        quantity_frame = tk.Frame(item_frame, bg="#e0f7ff")
        quantity_frame.grid(row=0, column=2, padx=10, sticky="e")

        # Minus button
        minus_button = tk.Button(
            quantity_frame,
            text="-",
            font=("KhanoonThin", 10),
            width=2,
            command=lambda c=code: adjust_cart_quantity(c, -1)
        )
        minus_button.grid(row=0, column=0)

        # Quantity entry
        qty_var = tk.StringVar()
        qty_var.set(str(quantity))
        quantity_entry = tk.Entry(quantity_frame, textvariable=qty_var, width=5, font=("KhanoonThin", 10), justify='center')
        quantity_entry.grid(row=0, column=1)
        quantity_entry.bind("<Return>", lambda e, c=code: set_quantity(c))
        cart_quantity_vars[code] = qty_var

        # Plus button
        plus_button = tk.Button(
            quantity_frame,
            text="+",
            font=("KhanoonThin", 10),
            width=2,
            command=lambda c=code: adjust_cart_quantity(c, 1)
        )
        plus_button.grid(row=0, column=2)

        # Calculate total
        item_total = price * quantity
        total_price += item_total

        # Display item total price
        price_label = tk.Label(item_frame, text=f"{format_price(item_total)}", font=("KhanoonThin", 10), bg="#e0f7ff")
        price_label.grid(row=0, column=3, sticky="e", padx=10)

        # Load black trash can image
        trash_can_path = r"C:\Users\acer\Pictures\PJ\black_trash_can.png"  # ระบุเส้นทางที่ถูกต้อง
        trash_can_image = load_image(trash_can_path, (27, 30))  # ขนาดใหญ่ขึ้นตามต้องการ
        if trash_can_image:
            delete_label = tk.Label(
                item_frame,
                image=trash_can_image,
                bg="#e0f7ff",
                cursor="hand2"
            )
            delete_label.image = trash_can_image  # Keep a reference
            delete_label.grid(row=1, column=2, padx=10, pady=5, sticky='w')
            # Bind click event to remove_from_cart
            delete_label.bind("<Button-1>", lambda e, c=code: remove_from_cart(c))

        # Product code
        code_label = tk.Label(item_frame, text=f"รหัส: {code}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="w")
        code_label.grid(row=1, column=1, sticky="w")

        # Message (e.g., "สินค้าหมดแล้ว")
        if quantity >= available_quantity:
            message_label = tk.Label(item_frame, text="สินค้าหมดแล้ว", font=("KhanoonThin", 10), bg="#e0f7ff", fg="red")
            message_label.grid(row=1, column=3, sticky="e")
            plus_button.config(state='disabled')
        else:
            # Clear any previous message
            message_label = tk.Label(item_frame, text="", font=("KhanoonThin", 10), bg="#e0f7ff")
            message_label.grid(row=1, column=3, sticky="e")

    # Calculate discount
    discount = 0
    if total_quantity >= 4:
        discount = total_price * 0.10
        discounted_price = total_price - discount
        discount_label = tk.Label(scrollable_cart_frame, text=f"ส่วนลด 10%: -{format_price(int(discount))}", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff", fg="green")
        discount_label.pack(pady=5)
        total_price = discounted_price

    # Display total price
    total_label = tk.Label(scrollable_cart_frame, text=f"รวมทั้งหมด: {format_price(int(total_price))}", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff")
    total_label.pack(pady=10)

    # Checkout button
    checkout_button = tk.Button(
        scrollable_cart_frame,
        text="สั่งซื้อสินค้า",
        font=("KhanoonThin", 14),
        bg="#004aad",
        fg="white",
        command=lambda: proceed_to_order(),
        cursor="hand2"
    )
    checkout_button.pack(pady=10)

    # Refresh scrollbar
    scrollable_cart_frame.update_idletasks()
    canvas = scrollable_cart_frame.master.master  # Canvas is the grandparent
    canvas.config(scrollregion=canvas.bbox("all"))

# --------------------- Order Functions ---------------------
def proceed_to_order():
    if not cart:
        messagebox.showinfo("ʕ>⌓<｡ʔ", "ตะกร้าสินค้าไม่มีรายการ")
        return
    
    # Check stock before proceeding to order
    for book_code, qty in cart.items():
        available_quantity = get_available_quantity(book_code)
        if qty > available_quantity:
            messagebox.showwarning("Stock Limit", f"สินค้ารายการ {book_code} จำนวนไม่พอในสต๊อก")
            return

    open_order_window()

def open_order_window():
    global order_window, scrollable_order_frame
    try:
        if order_window.winfo_exists():
            order_window.lift()
            return
    except:
        pass

    order_window = tk.Toplevel(root)
    order_window.title("Order")
    center_window(order_window, 700, 600)
    order_window.configure(bg="#e0f7ff")

    inner_frame = tk.Frame(order_window, bg="#e0f7ff")
    inner_frame.pack(pady=20, padx=20, fill="both", expand=True)

    canvas = tk.Canvas(inner_frame, bg="#e0f7ff", width=500, height=600, highlightthickness=0)
    scrollbar = tk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
    scrollable_order_frame = tk.Frame(canvas, bg="#e0f7ff")

    scrollable_order_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_order_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title and back button
    order_title = tk.Label(scrollable_order_frame, text="🛒รายการสั่งซื้อ", font=("KhanoonThin", 20, "bold"), bg="#e0f7ff")
    order_title.pack(pady=10)

    back_button = tk.Button(
        scrollable_order_frame,
        text="Back",
        font=("KhanoonThin", 12),
        bg="#fd5c70",
        fg="white",
        command=order_window.destroy,
        cursor="hand2"
    )
    back_button.pack(pady=5, anchor='ne')

    total_price = 0
    total_quantity = 0

    for code, quantity in cart.items():
        if quantity > 0:
            product = book_data[get_genre_of_book(code)][code]
            item_total = product["price"] * quantity
            total_price += item_total
            total_quantity += quantity

            item_frame = tk.Frame(scrollable_order_frame, bg="#e0f7ff", highlightbackground="#cccccc", highlightthickness=1)
            item_frame.pack(pady=5, padx=10, fill="x")

            # Load and display book image
            book_image = load_image(product['image'], (80,80))
            if book_image:
                image_label = tk.Label(item_frame, image=book_image, bg="#e0f7ff")
                image_label.image = book_image
                image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)

            # Product name
            name_label = tk.Label(item_frame, text=product['name'], font=("KhanoonThin", 12, "bold"), bg="#e0f7ff", anchor="w")
            name_label.grid(row=0, column=1, sticky="w")

            # Product code
            code_label = tk.Label(item_frame, text=f"รหัส: {code}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="w")
            code_label.grid(row=1, column=1, sticky="w")

            # Quantity
            qty_label = tk.Label(item_frame, text=f"จำนวน: {quantity}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="w")
            qty_label.grid(row=0, column=2, sticky="e")

            # Price
            price_total = product["price"] * quantity
            price_label = tk.Label(item_frame, text=f"ราคา: {format_price(price_total)}", font=("KhanoonThin", 10), bg="#e0f7ff", anchor="e")
            price_label.grid(row=1, column=2, sticky="e")

    # Calculate discount
    discount = 0
    if total_quantity >= 4:
        discount = total_price * 0.10
        discounted_price = total_price - discount
        discount_label = tk.Label(scrollable_order_frame, text=f"ส่วนลด 10%: -{format_price(int(discount))}", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff", fg="green")
        discount_label.pack(pady=5)
        total_price = discounted_price

    # Display total
    total_label = tk.Label(scrollable_order_frame, text=f"รวมทั้งหมด: {format_price(int(total_price))}", font=("KhanoonThin", 14, "bold"), bg="#e0f7ff")
    total_label.pack(pady=10)
 # สร้างตัวแปร IntVar เพียงตัวเดียว เก็บค่าการจัดส่ง
    delivery_method_var = tk.IntVar(value=0)  # 0 = ยังไม่เลือก, 1 = รับที่ร้าน, 2 = จัดส่ง

    order_options = tk.Frame(scrollable_order_frame, bg="#e0f7ff")
    order_options.pack(pady=10)

    # Radio Button "รับที่ร้าน" -> value=1
    pickup_radio = tk.Radiobutton(
        order_options, text="รับสินค้าที่ร้าน",
        variable=delivery_method_var, value=1, 
        bg="#e0f7ff", font=("KhanoonThin", 12)
    )
    pickup_radio.grid(row=0, column=0, padx=10, pady=5)

    # Radio Button "จัดส่ง" -> value=2
    delivery_radio = tk.Radiobutton(
        order_options, text="จัดส่งตามที่อยู่",
        variable=delivery_method_var, value=2,
        bg="#e0f7ff", font=("KhanoonThin", 12)
    )
    delivery_radio.grid(row=0, column=1, padx=10, pady=5)

    # ปุ่มยืนยัน
    def on_confirm_order():
        selected_method = delivery_method_var.get()

        if selected_method == 0:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกวิธีการสั่งซื้อ (รับที่ร้าน/จัดส่ง)")
            return

        elif selected_method == 1:  # ✅ รับสินค้าที่ร้าน
            finalize_order(pickup=True, delivery=False)

        elif selected_method == 2:  # ✅ จัดส่งสินค้า
            conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username FROM user_address_new WHERE username = ? LIMIT 1
            ''', (current_user,))
            address_result = cursor.fetchone()
            conn.close()

            if address_result:
                # ✅ ถ้ามีที่อยู่แล้ว ให้ไปที่ finalize_order() เพื่อบันทึก order_id แล้วเปิด QR Code
                finalize_order(pickup=False, delivery=True)
            else:
                # ❌ ถ้าไม่มีที่อยู่ ให้ไปที่หน้ากรอกที่อยู่ก่อน
                ask_delivery_details()

    confirm_button = tk.Button(
        scrollable_order_frame,
        text="ยืนยันการสั่งซื้อ",
        font=("KhanoonThin", 14),
        bg="#004aad",
        fg="white",
        command=on_confirm_order,
        cursor="hand2"
    )
    confirm_button.pack(pady=10)


    # ----------------------------------------------------------

    # รีเฟรช scrollbar
    scrollable_order_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
# ฟังก์ชันสำหรับบันทึกข้อมูลคำสั่งซื้อ
def insert_order_items(order_id, cart_items):
    """
    บันทึกข้อมูลสินค้าภายในคำสั่งซื้อไปยังตาราง order_items

    Parameters:
    order_id (int): หมายเลขคำสั่งซื้อที่เกี่ยวข้อง
    cart_items (dict): รายการสินค้าที่อยู่ในตะกร้า (รหัสสินค้า -> จำนวนสินค้า)
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()

    try:
        # วนลูปเพื่อเพิ่มสินค้าทั้งหมดลงใน order_items
        for product_code, quantity in cart_items.items():
            cursor.execute("SELECT price FROM products WHERE code = ?", (product_code,))
            result = cursor.fetchone()
            if result:
                unit_price = result[0]
                total_price = unit_price * quantity

                cursor.execute("""
                    INSERT INTO order_items (order_id, product_code, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, product_code, quantity, total_price))

        conn.commit()
        print("✅ บันทึกข้อมูล order_items สำเร็จ")
    
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึก order_items: {e}")
    
    finally:
        conn.close()

def get_order_items(order_id):
    """
    ดึงข้อมูลสินค้าที่อยู่ในคำสั่งซื้อที่ระบุ
    """
    conn = sqlite3.connect(r"D:\Project Pythonnnnnn\bookstore.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT oi.product_code, p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_code = p.code
            WHERE oi.order_id = ?
        """, (order_id,))

        items = cursor.fetchall()
        return items
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล order_items: {e}")
        return []
    finally:
        conn.close()
    for item in items:
        print(f"รหัสสินค้า: {item[0]}, ชื่อสินค้า: {item[1]}, จำนวน: {item[2]}, ราคา: {item[3]:,.2f} บาท")

# --------------------- Final Integration ---------------------
def show_cart_window():
    open_cart_window()

# --------------------- Final Integration ---------------------
def show_receipt_after_payment(order_cart):
    show_order_frame(order_cart)

# --------------------- Complete Code ---------------------
root.mainloop() 