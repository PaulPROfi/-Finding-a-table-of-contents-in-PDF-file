import tkinter as tk  # для создания диалоговых окон
from tkinter import filedialog, messagebox  # диалог выбора файла и сообщения об ошибках
from pdf2image import convert_from_path  # преобразование PDF в изображения
import pytesseract  # библиотека для распознавания текста (OCR)
import os  # работа с файловой системой
from toc_model import TOCModel #Импортируем нашу ML модель
import shutil  # для поиска исполняемых файлов в PATH

# =============================================================================
# ПОИСК И НАСТРОЙКА ВНЕШНИХ ПРОГРАММ
# =============================================================================

def setup_tesseract():
    """
    Настраивает Tesseract для распознавания русского текста
        Возвращает:
        bool: True если Tesseract найден и настроен, False если нет
    """
    # Ищем tesseract в системной переменной PATH
    tesseract_cmd = shutil.which("tesseract") 
    if tesseract_cmd:
        # Настраиваем путь к tesseract для pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        print(f"✓ Tesseract настроен: {tesseract_cmd}")
        return True
    else:
        print("❌ Tesseract не найден в PATH")
        print("Установите Tesseract-OCR и добавьте в переменную PATH")
        return False

def setup_poppler():
    """
    Находит путь к Poppler для конвертации PDF в изображения
        Возвращает:
        str: путь к папке bin Poppler или None если не найден
    """    
    # Ищем pdftoppm в системной переменной PATH
    poppler_cmd = shutil.which("pdftoppm")
    if poppler_cmd:
        # Получаем папку, где находится pdftoppm
        poppler_dir = os.path.dirname(poppler_cmd)
        print(f"✓ Poppler найден: {poppler_dir}")
        return poppler_dir
    else:
        print("❌ Poppler не найден в PATH")
        print("Установите Poppler и добавьте папку bin в переменную PATH")
        return None

# =============================================================================
# Логика звлечения текста из PDF
# =============================================================================

def main():
    """
    Основная функция программы - распознавание русского текста из PDF
    Процесс:
    1. Проверка наличия Tesseract и Poppler
    2. Выбор PDF файла пользователем
    3. Конвертация PDF в изображения
    4. Распознавание текста
    5. Сохранение результата в текстовый файл
        Возвращает:
        bool: True если успешно, False если ошибка
    """
    try:
        # =====================================================================
        # ПРОВЕРКА НЕОБХОДИМЫХ ПРОГРАММ
        # =====================================================================
        # Настраиваем Tesseract для распознавания текста
        if not setup_tesseract():
            messagebox.showerror("Ошибка", "Tesseract не найден!\n\nУстановите Tesseract-OCR и добавьте в PATH.")
            return False
        # Настраиваем Poppler для конвертации PDF
        poppler_path = setup_poppler()
        if not poppler_path:
            messagebox.showerror("Ошибка", "Poppler не найден!\n\nУстановите Poppler и добавьте папку bin в PATH.")
            return False
        
        model = TOCModel()
        
        # =====================================================================
        # ВЫБОР PDF ФАЙЛА
        # =====================================================================
        # Создаем скрытое окно для диалога выбора файла
        root = tk.Tk()
        root.withdraw()  # скрываем главное окно
        # Показываем диалог выбора PDF файла
        pdf_path = filedialog.askopenfilename(
            title="Выберите PDF документ для распознавания",
            filetypes=[("PDF файлы", "*.pdf")]
        )
        # Проверяем, выбрал ли пользователь файл
        if not pdf_path:
            messagebox.showerror("Ошибка при выборе файла", "Некорректный файл")
            return False
        print(f"📄 Выбран файл: {os.path.basename(pdf_path)}")
        # =====================================================================
        # КОНВЕРТАЦИЯ PDF В ИЗОБРАЖЕНИЯ
        # =====================================================================
        try:
            # Конвертируем PDF в изображения (первые 10 страниц)
            images = convert_from_path(
                pdf_path,
                dpi=300,  # высокое разрешение для лучшего качества распознавания
                first_page=1,
                last_page=10,  # ограничиваем 10 страницами для быстрой обработки
                poppler_path=poppler_path
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось конвертировать PDF:\n{e}")
            return False        
        # =====================================================================
        # РАСПОЗНАВАНИЕ ТЕКСТА
        # =====================================================================     
        texts = []  # список для хранения распознанного текста
        results = []
        
        # Простые и эффективные настройки
        tesseract_config = '--oem 3 --psm 6 -l rus+eng'
        
        for i, img in enumerate(images, 1):           
            try:
                # Распознаем текст с изображения
                text = pytesseract.image_to_string(
                    img,
                    config=tesseract_config
                )
                
                is_toc, confidence = model.predict(text)
                
                results.append({
                    'page': i,
                    'is_toc': is_toc,
                    'confidence': confidence
                })
                
            except Exception as e:
                texts.append(f"[Ошибка распознавания страницы {i}: {e}]")
        
        show_results(results)
        return results
    
    except Exception as e:
         print(f"❌ Критическая ошибка: {e}")
         messagebox.showerror("Ошибка", f"Произошла критическая ошибка:\n{e}")
         return False    

def show_results(results):
    """
    Показывает результаты анализа в удобном формате
    
    Аргументы:
        results (list): результаты анализа страниц
    """  
    toc_pages = []
    
    for result in results:
        status = "Оглавление" if result['is_toc'] else "Обычный текст"
        confidence = f"{result['confidence']:.1%}"
        
        print(f"Страница {result['page']}: {status}")
        print(f"   Уверенность: {confidence}")
        
        if result['is_toc']:
            toc_pages.append(result['page'])
    
    # Сводка
    print("\n📈 СВОДКА:")
    if toc_pages:
        pages_text = ", ".join(map(str, toc_pages))
        summary = f"✅ Найдено оглавление на странице: {pages_text} с увереностью {confidence}"
    else:
        summary = "❌ Оглавление не найдено на первых 10 страницах"
    
    print(summary)
    
    # Показываем результат в диалоговом окне
    messagebox.showinfo("Результат анализа", summary)



#Запуск скрипта
if __name__ == "__main__":
    main()
