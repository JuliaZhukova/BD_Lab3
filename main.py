import tkinter as tk
from tkinter import ttk, messagebox
import pymongo
from pymongo import MongoClient


class CleanHospitalApp:
    # Сучасна світла/темно-синя палітра класичного застосунку
    BG_MAIN = "#f1f5f9"       # Світло-сірий приємний фон вікна
    BG_SIDEBAR = "#1e293b"    # Темна бічна панель меню
    BG_CARD = "#ffffff"       # Білі картки контенту
    FG_DARK = "#0f172a"       # Темний текст
    FG_MUTED = "#64748b"      # Сірий допоміжний текст
    ACCENT = "#2563eb"        # Основний синій колір кнопок
    ACCENT_HOVER = "#1d4ed8"
    GREEN = "#10b981"         # Зелений колір для головної кнопки

    def __init__(self, root):
        self.root = root
        self.root.title("Аналітика медичних закладів — Лабораторна робота №3 (Варіант 1)")
        self.root.geometry("1020x640")
        self.root.minsize(900, 560)
        self.root.configure(bg=self.BG_MAIN)

        self.setup_styles()
        self.connect_db()
        self.build_ui()

        if self.connected:
            self.auto_pick_threshold(silent=True)
            self.step_1()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Clean.Treeview",
            background=self.BG_CARD,
            foreground=self.FG_DARK,
            fieldbackground=self.BG_CARD,
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Clean.Treeview.Heading",
            background="#e2e8f0",
            foreground=self.FG_DARK,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=(12, 8)
        )
        style.map(
            "Clean.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")]
        )

    def connect_db(self):
        try:
            self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2500)
            self.db = self.client["hospitals_mongodb"]
            self.collection = self.db["hospitals"]
            self.client.server_info()
            self.connected = True
            self.status_text = "● Базу даних підключено"
            self.status_color = "#10b981"
        except Exception:
            self.connected = False
            self.status_text = "● Немає зв'язку з базою даних"
            self.status_color = "#ef4444"

    def build_ui(self):
        # ================= ЛІВЕ МЕНЮ =================
        sidebar = tk.Frame(self.root, bg=self.BG_SIDEBAR, width=290, padx=18, pady=20)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Аналітика лікарень", bg=self.BG_SIDEBAR,
            fg="#ffffff", font=("Segoe UI", 15, "bold"), anchor="w"
        ).pack(fill="x")

        tk.Label(
            sidebar, text="Лабораторна робота №3 • Варіант 1", bg=self.BG_SIDEBAR,
            fg="#94a3b8", font=("Segoe UI", 9), anchor="w"
        ).pack(fill="x", pady=(2, 18))

        # Кнопка виконання всього одразу
        tk.Button(
            sidebar, text="▶ Розрахувати всі кроки",
            command=self.run_all, bg=self.GREEN, fg="#ffffff",
            activebackground="#059669", activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=9
        ).pack(fill="x", pady=(0, 18))

        tk.Label(
            sidebar, text="ЗВІТИ ЗА ЗАВДАННЯМ", bg=self.BG_SIDEBAR,
            fg="#94a3b8", font=("Segoe UI", 8, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 6))

        self.nav_buttons = []
        menu_items = [
            ("1. Загальна кількість записів", self.step_1),
            ("2. Загальна сума витрат", self.step_2),
            ("3. Сума витрат за штатами", self.step_3),
            ("4. Відбір штатів за порогом суми", self.step_4),
            ("5. Відбір за виписками та сумою", self.step_5),
        ]

        for title, cmd in menu_items:
            btn = tk.Button(
                sidebar, text=f"  {title}", command=cmd,
                bg="#334155", fg="#f8fafc",
                activebackground=self.ACCENT, activeforeground="#ffffff",
                font=("Segoe UI", 9, "bold"), relief="flat", anchor="w",
                cursor="hand2", pady=9, padx=6
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons.append(btn)

        # Налаштування фільтрів
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", pady=16)

        tk.Label(
            sidebar, text="НАЛАШТУВАННЯ ФІЛЬТРІВ", bg=self.BG_SIDEBAR,
            fg="#94a3b8", font=("Segoe UI", 8, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 8))

        tk.Label(
            sidebar, text="Мінімальна сума витрат ($):", bg=self.BG_SIDEBAR,
            fg="#e2e8f0", font=("Segoe UI", 9), anchor="w"
        ).pack(fill="x")

        self.entry_min_sum = tk.Entry(
            sidebar, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="flat", bd=6
        )
        self.entry_min_sum.insert(0, "350000000")
        self.entry_min_sum.pack(fill="x", pady=(4, 6))

        tk.Button(
            sidebar, text="Підібрати значення автоматично",
            command=lambda: self.auto_pick_threshold(silent=False),
            bg="#475569", fg="#ffffff", activebackground="#64748b",
            activeforeground="#ffffff", font=("Segoe UI", 8),
            relief="flat", cursor="hand2", pady=4
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            sidebar, text="Мін. кількість виписок пацієнтів:", bg=self.BG_SIDEBAR,
            fg="#e2e8f0", font=("Segoe UI", 9), anchor="w"
        ).pack(fill="x")

        self.entry_min_discharges = tk.Entry(
            sidebar, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="flat", bd=6
        )
        self.entry_min_discharges.insert(0, "20")
        self.entry_min_discharges.pack(fill="x", pady=(4, 0))

        # Статус підключення внизу меню
        tk.Label(
            sidebar, text=self.status_text, bg=self.BG_SIDEBAR,
            fg=self.status_color, font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(side="bottom", fill="x")

        # ================= ПРАВА ROBOЧА ОБЛАСТЬ =================
        content = tk.Frame(self.root, bg=self.BG_MAIN, padx=24, pady=20)
        content.pack(side="right", fill="both", expand=True)

        # Верхня картка з заголовком і підсумком
        header_card = tk.Frame(content, bg=self.BG_CARD, padx=20, pady=16)
        header_card.pack(fill="x", pady=(0, 16))

        self.lbl_title = tk.Label(
            header_card, text="Заголовок звіту", bg=self.BG_CARD,
            fg=self.FG_DARK, font=("Segoe UI", 14, "bold"), anchor="w"
        )
        self.lbl_title.pack(fill="x")

        self.lbl_subtitle = tk.Label(
            header_card, text="Опис дії", bg=self.BG_CARD,
            fg=self.FG_MUTED, font=("Segoe UI", 10), anchor="w"
        )
        self.lbl_subtitle.pack(fill="x", pady=(2, 12))

        # Картка головного результату
        summary_box = tk.Frame(header_card, bg="#eff6ff", padx=14, pady=10)
        summary_box.pack(fill="x")

        self.lbl_summary = tk.Label(
            summary_box, text="Результат: —", bg="#eff6ff",
            fg="#1d4ed8", font=("Segoe UI", 11, "bold"), anchor="w"
        )
        self.lbl_summary.pack(side="left")

        # Таблиця даних
        table_card = tk.Frame(content, bg=self.BG_CARD, padx=2, pady=2)
        table_card.pack(fill="both", expand=True)

        columns = ("num", "name", "value")
        self.tree = ttk.Treeview(
            table_card, columns=columns, show="headings", style="Clean.Treeview"
        )
        self.tree.heading("num", text="№")
        self.tree.heading("name", text="Категорія / Штат")
        self.tree.heading("value", text="Показник")

        self.tree.column("num", width=65, anchor="center")
        self.tree.column("name", width=300, anchor="center")
        self.tree.column("value", width=320, anchor="e")

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8fafc")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def select_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.config(bg=self.ACCENT if i == index else "#334155")

    def fill_table(self, col_name, col_val, rows):
        self.tree.heading("name", text=col_name)
        self.tree.heading("value", text=col_val)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, (name, val) in enumerate(rows, 1):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(idx, name, val), tags=(tag,))

    def auto_pick_threshold(self, silent=False):
        try:
            pipeline = [
                {"$group": {"_id": "$Provider_State", "totalCharges": {"$sum": "$Average_Covered_Charges"}}},
                {"$sort": {"totalCharges": pymongo.DESCENDING}},
                {"$limit": 10}
            ]
            top_states = list(self.collection.aggregate(pipeline))
            if len(top_states) >= 8:
                suggested = int(top_states[7]["totalCharges"]) - 1000
                self.entry_min_sum.delete(0, tk.END)
                self.entry_min_sum.insert(0, str(suggested))
                if not silent:
                    messagebox.showinfo(
                        "Значення підібрано",
                        f"Встановлено поріг суми: {suggested:,} $\n\n"
                        f"Це значення дозволяє відібрати 8 провідних штатів у 4-му звіті."
                    )
        except Exception as e:
            if not silent:
                messagebox.showerror("Помилка", str(e))

    # 1. Кількість документів
    def step_1(self):
        self.select_nav(0)
        res = list(self.collection.aggregate([
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]))
        count_val = res[0]["count"] if res else 0

        self.lbl_title.config(text="Крок 1. Загальна кількість записів у базі")
        self.lbl_subtitle.config(text="Підрахунок усіх зареєстрованих записів медичних закладів")
        self.lbl_summary.config(text=f"Усього знайдено записів: {count_val:,}")
        self.fill_table("Набір даних", "Кількість записів", [("Усі медичні заклади", f"{count_val:,} шт.")])

    # 2. Загальна сума
    def step_2(self):
        self.select_nav(1)
        res = list(self.collection.aggregate([
            {"$group": {"_id": None, "totalCharges": {"$sum": "$Average_Covered_Charges"}}}
        ]))
        total_val = res[0]["totalCharges"] if res else 0

        self.lbl_title.config(text="Крок 2. Загальна сума покритих витрат")
        self.lbl_subtitle.config(text="Сумарна вартість медичних послуг за всіма записами в базі даних")
        self.lbl_summary.config(text=f"Загальна сума: {total_val:,.2f} $")
        self.fill_table("Набір даних", "Загальна сума витрат", [("Усі медичні заклади", f"{total_val:,.2f} $")])

    # 3. Сума за штатами
    def step_3(self):
        self.select_nav(2)
        self.collection.aggregate([
            {"$group": {"_id": "$Provider_State", "totalCharges": {"$sum": "$Average_Covered_Charges"}}},
            {"$sort": {"totalCharges": pymongo.DESCENDING}},
            {"$out": "records_accsumsort"}
        ])
        docs = list(self.db["records_accsumsort"].find())

        self.lbl_title.config(text="Крок 3. Сума витрат для кожного штату")
        self.lbl_subtitle.config(text="Групування витрат за штатами та впорядкування від найбільшого до найменшого")
        self.lbl_summary.config(text=f"Оброблено штатів: {len(docs)}  (результат збережено в базу)")
        rows = [(doc["_id"], f'{doc["totalCharges"]:,} $') for doc in docs]
        self.fill_table("Штат", "Сума витрат ($)", rows)

    # 4. Штати, де сума перевищує поріг
    def step_4(self):
        self.select_nav(3)
        try:
            min_sum = int(self.entry_min_sum.get())
        except ValueError:
            messagebox.showwarning("Увага", "Введіть ціле число у поле мінімальної суми!")
            return

        self.collection.aggregate([
            {"$group": {"_id": "$Provider_State", "totalCharges": {"$sum": "$Average_Covered_Charges"}}},
            {"$match": {"totalCharges": {"$gt": min_sum}}},
            {"$sort": {"totalCharges": pymongo.DESCENDING}},
            {"$out": "records_accsumsortgt"}
        ])
        docs = list(self.db["records_accsumsortgt"].find())

        self.lbl_title.config(text="Крок 4. Відбір штатів із високими витратами")
        self.lbl_subtitle.config(text=f"Відображення лише тих штатів, де загальна сума витрат перевищує {min_sum:,} $")
        self.lbl_summary.config(text=f"Відібрано штатів: {len(docs)}  (результат збережено в базу)")
        rows = [(doc["_id"], f'{doc["totalCharges"]:,} $') for doc in docs]
        self.fill_table("Штат", "Сума витрат ($)", rows)

    # 5. Фільтр за виписками > 20 та сумою > порогу
    def step_5(self):
        self.select_nav(4)
        try:
            min_sum = int(self.entry_min_sum.get())
            min_dis = int(self.entry_min_discharges.get())
        except ValueError:
            messagebox.showwarning("Увага", "Введіть коректні числа у поля фільтрів!")
            return

        self.collection.aggregate([
            {"$match": {"Total_Discharges": {"$gt": min_dis}}},
            {"$group": {"_id": "$Provider_State", "totalCharges": {"$sum": "$Average_Covered_Charges"}}},
            {"$match": {"totalCharges": {"$gt": min_sum}}},
            {"$sort": {"totalCharges": pymongo.DESCENDING}},
            {"$out": "records_acctdsumsort"}
        ])
        docs = list(self.db["records_acctdsumsort"].find())

        self.lbl_title.config(text="Крок 5. Комбінований відбір за кількістю виписок та сумою")
        self.lbl_subtitle.config(
            text=f"Враховано лише лікарні з кількістю виписок понад {min_dis} та штати з сумою понад {min_sum:,} $"
        )
        self.lbl_summary.config(text=f"Відібрано штатів після фільтрації: {len(docs)}  (результат збережено в базу)")
        rows = [(doc["_id"], f'{doc["totalCharges"]:,} $') for doc in docs]
        self.fill_table("Штат", "Сума витрат ($)", rows)

    def run_all(self):
        self.step_1()
        self.step_2()
        self.step_3()
        self.step_4()
        self.step_5()
        messagebox.showinfo(
            "Розрахунок завершено",
            "Усі 5 звітів успішно сформовано та збережено в базу даних!"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CleanHospitalApp(root)
    root.mainloop()