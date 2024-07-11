import os
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import pytesseract
import openpyxl as xl

# Configurar la ruta de Tesseract si es necesario
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Función para seleccionar la carpeta
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_images(folder_path)

# Función para procesar las imágenes y extraer códigos de barra
def process_images(folder_path):
    wb = xl.Workbook()
    ws = wb.active
    ws.title = "Codigos de Barra"
    ws.append(["Receta", "Autorizacion", "Troquel"])

    for filename in os.listdir(folder_path):
        if filename.endswith(".tif"):
            image_path = os.path.join(folder_path, filename)
            barcodes = read_barcodes(image_path)
            if barcodes:
                ws.append(barcodes)

    excel_path = os.path.join(folder_path, "codigos_de_barras.xlsx")
    wb.save(excel_path)
    messagebox.showinfo("Proceso completado", f"Se ha generado el archivo Excel en:\n{excel_path}")

# Función para leer códigos de barra de una imagen
def read_barcodes(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = pytesseract.image_to_string(gray)
        # Filtrar para obtener sólo los datos que parecen ser códigos de barras (numéricos y longitud típica)
        decoded_codes = [code for code in barcodes.split() if code.isdigit() and 8 <= len(code) <= 13]
        if len(decoded_codes) >= 3:
            return decoded_codes[:3]  # Receta, Autorizacion y Troquel
        elif len(decoded_codes) == 2:
            return [decoded_codes[0], decoded_codes[1], ""]  # Receta y Autorizacion
        elif len(decoded_codes) == 1:
            return [decoded_codes[0], "", ""]  # Solo Receta
        return ["", "", ""]  # No se encontraron códigos suficientes
    except Exception as e:
        print(f"Error al procesar la imagen {image_path}: {e}")
        return ["", "", ""]  # Manejo básico de errores para continuar con otras imágenes

# Interfaz gráfica
root = tk.Tk()
root.title("Extractor de Códigos de Barra")
root.geometry("400x150")

label = tk.Label(root, text="Selecciona la carpeta con imágenes .tif:")
label.pack(pady=10)

button = tk.Button(root, text="Seleccionar Carpeta", command=select_folder)
button.pack(pady=10)

root.mainloop()
