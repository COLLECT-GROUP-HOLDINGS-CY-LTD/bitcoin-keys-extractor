#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import hashlib
import sys
import subprocess
import os


# ========== ФУНКЦИЯ ДЛЯ СБОРКИ В EXE ==========
def resource_path(relative_path):
    """Получение корректного пути к ресурсам для PyInstaller"""
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ========== ОРИГИНАЛЬНЫЙ КОД С ИСПРАВЛЕНИЯМИ ==========
# Base58 alphabet
B58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def b58decode(b58_str: str) -> bytes:
    num = 0
    for ch in b58_str.encode('ascii'):
        idx = B58_ALPHABET.find(bytes([ch]))
        if idx == -1:
            raise ValueError(f"Invalid base58 char: {chr(ch)}")
        num = num * 58 + idx
    combined = num.to_bytes((num.bit_length() + 7) // 8, 'big') or b'\x00'
    # leading '1's -> leading zeros
    n_pad = len(b58_str) - len(b58_str.lstrip('1'))
    return b'\x00' * n_pad + combined


def base58check_decode(s: str) -> bytes:
    raw = b58decode(s)
    data, checksum = raw[:-4], raw[-4:]
    hashed = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    if checksum != hashed:
        raise ValueError("Invalid checksum")
    return data


def wif_to_privkey(wif: str) -> bytes:
    decoded = base58check_decode(wif)
    if decoded[0] not in (0x80, 0xEF):  # mainnet/testnet
        raise ValueError("Invalid WIF version byte")
    priv = decoded[1:33]
    return priv


def priv_to_compressed_pubkey(priv: bytes) -> str:
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub_bytes = vk.to_string()
    x, y = pub_bytes[:32], pub_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
    return (prefix + x).hex()


def center_window(win, width, height):
    """Center a Tkinter window on the screen"""
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


# --- GUI Functions ---
def convert():
    wif = entry.get().strip()
    if not wif:
        messagebox.showwarning("Missing input", "Please enter a WIF key")
        return
    try:
        priv = wif_to_privkey(wif)
        pub_hex = priv_to_compressed_pubkey(priv)
        result.delete("1.0", tk.END)
        result.insert("1.0", pub_hex)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_to_clipboard():
    pub_hex = result.get("1.0", tk.END).strip()
    if not pub_hex:
        messagebox.showinfo("No output", "Nothing to copy yet.")
        return
    root.clipboard_clear()
    root.clipboard_append(pub_hex)
    root.update()
    messagebox.showinfo("Copied", "Public key copied to clipboard!")


# --- Disclaimer Page ---
def show_main_app():
    disclaimer_win.destroy()

    global root, entry, result
    root = tk.Tk()
    root.title("WIF → Public Key")
    root.geometry("600x250")
    root.resizable(False, False)
    center_window(root, 600, 250)

    tk.Label(root, text="Enter WIF Private Key:").pack(pady=5)
    # Entry with hidden text (asterisks)
    entry = tk.Entry(root, width=80, show="*")
    entry.pack(pady=5)

    tk.Button(root, text="Convert", command=convert).pack(pady=5)

    tk.Label(root, text="Public Key (can be shared, send it to the tech team):").pack()
    result = tk.Text(root, height=3, width=80)
    result.pack(pady=5)

    tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)

    root.mainloop()


# ========== ОСНОВНОЙ БЛОК С ИСПРАВЛЕНИЯМИ ==========
if __name__ == "__main__":
    # УБЕРИТЕ динамическую установку зависимостей из кода!
    # Вместо этого установите их заранее:
    # pip install ecdsa
    # или создайте requirements.txt

    try:
        from ecdsa import SigningKey, SECP256k1
    except ImportError as e:
        messagebox.showerror(
            "Missing Dependency",
            f"Please install ecdsa first:\n\n"
            f"Open terminal and run:\n"
            f"pip install ecdsa\n\n"
            f"Error: {str(e)}"
        )
        sys.exit(1)

    # --- Start with Disclaimer Window ---
    disclaimer_win = tk.Tk()
    disclaimer_win.title("Disclaimer")
    disclaimer_win.geometry("600x300")
    disclaimer_win.resizable(False, False)
    center_window(disclaimer_win, 600, 300)

    disclaimer_text = (
        "⚠️ IMPORTANT DISCLAIMER ⚠️\n\n"
        "This tool is for LOCAL use only.\n\n"
        "- NEVER share your private key online.\n"
        "- NEVER send your private key to anyone, not even tech team.\n"
        "- Use this app only on a secure, offline computer if possible.\n\n"
        "Click 'I Understand' to continue."
    )

    label = tk.Label(disclaimer_win, text=disclaimer_text, wraplength=550, justify="left", padx=20, pady=20)
    label.pack()

    btn = tk.Button(disclaimer_win, text="I Understand", command=show_main_app)
    btn.pack(pady=20)

    disclaimer_win.mainloop()