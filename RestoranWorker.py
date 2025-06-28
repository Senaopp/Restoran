import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import datetime
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random


# Настройки подключения к Supabase
SUPABASE_URL = "https://pyryfmngwdalgngvocry.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5cnlmbW5nd2RhbGduZ3ZvY3J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMzM5NDIsImV4cCI6MjA2NjYwOTk0Mn0.iXHNSauBxf2QlLFJbZ7dDsGtbvzaLHBq_FQ6tlH0W4I"

# Настройка клиента с автоматическим обновлением токена
client_options = ClientOptions(
    auto_refresh_token=True,
    persist_session=True
)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, client_options)

class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ресторан: Система управления")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')
        self.root.attributes('-topmost', True)  # Окно поверх всех других
        self.current_user = None
        self.current_profile = None
        self.setup_styles()
        self.show_login_page()

    def setup_styles(self):
        self.style = ttk.Style()
        
        # Цветовая схема
        self.bg_color = "#2c3e50"
        self.header_color = "#1a252f"
        self.accent_color = "#3498db"
        self.success_color = "#2ecc71"
        self.warning_color = "#e74c3c"
        self.content_bg = "#ecf0f1"
        
        # Настройка стилей
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Header.TFrame", background=self.header_color)
        self.style.configure("Title.TLabel", background=self.bg_color, foreground="white", 
                            font=("Arial", 20, "bold"))
        self.style.configure("Subtitle.TLabel", background=self.bg_color, foreground="#ecf0f1", 
                            font=("Arial", 14))
        self.style.configure("Content.TFrame", background=self.content_bg)
        
        self.style.configure("TButton", font=("Arial", 12), padding=10)
        self.style.configure("Primary.TButton", background=self.accent_color, foreground="black")
        self.style.configure("Success.TButton", background=self.success_color, foreground="black")
        self.style.configure("Danger.TButton", background=self.warning_color, foreground="black")
        
        self.style.configure("Treeview", font=("Arial", 11), rowheight=35, background="white")
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#bdc3c7")
        self.style.map("Treeview", background=[("selected", self.accent_color)])
        
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TCombobox", font=("Arial", 12), padding=5)
        self.style.configure("Header.TLabel", background=self.header_color, foreground="white", 
                            font=("Arial", 14))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_window()
        
        # Фоновая картинка
        try:
            response = requests.get("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4")
            bg_image = Image.open(BytesIO(response.content))
            bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.root.configure(bg=self.bg_color)
        
        # Основной фрейм для входа
        login_frame = ttk.Frame(self.root, style="TFrame")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок
        ttk.Label(login_frame, text="Вход в систему", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Поля ввода
        ttk.Label(login_frame, text="Email:", style="Subtitle.TLabel").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(login_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        self.email_entry.focus()
        
        ttk.Label(login_frame, text="Пароль:", style="Subtitle.TLabel").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопка входа
        login_btn = ttk.Button(login_frame, text="Войти", style="Primary.TButton", command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Автозаполнение для теста
        self.email_entry.insert(0, "admin@restaurant.com")
        self.password_entry.insert(0, "")

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Ошибка", "Введите email и пароль")
            return
        
        try:
            # Аутентификация через Supabase Auth
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                self.current_user = response.user
                
                # Получаем профиль пользователя
                profile_response = supabase.table("profiles").select("*").eq("id", response.user.id).execute()
                
                if profile_response.data:
                    self.current_profile = profile_response.data[0]
                    self.show_main_interface()
                else:
                    messagebox.showerror("Ошибка", "Профиль пользователя не найден")
            else:
                messagebox.showerror("Ошибка", "Неверный email или пароль")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка входа: {str(e)}")

    def show_main_interface(self):
        self.clear_window()
        
        # Создаем верхнюю панель
        header_frame = ttk.Frame(self.root, style="Header.TFrame", height=80)
        header_frame.pack(fill="x", side="top")
        
        # Информация о пользователе
        user_info = ttk.Label(
            header_frame, 
            text=f"{self.current_profile['full_name']} ({self.current_profile['role']})",
            style="Header.TLabel"
        )
        user_info.pack(side="left", padx=20)
        
        # Кнопка выхода
        logout_btn = ttk.Button(
            header_frame, 
            text="Выйти", 
            style="Danger.TButton",
            command=self.show_login_page
        )
        logout_btn.pack(side="right", padx=20)
        
        # Основной контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Создаем боковое меню
        sidebar = ttk.Frame(main_container, width=250, style="TFrame")
        sidebar.pack(fill="y", side="left", padx=(0, 20))
        
        # В зависимости от роли пользователя показываем разные кнопки
        role = self.current_profile["role"]
        
        if role == "admin":
            ttk.Button(
                sidebar, 
                text="Создать пользователя", 
                style="Primary.TButton",
                command=self.show_create_user
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Управление меню", 
                style="Primary.TButton",
                command=self.show_menu_management
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Статистика", 
                style="Primary.TButton",
                command=self.show_statistics
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Управление столами", 
                style="Primary.TButton",
                command=self.show_tables_management
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Просмотр бронирований", 
                style="Primary.TButton",
                command=self.show_reservations
            ).pack(fill="x", pady=5)
            
        elif role == "waiter":
            ttk.Button(
                sidebar, 
                text="Бронирование столов", 
                style="Primary.TButton",
                command=self.show_reservations
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Создать заказ", 
                style="Primary.TButton",
                command=self.create_order
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Текущие заказы", 
                style="Primary.TButton",
                command=self.show_current_orders
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Счета и оплаты", 
                style="Primary.TButton",
                command=self.show_bills
            ).pack(fill="x", pady=5)
            
        elif role == "chef":
            ttk.Button(
                sidebar, 
                text="Заказы на кухне", 
                style="Primary.TButton",
                command=self.show_kitchen_orders
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Инвентарь", 
                style="Primary.TButton",
                command=self.show_inventory
            ).pack(fill="x", pady=5)
            
            ttk.Button(
                sidebar, 
                text="Управление блюдами", 
                style="Primary.TButton",
                command=self.show_menu_management
            ).pack(fill="x", pady=5)
        
        # Основная область контента
        self.content_area = ttk.Frame(main_container, style="Content.TFrame")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Показываем приветственное сообщение
        self.show_welcome_message()

    def show_welcome_message(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        welcome_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(
            welcome_frame, 
            text=f"Добро пожаловать, {self.current_profile['full_name']}!",
            style="Title.TLabel"
        ).pack(pady=20)
        
        role = self.current_profile["role"]
        role_text = {
            "admin": "Вы администратор системы. Вы можете создавать пользователи, управлять меню и просматривать статистику.",
            "waiter": "Вы официант. Вы можете управлять бронированиями, создавать заказы и обслуживать клиентов.",
            "chef": "Вы повар. Вы можете просматривать текущие заказы и управлять инвентарем кухни."
        }.get(role, "")
        
        ttk.Label(
            welcome_frame, 
            text=role_text,
            style="Subtitle.TLabel",
            wraplength=800
        ).pack(pady=10)
        
        # Показываем текущее время
        time_frame = ttk.Frame(welcome_frame, style="Content.TFrame")
        time_frame.pack(pady=20)
        
        self.time_label = ttk.Label(
            time_frame, 
            text=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            style="Subtitle.TLabel",
            font=("Arial", 16)
        )
        self.time_label.pack()
        
        # Останавливаем предыдущий таймер, если он был
        if hasattr(self, 'time_update_id'):
            self.root.after_cancel(self.time_update_id)
        
        # Обновление времени каждую секунду
        self.update_time()

    def update_time(self):
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.config(text=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            self.time_update_id = self.root.after(1000, self.update_time)

    def show_create_user(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        form_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        form_frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        ttk.Label(form_frame, text="Создать нового пользователя", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Поля формы
        fields = [
            ("ФИО", "full_name"),
            ("Email", "email"),
            ("Телефон", "phone"),
            ("Пароль", "password"),
            ("Подтверждение пароля", "confirm_password"),
            ("Роль", "role")
        ]
        
        self.entries = {}
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label + ":", style="Subtitle.TLabel").grid(row=i+1, column=0, sticky="e", padx=10, pady=10)
            
            if field == "role":
                role_var = tk.StringVar()
                role_combo = ttk.Combobox(
                    form_frame, 
                    textvariable=role_var,
                    values=["admin", "waiter", "chef"],
                    state="readonly",
                    width=27
                )
                role_combo.current(0)
                role_combo.grid(row=i+1, column=1, padx=10, pady=10)
                self.entries[field] = role_var
            elif field == "password" or field == "confirm_password":
                entry = ttk.Entry(form_frame, show="*", width=30)
                entry.grid(row=i+1, column=1, padx=10, pady=10)
                self.entries[field] = entry
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i+1, column=1, padx=10, pady=10)
                self.entries[field] = entry
        
        # Кнопки
        btn_frame = ttk.Frame(form_frame, style="Content.TFrame")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame, 
            text="Создать", 
            style="Success.TButton",
            command=self.create_user
        ).pack(side="left", padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            style="Danger.TButton",
            command=self.show_welcome_message
        ).pack(side="left", padx=10)

    def create_user(self):
        # Получаем данные из формы
        data = {}
        for field, entry in self.entries.items():
            if isinstance(entry, tk.StringVar):
                data[field] = entry.get()
            else:
                data[field] = entry.get()
        
        # Проверки
        if not data["full_name"]:
            messagebox.showerror("Ошибка", "Введите ФИО пользователя")
            return
            
        if not data["email"] or "@" not in data["email"]:
            messagebox.showerror("Ошибка", "Введите корректный email")
            return
            
        if not data["password"] or len(data["password"]) < 6:
            messagebox.showerror("Ошибка", "Пароль должен содержать не менее 6 символов")
            return
            
        if data["password"] != data["confirm_password"]:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
            
        try:
            # Регистрация пользователя через Supabase Auth с передачей роли в метаданных
            auth_response = supabase.auth.sign_up({
                "email": data["email"],
                "password": data["password"],
                "options": {
                    "data": {
                        "full_name": data["full_name"],
                        "role": data["role"]  # Важно: передаем роль в метаданных
                    }
                }
            })
            
            if auth_response.user:
                # Дополнительно создаем профиль в таблице profiles
                user_data = {
                    "id": auth_response.user.id,
                    "email": data["email"],
                    "full_name": data["full_name"],
                    "phone": data.get("phone", ""),
                    "role": data["role"]  # Явно указываем роль
                }
                
                # Вставляем или обновляем профиль
                supabase.table("profiles").upsert(user_data).execute()
                
                messagebox.showinfo("Успех", "Пользователь успешно создан!")
                self.show_welcome_message()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания пользователя: {str(e)}")

    def show_menu_management(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление меню", style="Title.TLabel").pack(pady=(0, 20))
        
        # Получаем данные меню из базы
        try:
            response = supabase.table("menu").select("*").execute()
            menu_items = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить меню: {str(e)}")
            menu_items = []
        
        # Таблица с блюдами
        columns = ("id", "name", "category", "price", "availability")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Заголовки
        tree.heading("id", text="ID")
        tree.heading("name", text="Название")
        tree.heading("category", text="Категория")
        tree.heading("price", text="Цена")
        tree.heading("availability", text="Доступно")
        
        # Настройка столбцов
        tree.column("id", width=50, anchor="center")
        tree.column("name", width=250)
        tree.column("category", width=150)
        tree.column("price", width=100, anchor="center")
        tree.column("availability", width=100, anchor="center")
        
        # Заполнение данными
        for item in menu_items:
            availability = "Да" if item.get("is_available", True) else "Нет"
            tree.insert("", "end", values=(
                item.get("id", ""),
                item.get("name", ""),
                item.get("category", ""),
                f"{item.get('price', 0)} руб.",
                availability
            ))
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Добавить блюдо", 
            style="Success.TButton",
            command=self.add_dish
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Редактировать", 
            style="Primary.TButton",
            command=lambda: self.edit_dish(tree)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Удалить", 
            style="Danger.TButton",
            command=lambda: self.delete_dish(tree)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Обновить", 
            style="Primary.TButton",
            command=self.show_menu_management
        ).pack(side="right", padx=5)

    def add_dish(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить блюдо")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новое блюдо", font=("Arial", 14)).pack(pady=10)
        
        fields = [
            ("Название", "name"),
            ("Описание", "description"),
            ("Категория", "category"),
            ("Цена", "price"),
            ("Наличие", "is_available")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            frame = ttk.Frame(dialog)
            frame.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(frame, text=label + ":", width=15, anchor="e").pack(side="left")
            
            if field == "is_available":
                var = tk.BooleanVar(value=True)
                check = ttk.Checkbutton(frame, variable=var)
                check.pack(side="left")
                entries[field] = var
            elif field == "description":
                entry = tk.Text(frame, height=4, width=30)
                entry.pack(side="left", fill="x", expand=True)
                entries[field] = entry
            else:
                entry = ttk.Entry(frame, width=30)
                entry.pack(side="left", fill="x", expand=True)
                entries[field] = entry
        
        def save_dish():
            dish_data = {}
            for field, entry in entries.items():
                if isinstance(entry, tk.BooleanVar):
                    dish_data[field] = entry.get()
                elif isinstance(entry, tk.Text):
                    dish_data[field] = entry.get("1.0", "end-1c")
                else:
                    dish_data[field] = entry.get()
            
            try:
                # Преобразуем цену в число
                dish_data["price"] = float(dish_data["price"])
                
                # Добавляем блюдо в базу
                supabase.table("menu").insert(dish_data).execute()
                messagebox.showinfo("Успех", "Блюдо успешно добавлено!")
                dialog.destroy()
                self.show_menu_management()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить блюдо: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_dish).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=20)

    def edit_dish(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для редактирования")
            return
        
        item = tree.item(selected[0])
        dish_id = item['values'][0]
        
        # Получаем данные о блюде из базы
        try:
            response = supabase.table("menu").select("*").eq("id", dish_id).execute()
            dish = response.data[0] if response.data else None
            
            if not dish:
                messagebox.showerror("Ошибка", "Блюдо не найдено")
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать блюдо")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Редактирование блюда", font=("Arial", 14)).pack(pady=10)
        
        fields = [
            ("Название", "name"),
            ("Описание", "description"),
            ("Категория", "category"),
            ("Цена", "price"),
            ("Наличие", "is_available")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            frame = ttk.Frame(dialog)
            frame.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(frame, text=label + ":", width=15, anchor="e").pack(side="left")
            
            if field == "is_available":
                var = tk.BooleanVar(value=dish.get(field, True))
                check = ttk.Checkbutton(frame, variable=var)
                check.pack(side="left")
                entries[field] = var
            elif field == "description":
                entry = tk.Text(frame, height=4, width=30)
                entry.insert("1.0", dish.get(field, ""))
                entry.pack(side="left", fill="x", expand=True)
                entries[field] = entry
            else:
                entry = ttk.Entry(frame, width=30)
                entry.insert(0, str(dish.get(field, "")))
                entry.pack(side="left", fill="x", expand=True)
                entries[field] = entry
        
        def save_changes():
            dish_data = {"id": dish_id}
            for field, entry in entries.items():
                if isinstance(entry, tk.BooleanVar):
                    dish_data[field] = entry.get()
                elif isinstance(entry, tk.Text):
                    dish_data[field] = entry.get("1.0", "end-1c")
                else:
                    dish_data[field] = entry.get()
            
            try:
                # Преобразуем цену в число
                dish_data["price"] = float(dish_data["price"])
                
                # Обновляем блюдо в базе
                supabase.table("menu").update(dish_data).eq("id", dish_id).execute()
                messagebox.showinfo("Успех", "Изменения сохранены!")
                dialog.destroy()
                self.show_menu_management()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_changes).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=20)

    def delete_dish(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо для удаления")
            return
        
        item = tree.item(selected[0])
        dish_id = item['values'][0]
        dish_name = item['values'][1]
        
        if not messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить блюдо '{dish_name}'?"):
            return
        
        try:
            # Удаляем блюдо из базы
            supabase.table("menu").delete().eq("id", dish_id).execute()
            messagebox.showinfo("Успех", "Блюдо успешно удалено")
            self.show_menu_management()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить блюдо: {str(e)}")

    def show_statistics(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Статистика ресторана", style="Title.TLabel").pack(pady=(0, 20))
        
        # Вкладки
        notebook = ttk.Notebook(main_frame)
        
        # Вкладка продаж
        sales_frame = ttk.Frame(notebook, style="Content.TFrame")
        notebook.add(sales_frame, text="Продажи")
        
        # Получаем данные о продажах
        try:
            response = supabase.table("dish_sales_comparison").select("*").execute()
            sales_data = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику продаж: {str(e)}")
            sales_data = []
        
        # Таблица продаж
        columns = ("category", "dish_name", "current_qty", "previous_qty", "difference")
        tree = ttk.Treeview(sales_frame, columns=columns, show="headings", height=15)
        
        tree.heading("category", text="Категория")
        tree.heading("dish_name", text="Блюдо")
        tree.heading("current_qty", text="Текущий месяц")
        tree.heading("previous_qty", text="Прошлый месяц")
        tree.heading("difference", text="Разница")
        
        for item in sales_data:
            tree.insert("", "end", values=(
                item.get("category", ""),
                item.get("dish_name", ""),
                item.get("current_qty", 0),
                item.get("previous_qty", 0),
                item.get("difference", 0)
            ))
        
        tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Вкладка бронирований
        bookings_frame = ttk.Frame(notebook, style="Content.TFrame")
        notebook.add(bookings_frame, text="Бронирования")
        
        # Получаем данные о бронированиях
        try:
            response = supabase.table("reservations").select("*, tables(number), profiles(full_name)").execute()
            reservations = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {str(e)}")
            reservations = []
        
        # Таблица бронирований
        columns = ("id", "table", "date", "time", "guests", "client", "status")
        res_tree = ttk.Treeview(bookings_frame, columns=columns, show="headings", height=15)
        
        res_tree.heading("id", text="ID")
        res_tree.heading("table", text="Стол")
        res_tree.heading("date", text="Дата")
        res_tree.heading("time", text="Время")
        res_tree.heading("guests", text="Гости")
        res_tree.heading("client", text="Клиент")
        res_tree.heading("status", text="Статус")
        
        for res in reservations:
            start_time = datetime.datetime.strptime(res["start_time"], "%Y-%m-%dT%H:%M:%S")
            res_tree.insert("", "end", values=(
                res["id"],
                res["tables"]["number"],
                start_time.strftime("%d.%m.%Y"),
                start_time.strftime("%H:%M"),
                res["guests_count"],
                res["profiles"]["full_name"],
                res["status"]
            ))
        
        res_tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        notebook.pack(fill="both", expand=True)

    def show_reservations(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление бронированиями", style="Title.TLabel").pack(pady=(0, 20))
        
        # Получаем данные о столах
        try:
            tables_response = supabase.table("tables").select("*").execute()
            tables = tables_response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить столы: {str(e)}")
            tables = []
        
        # Получаем текущие бронирования
        try:
            reservations_response = supabase.table("reservations").select("*, tables(number), profiles(full_name)").execute()
            reservations = reservations_response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {str(e)}")
            reservations = []
        
        # Форма нового бронирования
        form_frame = ttk.Frame(main_frame, style="Content.TFrame")
        form_frame.pack(fill="x", pady=20)
        
        ttk.Label(form_frame, text="Новое бронирование", style="Subtitle.TLabel").grid(row=0, column=0, columnspan=4, pady=10)
        
        # Поля формы
        ttk.Label(form_frame, text="Стол:", style="Subtitle.TLabel").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.table_var = tk.StringVar()
        table_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.table_var,
            values=[f"{t['number']} (мест: {t['capacity']})" for t in tables],
            state="readonly",
            width=25
        )
        table_combo.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Дата:", style="Subtitle.TLabel").grid(row=1, column=2, sticky="e", padx=10, pady=5)
        self.date_entry = ttk.Entry(form_frame, width=15)
        self.date_entry.grid(row=1, column=3, padx=10, pady=5)
        self.date_entry.insert(0, datetime.date.today().strftime("%d.%m.%Y"))
        
        ttk.Label(form_frame, text="Время:", style="Subtitle.TLabel").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.time_entry = ttk.Entry(form_frame, width=15)
        self.time_entry.grid(row=2, column=1, padx=10, pady=5)
        self.time_entry.insert(0, "19:00")
        
        ttk.Label(form_frame, text="Кол-во гостей:", style="Subtitle.TLabel").grid(row=2, column=2, sticky="e", padx=10, pady=5)
        self.guests_entry = ttk.Entry(form_frame, width=15)
        self.guests_entry.grid(row=2, column=3, padx=10, pady=5)
        self.guests_entry.insert(0, "2")
        
        ttk.Label(form_frame, text="Клиент:", style="Subtitle.TLabel").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.client_entry = ttk.Entry(form_frame, width=25)
        self.client_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Button(
            form_frame, 
            text="Забронировать", 
            style="Success.TButton",
            command=self.create_reservation
        ).grid(row=3, column=2, columnspan=2, pady=10)
        
        # Список текущих бронирований
        list_frame = ttk.Frame(main_frame, style="Content.TFrame")
        list_frame.pack(fill="both", expand=True)
        
        ttk.Label(list_frame, text="Текущие бронирования", style="Subtitle.TLabel").pack(pady=10)
        
        columns = ("id", "table", "date", "time", "guests", "client", "status")
        self.reservations_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.reservations_tree.heading("id", text="ID")
        self.reservations_tree.heading("table", text="Стол")
        self.reservations_tree.heading("date", text="Дата")
        self.reservations_tree.heading("time", text="Время")
        self.reservations_tree.heading("guests", text="Гости")
        self.reservations_tree.heading("client", text="Клиент")
        self.reservations_tree.heading("status", text="Статус")
        
        self.reservations_tree.column("id", width=50, anchor="center")
        self.reservations_tree.column("table", width=80)
        self.reservations_tree.column("date", width=100)
        self.reservations_tree.column("time", width=80)
        self.reservations_tree.column("guests", width=80, anchor="center")
        self.reservations_tree.column("client", width=150)
        self.reservations_tree.column("status", width=100)
        
        # Заполняем таблицу данными
        for res in reservations:
            start_time = datetime.datetime.strptime(res["start_time"], "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.datetime.strptime(res["end_time"], "%Y-%m-%dT%H:%M:%S")
            
            self.reservations_tree.insert("", "end", values=(
                res["id"],
                res["tables"]["number"],
                start_time.strftime("%d.%m.%Y"),
                f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
                res["guests_count"],
                res["profiles"]["full_name"],
                res["status"]
            ), tags=(res["status"],))
        
        # Настраиваем цвета для разных статусов
        self.reservations_tree.tag_configure("active", background="#d4edda")
        self.reservations_tree.tag_configure("cancelled", background="#f8d7da")
        self.reservations_tree.tag_configure("completed", background="#e2e3e5")
        
        self.reservations_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Подтвердить", 
            style="Primary.TButton",
            command=lambda: self.update_reservation_status("active")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Отменить", 
            style="Danger.TButton",
            command=lambda: self.update_reservation_status("cancelled")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Завершить", 
            style="Success.TButton",
            command=lambda: self.update_reservation_status("completed")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Обновить", 
            style="Primary.TButton",
            command=self.show_reservations
        ).pack(side="right", padx=5)

    def create_reservation(self):
        try:
            table_str = self.table_var.get()
            if not table_str:
                messagebox.showerror("Ошибка", "Выберите стол")
                return
                
            table_number = table_str.split()[0]
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            guests = int(self.guests_entry.get())
            client = self.client_entry.get()
            
            # Получаем ID стола
            table_response = supabase.table("tables").select("id, capacity").eq("number", table_number).execute()
            if not table_response.data:
                messagebox.showerror("Ошибка", "Стол не найден")
                return
                
            table_id = table_response.data[0]["id"]
            table_capacity = table_response.data[0]["capacity"]
            
            if guests > table_capacity:
                messagebox.showerror("Ошибка", f"Стол вмещает только {table_capacity} гостей")
                return
                
            # Преобразуем дату и время
            start_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            end_time = start_time + datetime.timedelta(hours=2)
            
            # Проверяем доступность стола
            try:
                # Получаем все активные бронирования для этого стола
                response = supabase.table("reservations") \
                .select("*") \
                .eq("table_id", table_id) \
                .eq("status", "active") \
                .execute()

                # Проверяем пересечения по времени
                for reservation in response.data:
                    existing_start = datetime.datetime.strptime(reservation["start_time"], "%Y-%m-%dT%H:%M:%S")
                    existing_end = datetime.datetime.strptime(reservation["end_time"], "%Y-%m-%dT%H:%M:%S")
                    
                    # Проверяем пересечение временных интервалов
                    if (start_time < existing_end) and (end_time > existing_start):
                        messagebox.showerror("Ошибка", f"Стол уже забронирован на это время ({existing_start.strftime('%H:%M')}-{existing_end.strftime('%H:%M')})")
                        return
            
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка проверки доступности стола: {str(e)}")
                return
                
            # Получаем ID клиента (если клиент новый, создаем профиль)
            if "@" in client:  # Если введен email
                try:
                    # Проверяем, есть ли пользователь
                    user_response = supabase.table("profiles").select("id").eq("email", client).execute()
                    if user_response.data:
                        user_id = user_response.data[0]["id"]
                    else:
                        # Создаем временного пользователя
                        temp_user = {
                            "email": client,
                            "full_name": client.split("@")[0],
                            "role": "client"
                        }
                        insert_response = supabase.table("profiles").insert(temp_user).execute()
                        user_id = insert_response.data[0]["id"]
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать профиль клиента: {str(e)}")
                    return
            else:
                # Для анонимных бронирований используем текущего пользователя
                user_id = self.current_user.id
            
            # Создаем бронирование
            reservation_data = {
                "table_id": table_id,
                "user_id": user_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "guests_count": guests,
                "status": "active"
            }
            
            supabase.table("reservations").insert(reservation_data).execute()
            messagebox.showinfo("Успех", "Бронирование успешно создано!")
            self.show_reservations()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать бронирование: {str(e)}")

    def update_reservation_status(self, new_status):
        selected = self.reservations_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование")
            return
            
        item = self.reservations_tree.item(selected[0])
        reservation_id = item['values'][0]
        
        try:
            supabase.table("reservations").update({"status": new_status}).eq("id", reservation_id).execute()
            messagebox.showinfo("Успех", "Статус бронирования обновлен")
            self.show_reservations()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус: {str(e)}")

    def create_order(self):
        # Сначала получаем список активных бронирований
        try:
            response = supabase.table("reservations").select("*, tables(number)").eq("status", "active").execute()
            reservations = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {str(e)}")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Создать заказ")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новый заказ", font=("Arial", 14)).pack(pady=10)
        
        # Выбор бронирования
        reservation_frame = ttk.Frame(dialog)
        reservation_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(reservation_frame, text="Бронирование:").pack(side="left")
        self.reservation_var = tk.StringVar()
        reservation_combo = ttk.Combobox(
            reservation_frame, 
            textvariable=self.reservation_var,
            values=[f"{r['id']} - Стол {r['tables']['number']} ({r['guests_count']} чел.)" for r in reservations],
            state="readonly",
            width=50
        )
        reservation_combo.pack(side="left", padx=10)
        
        # Меню
        menu_frame = ttk.Frame(dialog)
        menu_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Получаем меню
        try:
            menu_response = supabase.table("menu").select("*").eq("is_available", True).execute()
            menu_items = menu_response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить меню: {str(e)}")
            dialog.destroy()
            return
        
        # Таблица меню
        columns = ("id", "name", "category", "price")
        self.menu_tree = ttk.Treeview(menu_frame, columns=columns, show="headings", height=10)
        
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Название")
        self.menu_tree.heading("category", text="Категория")
        self.menu_tree.heading("price", text="Цена")
        
        for item in menu_items:
            self.menu_tree.insert("", "end", values=(
                item["id"],
                item["name"],
                item["category"],
                f"{item['price']} руб."
            ))
        
        self.menu_tree.pack(side="left", fill="both", expand=True)
        
        # Кнопки добавления/удаления
        btn_frame = ttk.Frame(menu_frame)
        btn_frame.pack(side="left", fill="y", padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Добавить →", 
            command=lambda: self.add_to_order(self.menu_tree, self.order_tree)
        ).pack(pady=5)
        
        ttk.Button(
            btn_frame, 
            text="← Удалить", 
            command=lambda: self.remove_from_order(self.order_tree)
        ).pack(pady=5)
        
        # Текущий заказ
        order_frame = ttk.Frame(dialog)
        order_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(order_frame, text="Текущий заказ:").pack(anchor="w")
        
        columns = ("id", "name", "price", "quantity", "sum")
        self.order_tree = ttk.Treeview(order_frame, columns=columns, show="headings", height=5)
        
        self.order_tree.heading("id", text="ID")
        self.order_tree.heading("name", text="Название")
        self.order_tree.heading("price", text="Цена")
        self.order_tree.heading("quantity", text="Кол-во")
        self.order_tree.heading("sum", text="Сумма")
        
        self.order_tree.pack(fill="both", expand=True)
        
        # Итого
        total_frame = ttk.Frame(dialog)
        total_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(total_frame, text="Итого:").pack(side="left")
        self.total_var = tk.StringVar(value="0 руб.")
        ttk.Label(total_frame, textvariable=self.total_var, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Сохранить заказ", 
            style="Success.TButton",
            command=lambda: self.save_order(dialog)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Отмена", 
            style="Danger.TButton",
            command=dialog.destroy
        ).pack(side="right", padx=5)
        
        # Обновляем итоговую сумму при изменении заказа
        self.order_tree.bind("<<TreeviewSelect>>", self.update_total)

    def add_to_order(self, source_tree, target_tree):
        selected = source_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо из меню")
            return
            
        item = source_tree.item(selected[0])
        values = item['values']
        
        # Проверяем, есть ли уже это блюдо в заказе
        for child in target_tree.get_children():
            if target_tree.item(child)['values'][0] == values[0]:
                # Увеличиваем количество
                current_values = target_tree.item(child)['values']
                new_quantity = int(current_values[3]) + 1
                new_sum = float(current_values[2]) * new_quantity
                target_tree.item(child, values=(
                    current_values[0],
                    current_values[1],
                    current_values[2],
                    new_quantity,
                    f"{new_sum:.2f} руб."
                ))
                self.update_total()
                return
                
        # Добавляем новое блюдо в заказ
        target_tree.insert("", "end", values=(
            values[0],  # ID
            values[1],  # Название
            values[3].replace(" руб.", ""),  # Цена (без "руб.")
            1,  # Количество
            values[3]  # Сумма (равна цене для 1 порции)
        ))
        
        self.update_total()

    def remove_from_order(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо из заказа")
            return
            
        for item in selected:
            tree.delete(item)
            
        self.update_total()

    def update_total(self, event=None):
        total = 0.0
        for child in self.order_tree.get_children():
            values = self.order_tree.item(child)['values']
            total += float(values[4].replace(" руб.", ""))
            
        self.total_var.set(f"{total:.2f} руб.")

    def save_order(self, dialog):
        if not self.reservation_var.get():
            messagebox.showerror("Ошибка", "Выберите бронирование")
            return
            
        if not self.order_tree.get_children():
            messagebox.showerror("Ошибка", "Добавьте блюда в заказ")
            return
            
        try:
            # Получаем ID бронирования
            reservation_id = int(self.reservation_var.get().split()[0])
            
            # Создаем заказ
            order_data = {
                "reservation_id": reservation_id,
                "waiter_id": self.current_user.id,
                "status": "placed"
            }
            
            order_response = supabase.table("orders").insert(order_data).execute()
            order_id = order_response.data[0]["id"]
            
            # Добавляем позиции заказа
            for child in self.order_tree.get_children():
                values = self.order_tree.item(child)['values']
                
                order_item = {
                    "order_id": order_id,
                    "menu_item_id": values[0],
                    "quantity": values[3],
                    "price_at_order": values[2]
                }
                
                supabase.table("order_items").insert(order_item).execute()
            
            messagebox.showinfo("Успех", "Заказ успешно создан!")
            dialog.destroy()
            self.show_current_orders()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заказ: {str(e)}")

    def show_current_orders(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Текущие заказы", style="Title.TLabel").pack(pady=(0, 20))
        
        try:
            # Исправленный запрос с явным указанием связей
            response = supabase.table("orders").select(
                """*,
                reservations!orders_reservation_id_fkey (
                    tables!reservations_table_id_fkey ( number ),
                    profiles!reservations_user_id_fkey ( full_name )
                ),
                profiles!orders_waiter_id_fkey ( full_name )"""
            ).order("created_at", desc=True).execute()
            
            orders = response.data
            
            # Таблица заказов
            columns = ("id", "table", "waiter", "created", "status", "total")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
            
            # Настройка столбцов
            tree.heading("id", text="ID")
            tree.heading("table", text="Стол")
            tree.heading("waiter", text="Официант")
            tree.heading("created", text="Создан")
            tree.heading("status", text="Статус")
            tree.heading("total", text="Сумма")
            
            for order in orders:
                # Обработка даты
                try:
                    created_at = datetime.datetime.fromisoformat(order["created_at"])
                except:
                    created_at = datetime.datetime.now()
                
                # Получение суммы заказа
                total = 0
                try:
                    items = supabase.table("order_items").select("price_at_order, quantity").eq("order_id", order["id"]).execute().data
                    total = sum(item["price_at_order"] * item["quantity"] for item in items)
                except Exception as e:
                    print(f"Ошибка расчета суммы: {e}")
                
                # Получение данных о столе и официанте
                table_number = "-"
                if order.get("reservations") and order["reservations"].get("tables"):
                    table_number = order["reservations"]["tables"].get("number", "-")
                
                waiter_name = "-"
                if order.get("profiles"):
                    waiter_name = order["profiles"].get("full_name", "-")
                
                # Добавление строки в таблицу
                tree.insert("", "end", values=(
                    order["id"],
                    table_number,
                    waiter_name,
                    created_at.strftime("%d.%m.%Y %H:%M"),
                    order["status"],
                    f"{total:.2f} руб."
                ), tags=(order["status"],))
            
            # Настройка цветов статусов
            status_colors = {
                "draft": "#e2e3e5",
                "placed": "#fff3cd",
                "preparing": "#cce5ff",
                "ready": "#d4edda",
                "served": "#d1ecf1",
                "closed": "#d4edda"
            }
            for status, color in status_colors.items():
                tree.tag_configure(status, background=color)
            
            tree.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Кнопки управления
            btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
            btn_frame.pack(fill="x", pady=10)
            
            ttk.Button(
                btn_frame, 
                text="Просмотреть", 
                style="Primary.TButton",
                command=lambda: self.view_order_details(tree)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Изменить статус", 
                style="Primary.TButton",
                command=lambda: self.change_order_status(tree)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Создать счет", 
                style="Success.TButton",
                command=lambda: self.create_bill(tree)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Обновить", 
                style="Primary.TButton",
                command=self.show_current_orders
            ).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {str(e)}")

    def view_order_details(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
            
        item = tree.item(selected[0])
        order_id = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Детали заказа №{order_id}")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Получаем детали заказа
        try:
            order_response = supabase.table("orders").select("*, reservations(tables(number), profiles(full_name))").eq("id", order_id).execute()
            order = order_response.data[0]
            
            items_response = supabase.table("order_items").select("*, menu(name)").eq("order_id", order_id).execute()
            items = items_response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить детали заказа: {str(e)}")
            dialog.destroy()
            return
        
        # Информация о заказе
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"Заказ №{order_id}", font=("Arial", 14)).pack(anchor="w")
        ttk.Label(info_frame, text=f"Стол: {order['reservations']['tables']['number']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Клиент: {order['reservations']['profiles']['full_name']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Статус: {order['status']}").pack(anchor="w")
        
        # Позиции заказа
        items_frame = ttk.Frame(dialog)
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("name", "price", "quantity", "sum")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=10)
        
        items_tree.heading("name", text="Блюдо")
        items_tree.heading("price", text="Цена")
        items_tree.heading("quantity", text="Кол-во")
        items_tree.heading("sum", text="Сумма")
        
        total = 0
        for item in items:
            sum_item = item["price_at_order"] * item["quantity"]
            total += sum_item
            items_tree.insert("", "end", values=(
                item["menu"]["name"],
                f"{item['price_at_order']:.2f} руб.",
                item["quantity"],
                f"{sum_item:.2f} руб."
            ))
        
        items_tree.pack(fill="both", expand=True)
        
        # Итого
        total_frame = ttk.Frame(dialog)
        total_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(total_frame, text="Итого:", font=("Arial", 12)).pack(side="left")
        ttk.Label(total_frame, text=f"{total:.2f} руб.", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        
        # Кнопка закрытия
        ttk.Button(
            dialog, 
            text="Закрыть", 
            command=dialog.destroy
        ).pack(pady=10)

    def change_order_status(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
            
        item = tree.item(selected[0])
        order_id = item['values'][0]
        current_status = item['tags'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить статус заказа")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новый статус:", font=("Arial", 12)).pack(pady=10)
        
        status_var = tk.StringVar(value=current_status)
        statuses = ["placed", "preparing", "ready", "served", "closed"]
        
        for status in statuses:
            if statuses.index(status) > statuses.index(current_status):
                ttk.Radiobutton(
                    dialog, 
                    text=status, 
                    variable=status_var, 
                    value=status
                ).pack(anchor="w", padx=20)
        
        def save_status():
            new_status = status_var.get()
            try:
                supabase.table("orders").update({"status": new_status}).eq("id", order_id).execute()
                messagebox.showinfo("Успех", "Статус заказа обновлен")
                dialog.destroy()
                self.show_current_orders()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить статус: {str(e)}")
        
        ttk.Button(
            dialog, 
            text="Сохранить", 
            command=save_status
        ).pack(pady=10)

    def create_bill(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
            
        item = tree.item(selected[0])
        order_id = item['values'][0]
        
        # Проверяем, не создан ли уже счет
        try:
            bill_response = supabase.table("bills").select("*").eq("order_id", order_id).execute()
            if bill_response.data:
                # Если счет уже существует, спрашиваем, что делать
                if messagebox.askyesno("Счет уже существует", 
                                      "Счет для этого заказа уже создан. Хотите перейти к управлению счетами?"):
                    self.show_bills()
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить счета: {str(e)}")
            return
        
        # Получаем сумму заказа
        try:
            items_response = supabase.table("order_items").select("*").eq("order_id", order_id).execute()
            total = sum(item["price_at_order"] * item["quantity"] for item in items_response.data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось рассчитать сумму: {str(e)}")
            return
        
        # Создаем счет
        try:
            bill_data = {
                "order_id": order_id,
                "total_amount": total,
                "payment_status": "pending"
            }
            
            supabase.table("bills").insert(bill_data).execute()
            
            # Обновляем статус заказа
            supabase.table("orders").update({"status": "closed"}).eq("id", order_id).execute()
            
            messagebox.showinfo("Успех", "Счет успешно создан")
            self.show_current_orders()
            self.show_bills()
        except Exception as e:
            if '23505' in str(e):  # Код ошибки дубликата
                messagebox.showwarning("Предупреждение", "Счет для этого заказа уже существует")
            else:
                messagebox.showerror("Ошибка", f"Не удалось создать счет: {str(e)}")

    def show_bills(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление счетами", style="Title.TLabel").pack(pady=(0, 20))
        
        try:
            # Исправленный запрос
            response = supabase.table("bills").select(
                """*,
                orders (
                    reservations (
                        tables ( number )
                    ),
                    profiles!orders_waiter_id_fkey ( full_name )
                )"""
            ).order("id", desc=True).execute()
            
            bills = response.data
            
            # Таблица счетов
            columns = ("id", "order", "table", "waiter", "amount", "status")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
            
            tree.heading("id", text="ID")
            tree.heading("order", text="Заказ")
            tree.heading("table", text="Стол")
            tree.heading("waiter", text="Официант")
            tree.heading("amount", text="Сумма")
            tree.heading("status", text="Статус")
            
            # Настройка столбцов
            tree.column("id", width=50, anchor="center")
            tree.column("order", width=80, anchor="center")
            tree.column("table", width=80, anchor="center")
            tree.column("waiter", width=150)
            tree.column("amount", width=100, anchor="center")
            tree.column("status", width=100, anchor="center")
            
            for bill in bills:
                order = bill.get("orders", {})
                table_number = "-"
                waiter_name = "-"
                
                if order:
                    # Получаем номер стола
                    if order.get("reservations") and order["reservations"].get("tables"):
                        table_number = order["reservations"]["tables"].get("number", "-")
                    
                    # Получаем имя официанта
                    if order.get("profiles"):
                        waiter_name = order["profiles"].get("full_name", "-")
                
                tree.insert("", "end", values=(
                    bill["id"],
                    order.get("id", "-") if order else "-",
                    table_number,
                    waiter_name,
                    f"{bill['total_amount']:.2f} руб.",
                    bill["payment_status"]
                ), tags=(bill["payment_status"],))
            
            # Настраиваем цвета для разных статусов
            tree.tag_configure("pending", background="#fff3cd")
            tree.tag_configure("paid", background="#d4edda")
            tree.tag_configure("refunded", background="#f8d7da")
            
            tree.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Кнопки управления
            btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
            btn_frame.pack(fill="x", pady=10)
            
            ttk.Button(
                btn_frame, 
                text="Отметить как оплаченный", 
                style="Success.TButton",
                command=lambda: self.update_bill_status(tree, "paid")
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Возврат", 
                style="Danger.TButton",
                command=lambda: self.update_bill_status(tree, "refunded")
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Печать", 
                style="Primary.TButton",
                command=lambda: self.print_bill(tree)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Обновить", 
                style="Primary.TButton",
                command=self.show_bills
            ).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить счета: {str(e)}")

    def update_bill_status(self, tree, new_status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите счет")
            return
            
        item = tree.item(selected[0])
        bill_id = item['values'][0]
        
        try:
            update_data = {"payment_status": new_status}
            
            if new_status == "paid":
                update_data["payment_date"] = datetime.datetime.now().isoformat()
            
            supabase.table("bills").update(update_data).eq("id", bill_id).execute()
            
            messagebox.showinfo("Успех", "Статус счета обновлен")
            self.show_bills()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус: {str(e)}")

    def print_bill(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите счет")
            return
            
        item = tree.item(selected[0])
        bill_id = item['values'][0]
        
        try:
            # Исправленный запрос для получения данных о счете
            bill_response = supabase.table("bills").select("*").eq("id", bill_id).execute()
            bill = bill_response.data[0] if bill_response.data else None
            
            if not bill:
                messagebox.showerror("Ошибка", "Счет не найден")
                return
                
            # Получаем данные о заказе
            order_response = supabase.table("orders").select(
                """*,
                reservations!orders_reservation_id_fkey (
                    tables!reservations_table_id_fkey ( number ),
                    profiles!reservations_user_id_fkey ( full_name )
                ),
                order_items!inner (
                    menu!order_items_menu_item_id_fkey ( name ),
                    quantity,
                    price_at_order
                )"""
            ).eq("id", bill["order_id"]).execute()
            
            order = order_response.data[0] if order_response.data else None
            
            if not order:
                messagebox.showerror("Ошибка", "Заказ не найден")
                return
            
            # Формируем текст чека
            bill_text = f"""
            {'ЧЕК РЕСТОРАНА':^40}
            {'='*40}
            Дата: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}
            Счет №: {bill_id}
            Заказ №: {order['id']}
            """
            
            # Добавляем информацию о столе и клиенте
            table_number = "-"
            client_name = "-"
            if order.get("reservations"):
                if order["reservations"].get("tables"):
                    table_number = order["reservations"]["tables"].get("number", "-")
                if order["reservations"].get("profiles"):
                    client_name = order["reservations"]["profiles"].get("full_name", "-")
            
            bill_text += f"Стол: {table_number}\n"
            bill_text += f"Клиент: {client_name}\n"
            bill_text += f"{'-'*40}\n"
            bill_text += "Позиции:\n"
            
            # Добавляем позиции заказа
            total = 0
            for item in order.get("order_items", []):
                name = item.get("menu", {}).get("name", "Неизвестное блюдо")
                quantity = item.get("quantity", 0)
                price = item.get("price_at_order", 0)
                item_total = quantity * price
                total += item_total
                bill_text += f"{name[:30]:<30} {quantity} x {price:.2f} = {item_total:.2f} руб.\n"
            
            bill_text += f"""
            {'-'*40}
            Итого: {total:.2f} руб.
            Статус оплаты: {bill['payment_status']}
            {'='*40}
            Спасибо за посещение!
            """
            
            # Показываем чек в диалоговом окне
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Чек №{bill_id}")
            dialog.geometry("500x600")
            
            text_area = tk.Text(dialog, font=("Courier New", 12))
            text_area.insert("1.0", bill_text)
            text_area.config(state="disabled")
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            
            ttk.Button(
                dialog, 
                text="Печать", 
                style="Primary.TButton",
                command=lambda: self.print_to_printer(bill_text)
            ).pack(pady=10)
            
            ttk.Button(
                dialog, 
                text="Закрыть", 
                style="Danger.TButton",
                command=dialog.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать чек: {str(e)}")

    def print_to_printer(self, text):
        # В реальном приложении здесь был бы код для печати
        # Для демонстрации сохраняем в файл
        try:
            with open(f"чек_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Успех", "Чек сохранен в файл")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить чек: {str(e)}")

    def show_kitchen_orders(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Заказы на кухне", style="Title.TLabel").pack(pady=(0, 20))
        
        try:
            # 1. Получаем заказы со статусом preparing
            orders_response = supabase.table("orders")\
                .select("id, created_at, reservations(tables(number))")\
                .eq("status", "preparing")\
                .order("created_at", desc=False)\
                .execute()
            
            orders = [order for order in orders_response.data if order.get('id')]
            print(f"DEBUG: Найдено заказов: {orders}")  # Вывод всех данных заказов
            
            if orders:
                # 2. Получаем все позиции для этих заказов
                order_ids = [str(order['id']) for order in orders if order.get('id')]
                items_response = supabase.table("order_items")\
                    .select("id, order_id, quantity, menu(name), cooked_dishes(id)")\
                    .in_("order_id", order_ids)\
                    .execute()
                
                items = items_response.data
                print(f"DEBUG: Найдено позиций: {items}")  # Вывод всех данных позиций
                
                # 3. Группируем позиции по заказам с проверкой данных
                from collections import defaultdict
                items_by_order = defaultdict(list)
                for item in items:
                    if item.get('order_id'):
                        items_by_order[item['order_id']].append({
                            'id': item.get('id'),
                            'quantity': item.get('quantity', 0),
                            'menu': item.get('menu', {}),
                            'cooked_dishes': item.get('cooked_dishes', [])
                        })
                
                # 4. Формируем полные данные заказов с проверкой
                processed_orders = []
                for order in orders:
                    # Безопасное получение номера стола
                    table_number = '?'
                    if order.get('reservations') and isinstance(order['reservations'], dict):
                        tables = order['reservations'].get('tables', {})
                        if isinstance(tables, dict):
                            table_number = tables.get('number', '?')
                    
                    processed_order = {
                        'id': order['id'],
                        'created_at': order.get('created_at'),
                        'table_number': table_number,
                        'order_items': items_by_order.get(order['id'], [])
                    }
                    processed_orders.append(processed_order)
                
                orders = processed_orders
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {str(e)}")
            orders = []
        
        # Отображение заказов
        if not orders:
            no_orders_frame = ttk.Frame(main_frame, style="Content.TFrame")
            no_orders_frame.pack(pady=50)
            
            ttk.Label(
                no_orders_frame, 
                text="Сейчас нет заказов для приготовления", 
                style="Subtitle.TLabel"
            ).pack(pady=10)
            
            ttk.Button(
                no_orders_frame,
                text="Обновить",
                command=self.show_kitchen_orders,
                style="Primary.TButton"
            ).pack(pady=10)
            return
        
        notebook = ttk.Notebook(main_frame)
        
        for order in orders:
            try:
                if not order.get('id'):
                    continue
                    
                tab_frame = ttk.Frame(notebook, style="Content.TFrame")
                notebook.add(tab_frame, 
                    text=f"Заказ №{order['id']} (Стол {order.get('table_number', '?')})")
                
                # Таблица с блюдами
                tree = ttk.Treeview(tab_frame, 
                    columns=("Блюдо", "Кол-во", "Статус"), 
                    show="headings",
                    height=10)
                
                tree.heading("Блюдо", text="Блюдо")
                tree.heading("Кол-во", text="Кол-во")
                tree.heading("Статус", text="Статус")
                
                for item in order.get('order_items', []):
                    dish_name = item.get('menu', {}).get('name', 'Неизвестное блюдо')
                    quantity = item.get('quantity', 0)
                    is_cooked = len(item.get('cooked_dishes', [])) > 0
                    status = "✓ Готово" if is_cooked else "В процессе"
                    
                    tree.insert("", "end", 
                        values=(dish_name, quantity, status),
                        tags=("cooked" if is_cooked else "cooking"))
                
                tree.tag_configure("cooked", background="#d4edda")
                tree.tag_configure("cooking", background="#fff3cd")
                tree.pack(fill="both", expand=True, padx=20, pady=10)
                
                # Кнопки управления
                btn_frame = ttk.Frame(tab_frame)
                btn_frame.pack(fill="x", pady=10)
                
                ttk.Button(
                    btn_frame,
                    text="Отметить выбранное как готовое",
                    style="Success.TButton",
                    command=lambda t=tree, oid=order['id']: self.mark_as_cooked(t, oid)
                ).pack(side="left", padx=5)
                
                ttk.Button(
                    btn_frame,
                    text="Весь заказ готов",
                    style="Primary.TButton",
                    command=lambda oid=order['id']: self.mark_order_as_ready(oid)
                ).pack(side="left", padx=5)
                
            except Exception as e:
                print(f"Ошибка при отображении заказа {order.get('id')}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def mark_as_cooked(self, tree, order_id):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите блюдо")
            return
            
        item = tree.item(selected[0])
        item_name = item['values'][0]
        
        # Получаем ID позиции заказа
        try:
            response = supabase.table("order_items").select("id").eq("order_id", order_id).execute()
            items = response.data
            item_id = None
            for i in items:
                menu_response = supabase.table("menu").select("name").eq("id", i["menu_item_id"]).execute()
                if menu_response.data[0]["name"] == item_name:
                    item_id = i["id"]
                    break
                    
            if not item_id:
                messagebox.showerror("Ошибка", "Не удалось найти позицию заказа")
                return
                
            # Отмечаем как приготовленное
            cooked_data = {
                "chef_id": self.current_user.id,
                "order_item_id": item_id
            }
            
            supabase.table("cooked_dishes").insert(cooked_data).execute()
            
            # Обновляем статус в таблице
            tree.item(selected[0], values=(
                item['values'][0],
                item['values'][1],
                "Приготовлено"
            ), tags=("Приготовлено",))
            
            messagebox.showinfo("Успех", f"Блюдо '{item_name}' отмечено как готовое")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус: {str(e)}")

    def mark_order_as_ready(self, order_id):
        try:
            # Обновляем статус заказа
            supabase.table("orders").update({"status": "ready"}).eq("id", order_id).execute()
            messagebox.showinfo("Успех", "Заказ отмечен как готовый")
            self.show_kitchen_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус заказа: {str(e)}")

    def show_inventory(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление инвентарем", style="Title.TLabel").pack(pady=(0, 20))
        
        # Получаем данные о запасах
        try:
            response = supabase.table("dish_stock").select("*, menu(name, category)").execute()
            stock_items = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить инвентарь: {str(e)}")
            stock_items = []
        
        # Таблица инвентаря
        columns = ("id", "name", "category", "quantity")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="ID")
        tree.heading("name", text="Блюдо")
        tree.heading("category", text="Категория")
        tree.heading("quantity", text="Кол-во")
        
        for item in stock_items:
            tree.insert("", "end", values=(
                item["menu_item_id"],
                item["menu"]["name"],
                item["menu"]["category"],
                item["quantity"]
            ))
        
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Добавить запасы", 
            style="Success.TButton",
            command=lambda: self.update_inventory(tree, "add")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Списать запасы", 
            style="Danger.TButton",
            command=lambda: self.update_inventory(tree, "remove")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Обновить", 
            style="Primary.TButton",
            command=self.show_inventory
        ).pack(side="right", padx=5)

    def update_inventory(self, tree, action):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите позицию")
            return
            
        item = tree.item(selected[0])
        item_id = item['values'][0]
        current_qty = int(item['values'][3])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить количество" if action == "add" else "Списать запасы")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Текущее количество: {current_qty}").pack(pady=10)
        
        ttk.Label(dialog, text="Количество:").pack()
        qty_entry = ttk.Entry(dialog)
        qty_entry.pack(pady=5)
        qty_entry.focus()
        
        def save_changes():
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("Ошибка", "Введите положительное число")
                    return
                    
                if action == "add":
                    new_qty = current_qty + qty
                else:
                    new_qty = current_qty - qty
                    if new_qty < 0:
                        messagebox.showerror("Ошибка", "Недостаточно запасов")
                        return
                        
                supabase.table("dish_stock").update({"quantity": new_qty}).eq("menu_item_id", item_id).execute()
                messagebox.showinfo("Успех", "Количество обновлено")
                dialog.destroy()
                self.show_inventory()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить количество: {str(e)}")
        
        ttk.Button(
            dialog, 
            text="Сохранить", 
            command=save_changes
        ).pack(pady=10)

    def show_tables_management(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление столами", style="Title.TLabel").pack(pady=(0, 20))
        
        # Получаем данные о столах
        try:
            response = supabase.table("tables").select("*").execute()
            tables = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить столы: {str(e)}")
            tables = []
        
        # Таблица столов
        columns = ("id", "number", "capacity", "status")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="ID")
        tree.heading("number", text="Номер")
        tree.heading("capacity", text="Вместимость")
        tree.heading("status", text="Статус")
        
        for table in tables:
            tree.insert("", "end", values=(
                table["id"],
                table["number"],
                table["capacity"],
                table["status"]
            ), tags=(table["status"],))
        
        # Настраиваем цвета для разных статусов
        tree.tag_configure("free", background="#d4edda")
        tree.tag_configure("booked", background="#fff3cd")
        tree.tag_configure("occupied", background="#f8d7da")
        
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame, style="Content.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Добавить стол", 
            style="Success.TButton",
            command=self.add_table
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Редактировать", 
            style="Primary.TButton",
            command=lambda: self.edit_table(tree)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Удалить", 
            style="Danger.TButton",
            command=lambda: self.delete_table(tree)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Обновить", 
            style="Primary.TButton",
            command=self.show_tables_management
        ).pack(side="right", padx=5)

    def add_table(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить стол")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новый стол", font=("Arial", 14)).pack(pady=10)
        
        fields = [
            ("Номер стола:", "number"),
            ("Вместимость:", "capacity"),
            ("Статус:", "status")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            frame = ttk.Frame(dialog)
            frame.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(frame, text=label, width=15, anchor="e").pack(side="left")
            
            if field == "status":
                status_var = tk.StringVar(value="free")
                status_combo = ttk.Combobox(
                    frame, 
                    textvariable=status_var,
                    values=["free", "booked", "occupied"],
                    state="readonly",
                    width=17
                )
                status_combo.pack(side="left")
                entries[field] = status_var
            else:
                entry = ttk.Entry(frame, width=20)
                entry.pack(side="left")
                entries[field] = entry
        
        def save_table():
            table_data = {}
            for field, entry in entries.items():
                if isinstance(entry, tk.StringVar):
                    table_data[field] = entry.get()
                else:
                    table_data[field] = entry.get()
            
            try:
                table_data["capacity"] = int(table_data["capacity"])
                
                supabase.table("tables").insert(table_data).execute()
                messagebox.showinfo("Успех", "Стол успешно добавлен!")
                dialog.destroy()
                self.show_tables_management()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную вместимость")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить стол: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_table).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=20)

    def edit_table(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол")
            return
            
        item = tree.item(selected[0])
        table_id = item['values'][0]
        
        # Получаем данные о столе
        try:
            response = supabase.table("tables").select("*").eq("id", table_id).execute()
            table = response.data[0]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать стол")
        dialog.geometry("1920x1080")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Редактирование стола", font=("Arial", 14)).pack(pady=10)
        
        fields = [
            ("Номер стола:", "number"),
            ("Вместимость:", "capacity"),
            ("Статус:", "status")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            frame = ttk.Frame(dialog)
            frame.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(frame, text=label, width=15, anchor="e").pack(side="left")
            
            if field == "status":
                status_var = tk.StringVar(value=table["status"])
                status_combo = ttk.Combobox(
                    frame, 
                    textvariable=status_var,
                    values=["free", "booked", "occupied"],
                    state="readonly",
                    width=17
                )
                status_combo.pack(side="left")
                entries[field] = status_var
            else:
                entry = ttk.Entry(frame, width=20)
                entry.insert(0, str(table[field]))
                entry.pack(side="left")
                entries[field] = entry
        
        def save_changes():
            table_data = {"id": table_id}
            for field, entry in entries.items():
                if isinstance(entry, tk.StringVar):
                    table_data[field] = entry.get()
                else:
                    table_data[field] = entry.get()
            
            try:
                table_data["capacity"] = int(table_data["capacity"])
                
                supabase.table("tables").update(table_data).eq("id", table_id).execute()
                messagebox.showinfo("Успех", "Изменения сохранены!")
                dialog.destroy()
                self.show_tables_management()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную вместимость")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_changes).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=20)

    def delete_table(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол")
            return
            
        item = tree.item(selected[0])
        table_id = item['values'][0]
        table_number = item['values'][1]
        
        if not messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить стол №{table_number}?"):
            return
        
        try:
            # Проверяем, есть ли активные бронирования
            reservations_response = supabase.table("reservations").select("*").eq("table_id", table_id).eq("status", "active").execute()
            if reservations_response.data:
                messagebox.showerror("Ошибка", "Нельзя удалить стол с активными бронированиями")
                return
                
            supabase.table("tables").delete().eq("id", table_id).execute()
            messagebox.showinfo("Успех", "Стол успешно удален")
            self.show_tables_management()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить стол: {str(e)}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()
