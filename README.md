# LSB Steganography Web App

This is a complete web application that lets you hide secret messages within images using Least Significant Bit (LSB) steganography. Built with Flask, OpenCV, NumPy, Cryptography, and a beautiful Bootstrap 5 frontend featuring a glassmorphism design.

## Features
- **Encode**: Upload any image (PNG/JPG), enter a text message, and hide it inside the image.
- **Decode**: Upload an encoded image to extract the hidden message.
- **Optional Encryption**: Securely encrypt your messages with a password before hiding them inside the image using Fernet (AES).
- **Modern UI**: Smooth interface with glass cards, drag & drop image uploads, async file handling, and gradient text.

## Project Structure
```
LSB-Steganography/
├── app.py                  # Flask backend server
├── lsb.py                  # Core steganography & encryption logic
├── requirements.txt        # Python dependency list
├── README.md               # Setup instructions
├── templates/
│   └── index.html          # Frontend HTML user interface
└── static/
    ├── css/
    │   └── style.css       # Custom styling (animations, themes)
    └── js/
        └── script.js       # Client side API requests & UI logic
```

## How to Install and Run

### Prerequisites
- Python 3.8+ installed on your system.

### 1. Install Dependencies
Open a terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Run the App
Launch the Flask server:
```bash
python app.py
```

### 3. Open the Application
Open your web browser and go to:
[http://localhost:8080](http://localhost:8080)

## Security Note regarding Images
When downloading an encoded image, it will be saved as a `.png` file. This is crucial because **PNG is a lossless format**. If you convert it or send it through platforms that heavily compress images (like WhatsApp or Facebook Messenger), the Least Significant Bits may be scrambled, and the message will be lost!

## Technology Output
- Python + Flask
- OpenCV
- NumPy
- Cryptography (Fernet symmetric encryption)
- Bootstrap 5
- JavaScript Fetch API
