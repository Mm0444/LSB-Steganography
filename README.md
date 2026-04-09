<div align="center">
  <h1>LSB-Steganography Web Application🔐</h1>
   <p>
    <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-Web%20Framework-green" alt="Flask" />
    <img src="https://img.shields.io/badge/OpenCV-Image%20Processing-red" alt="OpenCV" />
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
  </p>
</div>

---

## 📌 Overview

LSB-Steganography is a web-based application that allows users to **hide and extract secret messages within images** using the *Least Significant Bit (LSB)* technique.

The application provides a simple and intuitive interface for encoding and decoding messages, making it suitable for educational purposes, demonstrations, and basic secure communication experiments.

---

## 🧠 What is LSB Steganography?

Least Significant Bit (LSB) steganography is a technique used to embed data into digital images by modifying the least significant bits of pixel values.

Example:

```
Original pixel: 10110010
Modified pixel: 10110011
```

The change is minimal and usually invisible to the human eye.

---

## 🚀 Features

* 🔐 Encode secret messages into images
* 🔓 Decode hidden messages from images
* 🖼️ Upload and download image files
* 🔒 Optional encryption (Fernet)

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, JavaScript
* **Image Processing:** OpenCV, NumPy
* **Encryption:** Cryptography (Fernet)
* **Database (optional):** SQLite / SQLAlchemy

---

## 📂 Project Structure

```
LSB-Steganography/
│
├── app.py              # Flask backend
├── lsb.py              # Core steganography logic
├── templates/          # HTML templates
├── static/             # CSS & JavaScript files
├── uploads/            # Encoded images (optional)
├── database.db         # SQLite database (optional)
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/Mm0444/LSB-Steganography.git 
cd LSB-Steganography
```

### 2️⃣ Install dependencies

```
python -m pip install -r requirements.txt
```

### 3️⃣ Run the application

```
python app.py
```

### 4️⃣ Open in browser

```
http://127.0.0.1:8080
```

---

## 🔄 How It Works

### 🔐 Encoding Process

1. User uploads an image
2. Input message is converted to binary
3. Binary data is embedded into image pixels (LSB)
4. Encoded image is generated for download

### 🔓 Decoding Process

1. User uploads encoded image
2. System reads least significant bits
3. Binary data is reconstructed
4. Original message is displayed

---

## 💡 Use Cases

* Secure message hiding
* Digital watermarking
* Cybersecurity learning
* Data embedding experiments

---

## ⚠️ Limitations

* Works best with **PNG images** (lossless format)
* JPEG compression may destroy hidden data
* Not suitable for high-security applications

---


## 📜 License

This project is licensed under the MIT License.

---
