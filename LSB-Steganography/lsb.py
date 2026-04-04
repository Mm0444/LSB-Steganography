import cv2
import numpy as np
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

DELIMITER = "#####"

# EOF Delimiters for General Files (Videos, Documents)
FILE_START_DELIMITER = b"<-STEG_START->"
FILE_END_DELIMITER = b"<-STEG_END->"

def _get_key(password):
    """Generate a valid Fernet key from the user's password."""
    password_bytes = password.encode('utf-8')
    salt = b'LSB_Stego_Salt'  # A static salt for simplicity
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key

def encrypt_message(message, password):
    """Encrypts a message using a password."""
    if not password:
        return message
    key = _get_key(password)
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode('utf-8')).decode('utf-8')
    return encrypted_message

def decrypt_message(encrypted_message, password):
    """Decrypts a message using a password."""
    if not password:
        return encrypted_message
    
    try:
        key = _get_key(password)
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message.encode('utf-8')).decode('utf-8')
        return decrypted_message
    except Exception as e:
        raise ValueError("Invalid password or corrupted data.")

def text_to_binary(text):
    """Convert string text to binary."""
    return ''.join(format(ord(i), '08b') for i in text)

def binary_to_text(binary):
    """Convert binary string back to text."""
    binary_values = [binary[i: i+8] for i in range(0, len(binary), 8)]
    ascii_chars = [chr(int(b, 2)) for b in binary_values]
    return ''.join(ascii_chars)

def encode(image_path, secret_message, password=None, output_dir=None):
    """
    Encode secret message into an image.
    Returns the path to the newly encoded image.
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be read.")
    
    # 1. Encrypt message if password is provided
    if password:
        secret_message = encrypt_message(secret_message, password)
        
    # 2. Append delimiter to know when to stop reading bits
    secret_message += DELIMITER
    binary_message = text_to_binary(secret_message)
    data_len = len(binary_message)
    
    # Check if image has enough pixels to hold the data
    total_pixels_bytes = image.shape[0] * image.shape[1] * 3
    if data_len > total_pixels_bytes:
        raise ValueError("Error: Need a larger image to hide this much data.")
    
    data_index = 0
    # Flatten the image array to process pixels sequentially
    flattened = image.flatten()
    
    # 3. Embed data into the least significant bits (LSB)
    for i in range(data_len):
        # Convert pixel value to binary, clear LSB, and add the current data bit
        pixel_bin = format(flattened[i], '08b')
        new_pixel = pixel_bin[:-1] + binary_message[data_index]
        flattened[i] = int(new_pixel, 2)
        data_index += 1
    
    # Reshape back to original dimensions
    encoded_image = flattened.reshape(image.shape)
    
    # Save the modified image as PNG to avoid lossy compression (which breaks LSB)
    output_filename = os.path.basename(os.path.splitext(image_path)[0]) + "_encoded.png"
    if output_dir:
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = os.path.join(os.path.dirname(image_path), output_filename)
    
    cv2.imwrite(output_path, encoded_image)
    return output_path

def decode(image_path, password=None):
    """
    Decode secret message from an image.
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be read.")
        
    binary_data = ""
    # Flatten the image array
    flattened = image.flatten()
    
    # Extract the LSB from all relevant pixels
    extracted_text = ""
    byte_str = ""
    
    for pixel in flattened:
        byte_str += format(pixel, '08b')[-1]
        
        # When we have exactly 8 bits (1 byte)
        if len(byte_str) == 8:
            char = chr(int(byte_str, 2))
            extracted_text += char
            byte_str = ""
            
            # Check if we hit the delimiter
            if extracted_text.endswith(DELIMITER):
                # Remove delimiter
                encrypted_message = extracted_text[:-len(DELIMITER)]
                # Decrypt if password provided
                if password:
                    return decrypt_message(encrypted_message, password)
                return encrypted_message
            
    raise ValueError("No hidden message found or wrong delimiter used.")

def encode_file(file_path, secret_message, password=None, output_dir=None):
    """
    Encode secret message into ANY file using EOF Appending.
    """
    if password:
        secret_message = encrypt_message(secret_message, password)
        
    payload = FILE_START_DELIMITER + secret_message.encode('utf-8') + FILE_END_DELIMITER
    
    with open(file_path, "rb") as f:
        file_data = f.read()
        
    # Prevent double encoding (or appending again to already encoded file)
    if payload in file_data:
        raise ValueError("File is already encoded with this exact data.")
        
    encoded_data = file_data + payload
    
    filename, ext = os.path.splitext(os.path.basename(file_path))
    output_filename = filename + "_encoded" + ext
    
    if output_dir:
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = os.path.join(os.path.dirname(file_path), output_filename)
        
    with open(output_path, "wb") as f:
        f.write(encoded_data)
        
    return output_path

def decode_file(file_path, password=None):
    """
    Decode secret message from a file using EOF Appending.
    """
    with open(file_path, "rb") as f:
        file_data = f.read()
        
    start_idx = file_data.rfind(FILE_START_DELIMITER)
    end_idx = file_data.rfind(FILE_END_DELIMITER)
    
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        raise ValueError("No hidden message found (or corrupted signature).")
        
    # Extract payload
    start_payload = start_idx + len(FILE_START_DELIMITER)
    encrypted_message_bytes = file_data[start_payload:end_idx]
    
    try:
        encrypted_message = encrypted_message_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Extracted payload contains invalid characters.")
    
    if password:
        return decrypt_message(encrypted_message, password)
    return encrypted_message
