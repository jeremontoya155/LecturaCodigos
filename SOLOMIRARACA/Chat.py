import cv2
from tkinter import Tk, filedialog
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import os
import shutil

def select_images():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Mostrar el diálogo para seleccionar múltiples archivos .tif y .tiff
    file_paths = filedialog.askopenfilenames(filetypes=[("TIFF files", "*.tif *.tiff"), ("PNG files", "*.png"), ("All files", "*.*")])

    # Verificar si se seleccionaron archivos
    if file_paths:
        total_count = 0
        valid_barcodes = []
        failed_images = []

        for file_path in file_paths:
            count, success, barcode = read_barcodes_from_image(file_path)
            total_count += count
            if success:
                valid_barcodes.append(barcode)
            else:
                print(f'Aplicando técnicas adicionales a la imagen {file_path}')
                count, success, barcode = process_failed_image(file_path)
                total_count += count
                if success:
                    valid_barcodes.append(barcode)
                else:
                    failed_images.append(file_path)
        
        print(f'Total de códigos de barras que comienzan con 8 y tienen 13 dígitos: {total_count}')
        save_results(valid_barcodes)
        if failed_images:
            save_failed_images(failed_images)
            retry_failed_images(failed_images, valid_barcodes)

def enhance_image(image, attempt):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if attempt == 1:
        gray = cv2.equalizeHist(gray)
    elif attempt == 2:
        gray = cv2.medianBlur(gray, 3)
    elif attempt == 3:
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)
    
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def process_failed_image(image_path):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    cropped_image = image[0:int(height * 0.2), 0:width]  # Tomar el 20% superior de la imagen
    
    count = 0
    success = False
    barcode = None
    try:
        # Aplicar técnicas adicionales de mejora
        for sigma in [1, 2, 3]:
            blurred = cv2.GaussianBlur(cropped_image, (0, 0), sigma)
            unsharp_image = cv2.addWeighted(cropped_image, 1.5, blurred, -0.5, 0)
            
            for attempt in range(1, 4):
                enhanced_image = enhance_image(unsharp_image, attempt)
                
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(unsharp_image, angle)
                    rotated_enhanced_image = rotate_image(enhanced_image, angle)
                    
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8') and len(barcode_data) == 13:
                            barcode_type = barcode_obj.type
                            print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                            count += 1
                            success = True
                            barcode = barcode_data
                            break
                    
                    if success:
                        break
                
                if success:
                    break
            
            if success:
                break
        
        # Aplicar técnicas adicionales si no se encuentra el código de barras
        if not success:
            kernel = np.ones((5,5),np.uint8)
            morph_image = cv2.morphologyEx(cropped_image, cv2.MORPH_CLOSE, kernel)
            for attempt in range(1, 4):
                enhanced_image = enhance_image(morph_image, attempt)
                
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(morph_image, angle)
                    rotated_enhanced_image = rotate_image(enhanced_image, angle)
                    
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8') and len(barcode_data) == 13:
                            barcode_type = barcode_obj.type
                            print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                            count += 1
                            success = True
                            barcode = barcode_data
                            break
                    
                    if success:
                        break
                
                if success:
                    break

        # Recortar y ampliar la imagen si aún no se encuentra el código de barras
        if not success:
            cropped_and_resized_image = resize_and_crop(image)
            for attempt in range(1, 4):
                enhanced_image = enhance_image(cropped_and_resized_image, attempt)
                
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(cropped_and_resized_image, angle)
                    rotated_enhanced_image = rotate_image(enhanced_image, angle)
                    
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8') and len(barcode_data) == 13:
                            barcode_type = barcode_obj.type
                            print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                            count += 1
                            success = True
                            barcode = barcode_data
                            break
                    
                    if success:
                        break
                
                if success:
                    break

        if not success:
            print(f'No se encontró un código de barras válido en la imagen {image_path} incluso después de técnicas adicionales')
    
    except Exception as e:
        print(f'Error procesando la imagen {image_path} con técnicas adicionales: {e}')
    
    return count, success, barcode

