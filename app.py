import os
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from pyzbar.pyzbar import decode
import openpyxl as xl

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

    # Pedir al usuario dónde guardar el archivo Excel
    excel_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if excel_path:
        wb.save(excel_path)
        messagebox.showinfo("Proceso completado", f"Se ha generado el archivo Excel en:\n{excel_path}")

# Función para leer códigos de barra de una imagen
# Función para leer códigos de barra de una imagen
def read_barcodes(image_path):
    try:
        image = cv2.imread(image_path)
        barcodes = decode(image)

        if barcodes:
            # Ordenar los códigos de barra por su posición vertical (y)
            barcodes_sorted = sorted(barcodes, key=lambda x: x.rect.top)

            decoded_codes = []
            for barcode in barcodes_sorted:
                barcode_data = barcode.data.decode("utf-8")
                decoded_codes.append(barcode_data)

            # Retornar solo los primeros 3 códigos encontrados (Receta, Autorizacion y Troquel)
            if len(decoded_codes) >= 3:
                return decoded_codes[:3]
            elif len(decoded_codes) == 2:
                return [decoded_codes[0], decoded_codes[1], ""]
            elif len(decoded_codes) == 1:
                return [decoded_codes[0], "", ""]
        
        return ["", "", ""]  # No se encontraron suficientes códigos de barra

    except Exception as e:
        print(f"Error al procesar la imagen {image_path}: {e}")
        return ["", "", ""]  # Manejo básico de errores para continuar con otras imágenes

root = tk.Tk()
root.title("Extractor de Códigos de Barra")
root.geometry("400x150")

label = tk.Label(root, text="Selecciona la carpeta con imágenes .tif:")
label.pack(pady=10)

button = tk.Button(root, text="Seleccionar Carpeta", command=select_folder)
button.pack(pady=10)

root.mainloop()
