import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from supabase import create_client
import datetime
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re  # Добавьте в импорты

# Настройки подключения к Supabase
SUPABASE_URL = "https://pyryfmngwdalgngvocry.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5cnlmbW5nd2RhbGduZ3ZvY3J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMzM5NDIsImV4cCI6MjA2NjYwOTk0Mn0.iXHNSauBxf2QlLFJbZ7dDsGtbvzaLHBq_FQ6tlH0W4I"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class RestaurantClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ресторан: Клиентский портал")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        self.current_user = None
        self.current_profile = None
        self.selected_table = None  # Для хранения выбранного стола
        self.setup_styles()
        self.show_welcome_page()

    def setup_styles(self):
        self.style = ttk.Style()
        
        # Цветовая схема
        self.bg_color = "#f8f9fa"
        self.header_color = "#343a40"
        self.accent_color = "#6c757d"
        self.primary_color = "#0d6efd"
        self.success_color = "#198754"
        self.warning_color = "#ffc107"
        self.danger_color = "#dc3545"
        
        # Настройка стилей
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Header.TFrame", background=self.header_color)
        self.style.configure("Title.TLabel", background=self.bg_color, 
                            foreground="#212529", font=("Arial", 24, "bold"))
        self.style.configure("Subtitle.TLabel", background=self.bg_color, 
                            foreground="#495057", font=("Arial", 14))
        self.style.configure("Card.TFrame", background="white", relief="solid", 
                            borderwidth=1, bordercolor="#dee2e6")
        
        self.style.configure("TButton", font=("Arial", 12), padding=8)
        self.style.configure("Primary.TButton", background=self.primary_color, 
                            foreground="black")
        self.style.configure("Success.TButton", background=self.success_color, 
                            foreground="black")
        self.style.configure("Warning.TButton", background=self.warning_color, 
                            foreground="black")
        self.style.configure("Danger.TButton", background=self.danger_color, 
                            foreground="black")
        
        self.style.configure("CardTitle.TLabel", background="white", 
                            foreground="#212529", font=("Arial", 16, "bold"))
        self.style.configure("CardText.TLabel", background="white", 
                            foreground="#495057", font=("Arial", 12))
        
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TCombobox", font=("Arial", 12), padding=5)
        self.style.configure("Header.TLabel", background=self.header_color, 
                            foreground="white", font=("Arial", 14))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_page(self):
        self.clear_window()
        
        # Фоновая картинка
        try:
            response = requests.get("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4")
            bg_image = Image.open(BytesIO(response.content))
            bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.root.configure(bg=self.bg_color)
        
        # Основной контент
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок - белый текст для лучшей видимости
        ttk.Label(main_frame, text="Добро пожаловать в наш ресторан!", 
                 style="Title.TLabel", foreground="black").grid(row=0, column=0, pady=(0, 20))
        
        # Описание - также белый
        ttk.Label(main_frame, 
                 text="Забронируйте столик и насладитесь изысканной кухней в уютной атмосфере", 
                 style="Subtitle.TLabel", foreground="black", wraplength=500).grid(row=1, column=0, pady=(0, 30))
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame, style="TFrame")
        btn_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Войти", style="Primary.TButton",
                  command=self.show_login_page).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Зарегистрироваться", style="Success.TButton",
                  command=self.show_register_page).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Продолжить без входа", style="Warning.TButton",
                  command=self.show_main_page).pack(side="left", padx=10)

    def show_login_page(self):
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок
        ttk.Label(main_frame, text="Вход в систему", 
                 style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Поля ввода
        ttk.Label(main_frame, text="Email:", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        self.email_entry.focus()
        
        ttk.Label(main_frame, text="Пароль:", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame, style="TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Войти", style="Primary.TButton",
                  command=self.login).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Назад", style="Danger.TButton",
                  command=self.show_welcome_page).pack(side="left", padx=10)

    def show_register_page(self):
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок
        ttk.Label(main_frame, text="Регистрация", 
                 style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поля ввода
        fields = [
            ("ФИО:", "full_name"),
            ("Email:", "email"),
            ("Телефон:", "phone"),
            ("Пароль:", "password"),
            ("Подтвердите пароль:", "confirm_password")
        ]
        
        self.register_entries = {}
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label, style="Subtitle.TLabel").grid(
                row=i+1, column=0, sticky="e", padx=5, pady=5)
            
            if "password" in field:
                entry = ttk.Entry(main_frame, width=30, show="*")
            else:
                entry = ttk.Entry(main_frame, width=30)
                
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.register_entries[field] = entry
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame, style="TFrame")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Зарегистрироваться", style="Success.TButton",
                  command=self.register).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Назад", style="Danger.TButton",
                  command=self.show_welcome_page).pack(side="left", padx=10)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Ошибка", "Введите email и пароль")
            return
        
        try:
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
                    self.show_main_page()
                else:
                    messagebox.showerror("Ошибка", "Профиль пользователя не найден")
            else:
                messagebox.showerror("Ошибка", "Неверный email или пароль")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка входа: {str(e)}")

    def register(self):
        # Получаем данные из формы
        data = {
            "full_name": self.register_entries["full_name"].get(),
            "email": self.register_entries["email"].get(),
            "phone": self.register_entries["phone"].get(),
            "password": self.register_entries["password"].get(),
            "confirm_password": self.register_entries["confirm_password"].get()
        }
        
        # Проверки
        if not data["full_name"]:
            messagebox.showerror("Ошибка", "Введите ФИО")
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
            # Регистрация пользователя
            auth_response = supabase.auth.sign_up({
                "email": data["email"],
                "password": data["password"],
                "options": {
                    "data": {
                        "full_name": data["full_name"],
                        "role": "client"
                    }
                }
            })
            
            if auth_response.user:
                # Получаем токен доступа
                access_token = auth_response.session.access_token if auth_response.session else None
                
                if access_token:
                    # Создаем нового клиента Supabase с токеном доступа
                    authed_supabase = create_client(SUPABASE_URL, SUPABASE_KEY, {
                        'global': {
                            'headers': {
                                'Authorization': f'Bearer {access_token}'
                            }
                        }
                    })
                    
                    # Обновляем профиль с использованием авторизованного клиента
                    update_response = authed_supabase.table("profiles").update({
                        "phone": data["phone"]
                    }).eq("id", auth_response.user.id).execute()
                    
                    if update_response.data:
                        messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
                        self.show_login_page()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось обновить профиль")
                else:
                    messagebox.showerror("Ошибка", "Не удалось получить токен доступа")
            else:
                messagebox.showerror("Ошибка", "Не удалось зарегистрировать пользователя")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {str(e)}")

    def show_main_page(self):
        self.clear_window()
        
        # Создаем верхнюю панель
        header_frame = ttk.Frame(self.root, style="Header.TFrame", height=70)
        header_frame.pack(fill="x", side="top")
        
        # Информация о пользователе
        user_info = ""
        if self.current_profile:
            user_info = f"{self.current_profile['full_name']}"
        else:
            user_info = "Гость"
            
        user_label = ttk.Label(
            header_frame, 
            text=user_info,
            style="Header.TLabel"
        )
        user_label.pack(side="left", padx=20)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(header_frame, style="Header.TFrame")
        nav_frame.pack(side="right", padx=20)
        
        if self.current_user:
            ttk.Button(nav_frame, text="Профиль", style="Primary.TButton",
                      command=self.show_profile).pack(side="left", padx=5)
            ttk.Button(nav_frame, text="История", style="Primary.TButton",
                      command=self.show_history).pack(side="left", padx=5)
            ttk.Button(nav_frame, text="Выйти", style="Danger.TButton",
                      command=self.logout).pack(side="left", padx=5)
        else:
            ttk.Button(nav_frame, text="Войти", style="Primary.TButton",
                      command=self.show_login_page).pack(side="left", padx=5)
        
        # Основной контейнер
        self.main_container = ttk.Notebook(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Создаем вкладки
        self.home_tab = ttk.Frame(self.main_container, style="TFrame")
        self.menu_tab = ttk.Frame(self.main_container, style="TFrame")
        self.reservation_tab = ttk.Frame(self.main_container, style="TFrame")
        
        self.main_container.add(self.home_tab, text="Главная")
        self.main_container.add(self.menu_tab, text="Меню")
        self.main_container.add(self.reservation_tab, text="Бронирование")
        
        # Заполняем вкладки
        self.fill_home_tab()
        self.fill_menu_tab()
        self.fill_reservation_tab()

    def fill_home_tab(self):
        # Очистка вкладки
        for widget in self.home_tab.winfo_children():
            widget.destroy()
        
        # Основной контент
        content_frame = ttk.Frame(self.home_tab, style="TFrame")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Приветствие
        greeting = "Добро пожаловать в наш ресторан!" if not self.current_user else f"Добро пожаловать, {self.current_profile['full_name']}!"
        ttk.Label(content_frame, text=greeting, style="Title.TLabel").pack(pady=20)
        
        # Информационные карточки
        cards_frame = ttk.Frame(content_frame, style="TFrame")
        cards_frame.pack(fill="x", pady=20)
        
        # Карточка 1 - О нас
        card1 = ttk.Frame(cards_frame, style="Card.TFrame", width=300, height=200)
        card1.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ttk.Label(card1, text="О нас", style="CardTitle.TLabel").pack(pady=10, padx=10, anchor="w")
        ttk.Label(card1, text="Наш ресторан предлагает изысканные блюда в уютной атмосфере. Мы используем только свежие продукты и традиционные рецепты.", 
                 style="CardText.TLabel", wraplength=250).pack(pady=5, padx=10, anchor="w")
        
        # Карточка 2 - Часы работы
        card2 = ttk.Frame(cards_frame, style="Card.TFrame", width=300, height=200)
        card2.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ttk.Label(card2, text="Часы работы", style="CardTitle.TLabel").pack(pady=10, padx=10, anchor="w")
        ttk.Label(card2, text="Пн-Пт: 10:00 - 23:00\nСб-Вс: 11:00 - 00:00", 
                 style="CardText.TLabel").pack(pady=5, padx=10, anchor="w")
        
        # Карточка 3 - Контакты
        card3 = ttk.Frame(cards_frame, style="Card.TFrame", width=300, height=200)
        card3.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ttk.Label(card3, text="Контакты", style="CardTitle.TLabel").pack(pady=10, padx=10, anchor="w")
        ttk.Label(card3, text="Телефон: +7 (123) 456-78-90\nEmail: info@restaurant.com\nАдрес: ул. Ресторанная, д. 1", 
                 style="CardText.TLabel").pack(pady=5, padx=10, anchor="w")
        
        # Кнопка бронирования
        btn_frame = ttk.Frame(content_frame, style="TFrame")
        btn_frame.pack(pady=30)
        ttk.Button(btn_frame, text="Забронировать стол", style="Success.TButton",
                  command=lambda: self.main_container.select(self.reservation_tab)).pack(pady=10)

    def fill_menu_tab(self):
        # Очистка вкладки
        for widget in self.menu_tab.winfo_children():
            widget.destroy()
        
        # Основной контент
        content_frame = ttk.Frame(self.menu_tab, style="TFrame")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        ttk.Label(content_frame, text="Наше меню", style="Title.TLabel").pack(pady=20)
        
        # Получаем меню из базы данных
        try:
            response = supabase.table("menu").select("*").eq("is_available", True).execute()
            menu_items = response.data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить меню: {str(e)}")
            menu_items = []
        
        # Группируем по категориям
        categories = {}
        for item in menu_items:
            category = item.get("category", "Без категории")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Создаем вкладки для категорий
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        for category, items in categories.items():
            tab = ttk.Frame(notebook, style="TFrame")
            notebook.add(tab, text=category)
            
            # Создаем фрейм для прокрутки
            canvas = tk.Canvas(tab)
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas, style="TFrame")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Отображаем блюда
            for i, item in enumerate(items):
                dish_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
                dish_frame.pack(fill="x", padx=10, pady=10, ipadx=10, ipady=10)
                
                # Название и цена
                ttk.Label(dish_frame, text=item["name"], 
                         style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
                ttk.Label(dish_frame, text=f"{item['price']} руб.", 
                         style="CardTitle.TLabel").grid(row=0, column=1, sticky="e")
                
                # Описание
                if item.get("description"):
                    ttk.Label(dish_frame, text=item["description"], 
                             style="CardText.TLabel", wraplength=600).grid(
                                 row=1, column=0, columnspan=2, sticky="w", pady=5)
                
                # Кнопка добавления в заказ (если пользователь авторизован)
                if self.current_user:
                    ttk.Button(dish_frame, text="Добавить в заказ", 
                              style="Success.TButton", width=15,
                              command=lambda i=item: self.add_to_order(i)).grid(
                                  row=2, column=1, sticky="e", pady=5)

    def add_to_order(self, item):
        # Здесь будет логика добавления в заказ
        messagebox.showinfo("Добавлено", f"{item['name']} добавлено в ваш заказ!")

    def fill_reservation_tab(self):
        # Очистка вкладки
        for widget in self.reservation_tab.winfo_children():
            widget.destroy()
        
        # Основной контент
        content_frame = ttk.Frame(self.reservation_tab, style="TFrame")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        ttk.Label(content_frame, text="Бронирование стола", style="Title.TLabel").pack(pady=20)
        
        # Контейнер для формы и выбора столов
        main_container = ttk.Frame(content_frame, style="TFrame")
        main_container.pack(fill="both", expand=True)
        
        # Форма бронирования - левая панель
        form_frame = ttk.Frame(main_container, style="Card.TFrame")
        form_frame.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)
        
        ttk.Label(form_frame, text="Данные для бронирования", 
                 style="CardTitle.TLabel").pack(pady=10, anchor="w")
        
        # Поля формы
        fields = [
            ("Дата:", "date"),
            ("Время:", "time"),
            ("Количество гостей:", "guests"),
            ("Имя:", "name"),
            ("Телефон:", "phone"),
            ("Email:", "email")
        ]
        
        self.reservation_entries = {}
        
        for i, (label, field) in enumerate(fields):
            row_frame = ttk.Frame(form_frame, style="Card.TFrame")
            row_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(row_frame, text=label, width=20, 
                     style="CardText.TLabel").pack(side="left")
            
            if field == "guests":
                entry = ttk.Combobox(row_frame, width=25, values=[str(i) for i in range(1, 21)])
                entry.current(0)
            elif field == "date":
                # Виджет календаря
                entry_frame = ttk.Frame(row_frame)
                entry_frame.pack(side="left", fill="x", expand=True)
                
                self.calendar_btn = ttk.Button(entry_frame, text="Выбрать дату",
                                             command=self.show_calendar)
                self.calendar_btn.pack(side="left")
                
                self.date_var = tk.StringVar()
                self.date_label = ttk.Label(entry_frame, textvariable=self.date_var,
                                          style="CardText.TLabel")
                self.date_label.pack(side="left", padx=5)
                entry = None  # Для этого поля не будет прямого ввода
            elif field == "time":
                # Выпадающий список с временами
                times = [f"{hour:02d}:{minute:02d}" for hour in range(10, 22) for minute in [0, 30]]
                entry = ttk.Combobox(row_frame, width=25, values=times)
                entry.current(0)
            else:
                entry = ttk.Entry(row_frame, width=28)
            
            if entry is not None:
                entry.pack(side="left")
                self.reservation_entries[field] = entry
            else:
                self.reservation_entries[field] = self.date_var
        
        # Заполняем данные пользователя, если он авторизован
        if self.current_profile:
            self.reservation_entries["name"].insert(0, self.current_profile["full_name"])
            self.reservation_entries["phone"].insert(0, self.current_profile.get("phone", ""))
            self.reservation_entries["email"].insert(0, self.current_profile["email"])
        
        # Кнопка бронирования
        btn_frame = ttk.Frame(form_frame, style="Card.TFrame")
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Забронировать", style="Success.TButton",
                  command=self.make_reservation).pack(pady=10)
        
        # Правая панель - выбор стола
        tables_frame = ttk.Frame(main_container, style="Card.TFrame")
        tables_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10, ipadx=10, ipady=10)
        
        ttk.Label(tables_frame, text="Выберите стол", 
                 style="CardTitle.TLabel").pack(pady=10, anchor="w")
        
        # Контейнер для столов
        self.tables_container = ttk.Frame(tables_frame, style="Card.TFrame")
        self.tables_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Загружаем столы
        self.load_tables()
    
    def show_calendar(self):
        """Показывает календарь для выбора даты"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор даты")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Минимальная дата - сегодня
        min_date = datetime.date.today()
        # Максимальная дата - через 3 месяца
        max_date = min_date + datetime.timedelta(days=90)
        
        cal = Calendar(dialog, selectmode='day', 
                      year=min_date.year, month=min_date.month, day=min_date.day,
                      mindate=min_date, maxdate=max_date,
                      locale='ru_RU',
                      date_pattern='dd/mm/yyyy')  # Указываем нужный формат
        cal.pack(padx=10, pady=10)
        
        def set_date():
                # Форматируем дату в нужный формат
            selected_date = cal.get_date()
            self.date_var.set(selected_date)
            dialog.destroy()
        
        ttk.Button(dialog, text="Выбрать", command=set_date).pack(pady=10)
    
    def load_tables(self):
        """Загружает и отображает доступные столы"""
        try:
            # Получаем все столы из базы данных
            response = supabase.table("tables").select("*").order("number").execute()
            tables = response.data
            
            # Получаем текущие бронирования
            reservations = supabase.table("reservations").select("table_id").eq("status", "active").execute()
            booked_table_ids = {res["table_id"] for res in reservations.data}
            
            # Очищаем контейнер
            for widget in self.tables_container.winfo_children():
                widget.destroy()
            
            # Создаем сетку для столов
            self.table_buttons = {}
            row, col = 0, 0
            
            for table in tables:
                # Определяем статус стола
                is_booked = table["id"] in booked_table_ids
                status = "booked" if is_booked else "free"
                
                # Обновляем статус в объекте стола
                table["status"] = status
                
                # Определяем стиль кнопки
                style = "Primary.TButton" if status == "free" else "Danger.TButton"
                
                # Создаем кнопку для стола
                btn = ttk.Button(
                    self.tables_container,
                    text=f"Стол {table['number']}\n(до {table['capacity']} чел.)",
                    style=style,
                    width=12,
                    command=lambda t=table: self.select_table(t)
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                
                # Сохраняем ссылку на кнопку
                self.table_buttons[table['id']] = btn
                
                # Обновляем позицию в сетке
                col += 1
                if col > 4:
                    col = 0
                    row += 1
            
            # Сохраняем список столов
            self.all_tables = tables
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить столы: {str(e)}")
    
    def select_table(self, table):
        """Выбирает стол для бронирования"""
        # Проверяем, свободен ли стол
        if table['status'] != 'free':
            messagebox.showwarning("Стол занят", "Этот стол уже забронирован, выберите другой")
            return
        
        # Сбрасываем предыдущий выбор
        if self.selected_table:
            self.table_buttons[self.selected_table['id']].configure(style="Primary.TButton")
        
        # Подсвечиваем выбранный стол
        self.table_buttons[table['id']].configure(style="Success.TButton")
        self.selected_table = table
        messagebox.showinfo("Стол выбран", f"Вы выбрали стол №{table['number']}")
    
    def make_reservation(self):
        """Создает бронирование"""
        try:
            # Получаем данные из формы
            data = {}
            for field, entry in self.reservation_entries.items():
                if isinstance(entry, ttk.Entry) or isinstance(entry, ttk.Combobox):
                    data[field] = entry.get()
                elif isinstance(entry, tk.StringVar):
                    data[field] = entry.get()
            
            # Проверка заполненности полей
            required_fields = ["date", "time", "guests", "name", "phone", "email"]
            for field in required_fields:
                if not data.get(field):
                    messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                    return
            
            # Проверка выбора стола
            if not self.selected_table:
                messagebox.showerror("Ошибка", "Выберите стол для бронирования")
                return
            
            # Преобразуем количество гостей в число
            try:
                guests = int(data["guests"])
            except ValueError:
                messagebox.showerror("Ошибка", "Количество гостей должно быть числом")
                return
            
            # Проверка диапазона гостей
            if guests < 1 or guests > 20:
                messagebox.showerror("Ошибка", "Количество гостей должно быть от 1 до 20")
                return
            
            # Проверяем, что стол подходит для количества гостей
            table_capacity = self.selected_table["capacity"]
            if guests > table_capacity:
                messagebox.showerror("Ошибка", 
                                   f"Выбранный стол вмещает только {table_capacity} гостей")
                return
            
            # Форматирование времени (добавляем двоеточие, если нужно)
            time_str = data["time"]
            if ":" not in time_str and len(time_str) == 4:
                time_str = f"{time_str[:2]}:{time_str[2:]}"
                data["time"] = time_str
            
            # Проверка формата времени
            if not re.match(r"^\d{1,2}:\d{2}$", time_str):
                messagebox.showerror("Ошибка", "Введите время в формате ЧЧ:ММ (например, 10:00)")
                return
            
            # Форматирование даты
            date_str = data["date"]
            try:
                # Пробуем разные форматы даты
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    try:
                        date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")
                    except:
                        date_obj = datetime.datetime.strptime(date_str, "%d/%m/%y")
                
                # Форматируем дату в единый формат для отображения
                formatted_date = date_obj.strftime("%d/%m/%Y")
                self.date_var.set(formatted_date)
                
            except Exception:
                messagebox.showerror("Ошибка", 
                                    "Введите дату в формате ДД/ММ/ГГГГ (например, 29/06/2025)")
                return
            
            # Создаем полную дату-время
            start_time = datetime.datetime.combine(date_obj.date(), 
                                                 datetime.datetime.strptime(time_str, "%H:%M").time())
            
            # Бронирование на 2 часа
            end_time = start_time + datetime.timedelta(hours=2)
            
            # Проверка, что время в рабочем диапазоне
            if start_time.hour < 10 or start_time.hour > 22:
                messagebox.showerror("Ошибка", "Ресторан работает с 10:00 до 22:00")
                return
            
            # Создаем бронирование
            reservation_data = {
                "table_id": self.selected_table["id"],
                "user_id": self.current_user.id if self.current_user else None,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "guests_count": guests,
                "customer_name": data["name"],
                "customer_phone": data["phone"],
                "customer_email": data["email"],
                "status": "active"
            }
            
            # Отправляем данные в Supabase
            response = supabase.table("reservations").insert(reservation_data).execute()
            
            if response.data:
                messagebox.showinfo("Успех", "Столик успешно забронирован!")
                
                # Обновляем статус стола
                supabase.table("tables").update({"status": "booked"}).eq("id", self.selected_table["id"]).execute()
                
                # Очищаем форму
                for entry in self.reservation_entries.values():
                    if isinstance(entry, ttk.Entry):
                        entry.delete(0, tk.END)
                    elif isinstance(entry, ttk.Combobox):
                        entry.set('')
                self.date_var.set('')
                self.selected_table = None
                self.load_tables()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_profile(self):
        if not self.current_user:
            messagebox.showinfo("Информация", "Для просмотра профиля необходимо войти в систему")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Ваш профиль")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text="Ваш профиль", style="Title.TLabel").pack(pady=20)
        
        # Информация
        profile_frame = ttk.Frame(dialog, style="Card.TFrame")
        profile_frame.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)
        
        fields = [
            ("ФИО:", self.current_profile["full_name"]),
            ("Email:", self.current_profile["email"]),
            ("Телефон:", self.current_profile.get("phone", "не указан")),
            ("Роль:", self.current_profile["role"])
        ]
        
        for i, (label, value) in enumerate(fields):
            row_frame = ttk.Frame(profile_frame, style="Card.TFrame")
            row_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(row_frame, text=label, width=10, 
                     style="CardText.TLabel").pack(side="left")
            ttk.Label(row_frame, text=value, 
                     style="CardText.TLabel").pack(side="left")
        
        # Кнопка редактирования
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Редактировать", style="Primary.TButton").pack(pady=5)
        ttk.Button(btn_frame, text="Закрыть", style="Danger.TButton",
                  command=dialog.destroy).pack(pady=5)

    def show_history(self):
        if not self.current_user:
            messagebox.showinfo("Информация", "Для просмотра истории необходимо войти в систему")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("История бронирований")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text="История бронирований", style="Title.TLabel").pack(pady=20)
        
        # Таблица с историей
        columns = ("date", "time", "guests", "status")
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=15)
        
        tree.heading("date", text="Дата")
        tree.heading("time", text="Время")
        tree.heading("guests", text="Гости")
        tree.heading("status", text="Статус")
        
        tree.column("date", width=150, anchor="center")
        tree.column("time", width=150, anchor="center")
        tree.column("guests", width=100, anchor="center")
        tree.column("status", width=150, anchor="center")
        
        # Заполняем тестовыми данными
        for i in range(10):
            tree.insert("", "end", values=(
                f"2023-12-{10+i}",
                f"{18+i%3}:00",
                f"{2+i%4}",
                "Подтверждено" if i % 2 == 0 else "Ожидание"
            ))
        
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Отменить бронь", style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Повторить бронь", style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Закрыть", style="Danger.TButton",
                  command=dialog.destroy).pack(side="right", padx=5)

    def logout(self):
        self.current_user = None
        self.current_profile = None
        self.show_main_page()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantClientApp(root)
    root.mainloop()