def retry_failed_images(failed_images, valid_barcodes):
    for file_path in failed_images:
        print(f'Reintentando con técnicas avanzadas en la imagen {file_path}')
        image = cv2.imread(file_path)
        height, width = image.shape[:2]
        cropped_image = image[0:int(height * 0.2), 0:width]  # Tomar el 20% superior de la imagen

        success = False
        barcode = None
        try:
            # Filtro bilateral y ajuste de brillo y contraste
            for attempt in range(1, 4):
                enhanced_image = apply_bilateral_filter(cropped_image, attempt)
                
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(enhanced_image, angle)
                    rotated_enhanced_image = adjust_brightness_contrast(rotated_image, attempt)
                    
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8') and len(barcode_data) == 13:
                            barcode_type = barcode_obj.type
                            print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                            success = True
                            barcode = barcode_data
                            valid_barcodes.append(barcode)
                            break
                    
                    if success:
                        break
                
                if success:
                    break

            # Aplicar filtro de Canny si aún no se encuentra el código de barras
            if not success:
                canny_image = apply_canny_edge(cropped_image)
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(canny_image, angle)
                    
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8') and len(barcode_data) == 13:
                            barcode_type = barcode_obj.type
                            print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                            success = True
                            barcode = barcode_data
                            valid_barcodes.append(barcode)
                            break
                    
                    if success:
                        break

            if not success:
                print(f'No se encontró un código de barras válido en la imagen {file_path} incluso después de técnicas avanzadas')

        except Exception as e:
            print(f'Error procesando la imagen {file_path} con técnicas avanzadas: {e}')

    save_results(valid_barcodes)

def read_barcodes_from_image(image_path):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    # Recortar la parte superior de la imagen (ajusta según sea necesario)
    cropped_image = image[0:int(height * 0.2), 0:width]  # Tomar el 20% superior de la imagen
    
    count = 0
    success = False
    barcode = None
    try:
        angles = [0, 90, 180, 270]
        found_barcode = None
        
        for attempt in range(1, 4):  # Intentar 3 técnicas de mejora diferentes
            enhanced_image = enhance_image(cropped_image, attempt)
            
            for angle in angles:
                rotated_image = rotate_image(cropped_image, angle)
                rotated_enhanced_image = rotate_image(enhanced_image, angle)
                
                barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])

                for barcode_obj in barcodes:
                    barcode_data = barcode_obj.data.decode('utf-8')
                    if barcode_data.startswith('8') and len(barcode_data) == 13:
                        barcode_type = barcode_obj.type
                        print(f'Código de barras: {barcode_data}, Tipo: {barcode_type}')
                        found_barcode = barcode_data
                        count += 1
                        success = True
                        barcode = barcode_data
                        break
                
                if found_barcode:
                    break
            
            if found_barcode:
                break
        
        if not found_barcode:
            print(f'No se encontró un código de barras válido en la imagen {image_path}')
    
    except Exception as e:
        print(f'Error procesando la imagen {image_path}: {e}')

    return count, success, barcode

def rotate_image(image, angle):
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (width, height))
    return rotated_image

def resize_and_crop(image):
    height, width = image.shape[:2]
    # Recortar la parte superior de la imagen
    cropped_image = image[0:int(height * 0.2), 0:width]
    # Ampliar la imagen
    resized_image = cv2.resize(cropped_image, (width * 2, height * 2))
    return resized_image

def apply_bilateral_filter(image, attempt):
    if attempt == 1:
        return cv2.bilateralFilter(image, 9, 75, 75)
    elif attempt == 2:
        return cv2.bilateralFilter(image, 12, 100, 100)
    elif attempt == 3:
        return cv2.bilateralFilter(image, 15, 150, 150)
    return image

def adjust_brightness_contrast(image, attempt):
    if attempt == 1:
        return cv2.convertScaleAbs(image, alpha=1.5, beta=50)
    elif attempt == 2:
        return cv2.convertScaleAbs(image, alpha=2.0, beta=50)
    elif attempt == 3:
        return cv2.convertScaleAbs(image, alpha=2.5, beta=50)
    return image

def apply_canny_edge(image):
    edges = cv2.Canny(image, 100, 200)
    return cv2.bitwise_not(edges)

def save_results(barcodes):
    with open('resultados_barcodes.txt', 'w') as file:
        for barcode in barcodes:
            file.write(f'{barcode}\n')
    print('Resultados guardados en resultados_barcodes.txt')

def save_failed_images(failed_images):
    failed_dir = 'imagenes_fallidas'
    os.makedirs(failed_dir, exist_ok=True)
    for file_path in failed_images:
        shutil.copy(file_path, failed_dir)
    print(f'Imágenes fallidas guardadas en la carpeta {failed_dir}')

# Llamar a la función para seleccionar las imágenes
select_images()
