# FTP CSV Validator GUI

A Python-based desktop application that connects to an FTP server, lists available CSV files, and allows users to download and validate them through a user-friendly graphical interface. The application also includes integrated CI/CD pipelines using GitHub Actions and Docker for automated building, testing, and deployment.

---

## 🚀 Features

- Connect to an FTP server using host and login credentials
- List and search CSV files available on the server
- Select and download CSV files from the server
- Automatically validate CSV files
  - ✅ Valid files are saved in the valid folder
  - ❌ Invalid files trigger an error log
- Simple and intuitive GUI built with Tkinter
- Continuous integration and deployment using GitHub Actions and Docker
- GUI compatibility in Docker using Xming (for Windows)

---

## 📦 Requirements

Ensure you have the following installed in your system:

### 🔧 Python Modules (Standard & External)

- `os` – for file and path handling
- `re` – for regular expression matching
- `csv` – for reading/writing CSV files
- `logging` – for error and event logging
- `requests` – for HTTP operations
- `ftplib` – for FTP server operations
- `datetime` – to work with date and time
- `tkinter` – for building the graphical user interface
  - Components used: `Button`, `Entry`, `END`, `Frame`, `messagebox`, `Listbox`, `Label`, `StringVar`, `Scrollbar`, `Tk`

Install external dependencies with:

```bash
pip install -r requirements.txt
