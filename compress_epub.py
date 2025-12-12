#!/usr/bin/env python3
"""
Скрипт для сжатия EPUB файла для Kindle
Оптимизирует изображения и удаляет ненужные ресурсы
"""

import zipfile
import os
import io
from PIL import Image
import sys
from pathlib import Path

# Поддерживаемые форматы изображений
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
MAX_IMAGE_WIDTH = 1920  # Максимальная ширина для Kindle
MAX_IMAGE_HEIGHT = 2560  # Максимальная высота для Kindle
JPEG_QUALITY = 85  # Качество JPEG (85-90 для сохранения ~90% качества)
PNG_OPTIMIZE = True


def get_file_size_mb(filepath):
    """Получить размер файла в МБ"""
    return os.path.getsize(filepath) / (1024 * 1024)


def optimize_image(image_data, filename):
    """
    Оптимизирует изображение
    Возвращает оптимизированные данные изображения
    """
    try:
        # Открываем изображение из байтов
        img = Image.open(io.BytesIO(image_data))
        original_format = img.format
        original_size = img.size
        
        # Конвертируем RGBA в RGB для JPEG
        if img.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон для прозрачных изображений
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Уменьшаем размер если слишком большой
        width, height = img.size
        if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
            img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        
        # Сохраняем в JPEG для лучшего сжатия
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        output.seek(0)
        
        new_size = len(output.getvalue())
        original_size_bytes = len(image_data)
        compression_ratio = (1 - new_size / original_size_bytes) * 100
        
        print(f"  Оптимизировано: {filename} "
              f"({original_size[0]}x{original_size[1]}) "
              f"{original_size_bytes/1024:.1f}KB -> {new_size/1024:.1f}KB "
              f"({compression_ratio:.1f}% сжатие)")
        
        return output.getvalue()
    
    except Exception as e:
        print(f"  Ошибка при оптимизации {filename}: {e}")
        return image_data  # Возвращаем оригинал при ошибке


def compress_epub(input_file, output_file, target_size_mb=49):
    """
    Сжимает EPUB файл
    """
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден")
        return False
    
    original_size = get_file_size_mb(input_file)
    print(f"Исходный размер: {original_size:.2f} МБ")
    print(f"Целевой размер: {target_size_mb} МБ")
    print(f"Необходимое сжатие: {(1 - target_size_mb/original_size)*100:.1f}%")
    print("\nНачинаю обработку...\n")
    
    # Создаем временную директорию для работы
    temp_dir = Path(output_file).parent / "temp_epub"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Открываем исходный EPUB
        with zipfile.ZipFile(input_file, 'r') as input_zip:
            # Создаем новый EPUB
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as output_zip:
                total_files = len(input_zip.namelist())
                processed_files = 0
                images_optimized = 0
                total_original_size = 0
                total_compressed_size = 0
                
                for file_info in input_zip.infolist():
                    filename = file_info.filename
                    processed_files += 1
                    
                    # Пропускаем служебные файлы macOS
                    if filename.startswith('__MACOSX/') or filename.endswith('.DS_Store'):
                        continue
                    
                    file_data = input_zip.read(filename)
                    original_file_size = len(file_data)
                    total_original_size += original_file_size
                    
                    # Проверяем, является ли файл изображением
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in IMAGE_EXTENSIONS:
                        print(f"[{processed_files}/{total_files}] Обработка изображения: {filename}")
                        optimized_data = optimize_image(file_data, filename)
                        total_compressed_size += len(optimized_data)
                        images_optimized += 1
                        output_zip.writestr(file_info, optimized_data)
                    else:
                        # Для не-изображений просто копируем
                        total_compressed_size += original_file_size
                        output_zip.writestr(file_info, file_data)
                
                print(f"\n{'='*60}")
                print(f"Обработано файлов: {processed_files}")
                print(f"Оптимизировано изображений: {images_optimized}")
                print(f"Исходный размер: {total_original_size / (1024*1024):.2f} МБ")
                print(f"Размер после сжатия: {total_compressed_size / (1024*1024):.2f} МБ")
        
        # Проверяем финальный размер
        final_size = get_file_size_mb(output_file)
        compression_achieved = (1 - final_size/original_size) * 100
        
        print(f"\n{'='*60}")
        print(f"РЕЗУЛЬТАТ:")
        print(f"Исходный размер: {original_size:.2f} МБ")
        print(f"Финальный размер: {final_size:.2f} МБ")
        print(f"Достигнутое сжатие: {compression_achieved:.1f}%")
        
        if final_size <= target_size_mb:
            print(f"✓ Цель достигнута! Файл меньше {target_size_mb} МБ")
        else:
            print(f"⚠ Файл все еще больше {target_size_mb} МБ")
            print(f"  Можно попробовать:")
            print(f"  - Уменьшить JPEG_QUALITY до 80")
            print(f"  - Уменьшить MAX_IMAGE_WIDTH/HEIGHT")
        
        return True
    
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Удаляем временную директорию
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Использование: python compress_epub.py <input.epub> [output.epub] [target_size_mb]")
        print("\nПример:")
        print("  python compress_epub.py book.epub")
        print("  python compress_epub.py book.epub book_compressed.epub")
        print("  python compress_epub.py book.epub book_compressed.epub 49")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Создаем имя выходного файла автоматически
        path = Path(input_file)
        output_file = str(path.parent / f"{path.stem}_compressed{path.suffix}")
    
    target_size_mb = 49
    if len(sys.argv) >= 4:
        try:
            target_size_mb = float(sys.argv[3])
        except ValueError:
            print(f"Предупреждение: неверное значение target_size_mb, использую {target_size_mb}")
    
    print("="*60)
    print("EPUB Compressor для Kindle")
    print("="*60)
    print()
    
    success = compress_epub(input_file, output_file, target_size_mb)
    
    if success:
        print("\n✓ Готово! Файл сохранен как:", output_file)
    else:
        print("\n✗ Произошла ошибка при обработке")
        sys.exit(1)


if __name__ == "__main__":
    main()

