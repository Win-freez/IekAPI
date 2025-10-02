import asyncio
import httpx
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from src.config import settings
from src.services.IekService import IekAPI
from src.services.ExcelService import ExcelPriceCheckerOpenpyxl

class ExcelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IEK Excel Processor")
        self.geometry("700x500")

        # Кнопки для выбора файлов
        tk.Button(self, text="Выбрать Excel-файл", command=self.select_input_file).pack(pady=5)
        tk.Button(self, text="Выбрать файл для сохранения результата", command=self.select_output_file).pack(pady=5)
        tk.Button(self, text="Запустить обработку", command=self.run_processing).pack(pady=10)

        # Текстовое поле для логов
        self.log_widget = scrolledtext.ScrolledText(self, height=25)
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.input_file = None
        self.output_file = None

    def log(self, message: str):
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.update_idletasks()

    def select_input_file(self):
        self.input_file = filedialog.askopenfilename(
            title="Выберите Excel-файл",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if self.input_file:
            self.log(f"Выбран файл: {self.input_file}")
        else:
            messagebox.showwarning("Отмена", "Файл не выбран")

    def select_output_file(self):
        self.output_file = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if self.output_file:
            self.log(f"Результат будет сохранен в: {self.output_file}")
        else:
            messagebox.showwarning("Отмена", "Файл для сохранения не выбран")

    def run_processing(self):
        if not self.input_file or not self.output_file:
            messagebox.showwarning("Ошибка", "Выберите оба файла перед запуском")
            return
        self.log("Запуск обработки...")
        self.after(100, lambda: asyncio.run(self.process_excel()))

    async def process_excel(self):
        async with httpx.AsyncClient() as client:
            api = IekAPI(client=client)
            self.log("Авторизация на IEK API...")
            await api.login(username=settings.IEK.username, password=settings.IEK.password)
            self.log("Авторизация успешна!")

            checker = ExcelPriceCheckerOpenpyxl(api=api)
            self.log("Начинаем обработку Excel-файла...")
            await checker.process_excel_file(
                file_path=self.input_file,
                output_path=self.output_file,
                article_column="Артикул",
                header_row=1
            )
            self.log("Обработка завершена!")
            messagebox.showinfo("Готово", f"Обработка завершена!\nРезультат сохранен в:\n{self.output_file}")

if __name__ == "__main__":
    app = ExcelApp()
    app.mainloop()
