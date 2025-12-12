
# **EPUB Compressor for Kindle**

A lightweight tool that compresses EPUB files by optimizing images while preserving ~90% visual quality — perfect for sending large books to your Kindle.

---

## 🚀 **Quick Start with Google Colab (Recommended!)**

**The easiest and fastest way to use this tool is via Google Colab. Zero setup required.**

1. Open the `compress_epub_colab.ipynb` notebook in Google Colab

   * Upload it directly to [Google Colab](https://colab.research.google.com/), **or**
   * Create a new notebook and paste the code from `compress_epub_colab.ipynb`

2. Run all cells in order:

   * **Cell 1:** installs dependencies
   * **Cell 2:** imports libraries
   * **Cell 3:** loads helper functions
   * **Cell 4:** lets you upload your EPUB (just pick a file!)
   * **Cell 5:** starts the compression process
   * **Cell 6:** downloads the final compressed file

**That's it. No configuration. No environment issues. Just smooth compression.**

---

## 💻 **Local Usage**

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

or minimal install:

```bash
pip install Pillow
```

---

## ▶️ **How to Use**

### **Basic usage**

```bash
python compress_epub.py book.epub
```

This will generate `book_compressed.epub` in the same folder.

---

### **Specify custom output**

```bash
python compress_epub.py book.epub compressed_book.epub
```

---

### **Specify target size (in MB)**

```bash
python compress_epub.py book.epub compressed_book.epub 49
```

---

## 🧠 **How It Works**

### 1. **Image Optimization**

* Converts all images to **JPEG (quality=85%)**
* Resizes images to a maximum of **1920×2560** (ideal Kindle dimensions)
* Removes transparency and converts to **RGB**
* Downscales oversized images for better compression

### 2. **EPUB Repack & Compression**

* Rebuilds the EPUB using **ZIP level=9**
* Preserves metadata and EPUB internal structure
* Only images are modified — text stays untouched

### 3. **High quality preserved**

* JPEG quality 85% → ~90% visual fidelity
* Image resolution is tuned for Kindle’s e-ink and Kindle app screens

---

## ⚙️ **Customizing Compression Settings**

Open `compress_epub.py` and tweak these values:

```python
MAX_IMAGE_WIDTH = 1920   # Try 1200–1600 for stronger compression
MAX_IMAGE_HEIGHT = 2560  # Try 1600–2000
JPEG_QUALITY = 85        # Lower to 80 for smaller size
```

If you need to bring a **700 MB EPUB → 49 MB**, you’ll likely iterate these settings once or twice.

---

## 📌 Notes & Tips

* Text files inside the EPUB remain unchanged
* All images are converted to JPEG for optimal compression
* Multiple passes may be required for strict target sizes
* Works well for manga, illustrated books, textbooks, scanned materials, and image-heavy EPUBs

---

## 📁 **Project Files**

* `compress_epub_colab.ipynb` — **Recommended notebook for Colab**
* `compress_epub.py` — Main script for local usage
* `compress_epub_colab.py` — Alternative `.py` version for Colab users


