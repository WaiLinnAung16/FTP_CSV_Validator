import os
import re
import csv
import logging
import requests
import ftplib
from datetime import datetime
from tkinter import Button, Entry, END, Frame, messagebox, Listbox, Label, StringVar, Scrollbar, Tk

# === CONFIGURATION ===
VALID_DIR = "valid_files"
ERROR_LOG_DIR = "error_logs"
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, "error_log.txt")
EXPECTED_HEADERS = ["batch_id", "timestamp"] + \
    [f"reading{i}" for i in range(1, 11)]


class FTPClient:
    def __init__(self):
        self.ftp = None
        self.downloaded_files = []

    def connect(self, host, user, password):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host)
        self.ftp.login(user, password)
        return True, "Connected to FTP server"

    def disconnect(self):
        self.ftp.quit()
        return False, "Disconnected to FTP server"

    def get_ftp_list(self):
        return self.ftp.nlst()

    def is_connected(self):
        return self.ftp is not None

    def search_files(self, keyword):
        all_files = self.get_ftp_list()
        matched_files = [f for f in all_files if keyword in f]

        if not matched_files:
            messagebox.showerror('Error', "There is no file with this name!")

        return matched_files

    def download_file(self, filename):
        # content = []
        # self.ftp.retrbinary(f'RETR {filename}', content.append)
        # return "\n".join(content)
        from io import StringIO
        content = []

        def handle_binary(data):
            content.append(data.decode("utf-8"))

        self.ftp.retrbinary(f'RETR {filename}', callback=handle_binary)
        return ''.join(content)


class FileValidator:
    @staticmethod
    def validate(file_content):
        try:
            reader = csv.reader(file_content.splitlines())
            headers = next(reader, None)

            if not FileValidator.validate_headers(headers):
                return False, f"Incorrect or missing headers: {headers}"

            batch_ids = set()
            for row_num, row in enumerate(reader, start=2):
                if not FileValidator.validate_row_length(row):
                    return False, f"Row {row_num} has missing columns"
                if not FileValidator.validate_unique_batch_id(row[0], batch_ids):
                    return False, f"Duplicate batch_id {row[0]} on row {row_num}"
                is_valid, msg = FileValidator.validate_readings(
                    row[2:], row_num)
                if not is_valid:
                    return False, msg

        except Exception as e:
            return False, f"Malformed file error: {str(e)}"
        return True, "Valid"

    @staticmethod
    def validate_headers(headers):
        return headers == EXPECTED_HEADERS

    @staticmethod
    def validate_row_length(row):
        return len(row) == 12

    @staticmethod
    def validate_unique_batch_id(batch_id, batch_ids):
        if batch_id in batch_ids:
            return False
        batch_ids.add(batch_id)
        return True

    @staticmethod
    def validate_readings(readings, row_num):
        for i, reading in enumerate(readings, start=1):
            try:
                value = float(reading)
                if value > 9.9:
                    return False, f"Value exceeds 9.9 in reading{i} on row {row_num}: {value}"
                if not re.match(r"^\d+(\.\d{1,3})?$", reading):
                    return False, f"Invalid decimal format in reading{i} on row {row_num}: {reading}"
            except ValueError:
                return False, f"Non-numeric reading{i} on row {row_num}: {reading}"
        return True, None


class Logger:
    def __init__(self):
        self.ensure_directories()
        # Clear the error log file at startup
        if os.path.exists(ERROR_LOG_FILE):
            # Truncate the file to clear old logs
            open(ERROR_LOG_FILE, 'w').close()
        logging.basicConfig(
            filename=ERROR_LOG_FILE,
            filemode='a',  # Append mode ensures new logs are added
            level=logging.ERROR,
            format="%(asctime)s - ERROR - [UUID: %(uuid)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def ensure_directories(self):
        os.makedirs(VALID_DIR, exist_ok=True)
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)

    def get_uuid(self):
        try:
            response = requests.get(
                "https://www.uuidtools.com/api/generate/v1")
            response.raise_for_status()
            uuid_list = response.json()
            return uuid_list[0] if uuid_list else "unknown_uuid"
        except Exception as e:
            logging.error(f"UUID generation failed: {str(e)}", extra={
                          "uuid": "unknown_uuid"})
            return "unknown_uuid"

    def log(self, message):
        uuid = self.get_uuid()
        logging.error(message, extra={"uuid": uuid})


class App:
    def __init__(self, root):
        self.root = root
        self.files = None
        self.file_listbox = None
        self.valid_files_listbox = None
        self.error_logs_listbox = None
        self.search_var = StringVar()
        self.ftp_client = FTPClient()
        self.logger = Logger()
        self.build_gui()

    def ftp_client_connect(self):
        try:
            self.ftp_client.connect(
                self.host_var.get(), self.user_var.get(), self.pass_var.get())

            # Change entry state to disabled
            self.host_entry.config(state='disabled')
            self.user_entry.config(state='disabled')
            self.pass_entry.config(state='disabled')

            # Connection Button
            self.ftp_connect_btn.config(
                text="Disconnect", bg='red', command=self.ftp_client_disconnect)
            messagebox.showinfo("Success", "Connected to FTP Server")

            self.list_files()
        except Exception as e:
            messagebox.showerror("Error", f"FTP connection failed: {e}")

    def ftp_client_disconnect(self):
        try:
            self.ftp_client.disconnect()
            # Change state to normal to type again
            self.host_entry.config(state='normal')
            self.user_entry.config(state='normal')
            self.pass_entry.config(state='normal')
            # Clear entry values
            self.host_var.set("")
            self.user_var.set("")
            self.pass_var.set("")

            self.search_var.set('')

            # Connection Button
            self.ftp_connect_btn.config(
                text="Connect to FTP", command=self.ftp_client_connect, bg='teal')
            messagebox.showinfo(
                "Disconnected", "Disconnected from FTP Server")

            self.remove_files()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")

    def list_files(self):
        try:
            self.files = self.ftp_client.get_ftp_list()
            self.file_listbox.delete(0, END)
            for file in self.files:
                self.file_listbox.insert(END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {e}")

    def remove_files(self):
        self.files = None
        self.file_listbox.delete(0, END)

    def download_file(self):
        if not self.ftp_client.is_connected():
            messagebox.showerror("Error", "Not connected to FTP")
            return

        selected_file = self.file_listbox.curselection()
        if not selected_file:
            messagebox.showerror("Error", "No file selected")
            return

        filename = self.file_listbox.get(selected_file)
        if filename in self.ftp_client.downloaded_files:
            messagebox.showwarning(
                "Warning", f"File '{filename}' already downloaded or attempted.")
            return

        self.download_status.config(text="Downloading...", foreground="blue")
        self.download_btn.config(state="disabled", bg="white")

        def after_delay():
            if not filename.lower().endswith('.csv'):
                self.download_status.config(
                    text="Fail", foreground="red")
                error_msg = f"Invalid file extension for '{filename}'. Only '.csv' files are allowed."
                self.logger.log(error_msg)
                self.load_error_logs()
                messagebox.showerror("Invalid File", error_msg)
                self.ftp_client.downloaded_files.append(filename)
                self.download_status.config(text="Idle", foreground="black")
                self.download_btn.config(state="normal", bg="teal")
                return

            try:
                size = self.ftp_client.ftp.size(filename)
                if size == 0:
                    self.download_status.config(
                        text="Fail", foreground="red")
                    error_msg = f"File '{filename}' is empty (zero size)."
                    self.logger.log(error_msg)
                    self.load_error_logs()
                    messagebox.showwarning("Warning", error_msg)
                    self.ftp_client.downloaded_files.append(filename)
                    self.download_status.config(
                        text="Idle", foreground="black")
                    self.download_btn.config(state="normal", bg="teal")
                    return
            except Exception as e:
                self.download_status.config(
                    text="Fail", foreground="red")
                self.logger.log(f"Download size check error: {str(e)}")
                self.load_error_logs()
                self.ftp_client.downloaded_files.append(filename)
                self.download_status.config(text="Idle", foreground="black")
                self.download_btn.config(state="normal", bg="teal")
                return

            try:
                content = self.ftp_client.download_file(filename)
                valid, msg = FileValidator.validate(content)
                if valid:
                    self.download_status.config(
                        text="Success", foreground="green")
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    new_filename = f"MED_DATA_{timestamp}.csv"
                    path = os.path.join(VALID_DIR, new_filename)
                    with open(path, 'w') as f:
                        f.write(content)
                    self.valid_files_listbox.insert(END, new_filename)
                    self.valid_files_listbox.see(END)
                    self.valid_files_listbox.selection_clear(0, END)
                    self.valid_files_listbox.selection_set(END)
                    messagebox.showinfo(
                        "Success", f"File saved as '{new_filename}' in '{VALID_DIR}'.")
                else:
                    self.download_status.config(
                        text="Fail", foreground="red")
                    self.logger.log(
                        f"Validation failed for '{filename}': {msg}")
                    self.load_error_logs()
                    messagebox.showerror("Validation Error",
                                         f"Validation failed:\n{msg}")
            except Exception as e:
                self.download_status.config(
                    text="Fail", foreground="red")
                self.logger.log(f"Download error: {str(e)}")
                self.load_error_logs()
                messagebox.showerror(
                    "Download Error", f"Failed to download/process file:\n{e}")
            finally:
                self.ftp_client.downloaded_files.append(filename)
                self.download_status.config(text="Idle", foreground="black")
                self.download_btn.config(state="normal", bg="teal")

        self.download_status.after(
            3000, after_delay)

    def load_error_logs(self):
        """Load error logs from the file and update the error_logs_listbox."""
        try:
            if os.path.exists(ERROR_LOG_FILE):
                with open(ERROR_LOG_FILE, "r") as file:
                    logs = file.readlines()
                self.error_logs_listbox.delete(0, END)
                for log in logs:
                    self.error_logs_listbox.insert(END, log.strip())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load error logs: {e}")

    def searchFileName(self):
        if not self.ftp_client.is_connected():
            messagebox.showerror("Error", "Not connected to FTP")
            return
        search_value = self.search_var.get().strip()
        if not search_value:
            messagebox.showerror("Error", "Please enter search keyword")
            return
        try:
            found_files = self.ftp_client.search_files(search_value)
            self.file_listbox.delete(0, END)
            for file in found_files:
                self.file_listbox.insert(END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

    def clearSearch(self):
        self.search_var.set('')
        self.list_files()

    def build_gui(self):
        self.root.title("FTP CSV Validator")
        self.root.geometry("800x600")

        main_frame = Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Connection Frame
        navbar_header = Frame(main_frame)
        navbar_header.pack(fill="x")

        # Header
        Label(navbar_header, text="FTP Connection",
              font=("Arial", 12, "bold")).pack(side="left")
        navbar_frame = Frame(main_frame)
        navbar_frame.pack(fill="x", pady=15)

        # Hostname Entry
        Label(navbar_frame, text="Hostname").pack(side="left")
        self.host_var = StringVar()
        self.host_entry = Entry(navbar_frame, textvariable=self.host_var)
        self.host_entry.pack(side="left", padx=10)

        # Username Entry
        Label(navbar_frame, text="Username").pack(side="left")
        self.user_var = StringVar()
        self.user_entry = Entry(navbar_frame, textvariable=self.user_var)
        self.user_entry.pack(side="left", padx=10)

        # Password Entry
        Label(navbar_frame, text="Password").pack(side="left")
        self.pass_var = StringVar()
        self.pass_entry = Entry(
            navbar_frame, textvariable=self.pass_var, show='*')
        self.pass_entry.pack(side="left", padx=10)

        # FTP Server Connection Button
        self.ftp_connect_btn = Button(
            navbar_frame,
            text="Connect to FTP",
            command=self.ftp_client_connect,
            width=20,
            background='teal',
            foreground='white',
            activeforeground='teal'
        )
        self.ftp_connect_btn.pack(side="right")

        # File List Header Frame
        file_header_frame = Frame(main_frame)
        file_header_frame.pack(fill="both", expand=True, pady=10)
        Label(file_header_frame, text="Available Files",
              font=("Arial", 12, "bold")).pack(side="left")
        # Search Entry and Buttons
        Button(file_header_frame, command=self.clearSearch, text="Clear Search", width=10, pady=0, foreground='teal',
               ).pack(side="right")
        Button(file_header_frame, command=self.searchFileName, text="Search", width=10, pady=0, foreground='teal'
               ).pack(side="right", padx=3)
        Entry(file_header_frame, textvariable=self.search_var,
              width=30).pack(side="right")

        # File Lists
        file_frame = Frame(main_frame)
        file_frame.pack(fill="both", expand=True, pady=5)
        self.file_listbox = Listbox(file_frame, width=60, height=10)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(file_frame)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        # File Lists Footer
        file_footer_frame = Frame(main_frame)
        file_footer_frame.pack(fill="x", expand=True)

        # Download Status
        Label(file_footer_frame, text="Download Status:", font=("Arial", 10)).pack(
            side="left")
        self.download_status = Label(
            file_footer_frame, text="Idle", foreground="black")
        self.download_status.pack(side="left")

        # Download Button
        self.download_btn = Button(file_footer_frame, command=self.download_file, text="Download File", width=20, pady=3, foreground='white', background='teal',
                                   )
        self.download_btn.pack(side="right")

        # Valid Files Frame
        valid_files_frame = Frame(main_frame)
        valid_files_frame.pack(fill="both", expand=True, pady=5)
        Label(valid_files_frame, text="Valid Files", font=(
            "Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.valid_files_listbox = Listbox(
            valid_files_frame, width=60, height=5)
        self.valid_files_listbox.pack(side="left", fill="both", expand=True)

        valid_scrollbar = Scrollbar(valid_files_frame)
        valid_scrollbar.pack(side="right", fill="y")
        self.valid_files_listbox.config(yscrollcommand=valid_scrollbar.set)
        valid_scrollbar.config(command=self.valid_files_listbox.yview)

        # Error Logs Frame
        error_logs_frame = Frame(main_frame)
        error_logs_frame.pack(fill="both", expand=True, pady=5)
        Label(error_logs_frame, text="Error Logs", font=(
            "Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.error_logs_listbox = Listbox(error_logs_frame, width=60, height=5)
        self.error_logs_listbox.pack(side="left", fill="both", expand=True)

        error_scrollbar = Scrollbar(error_logs_frame)
        error_scrollbar.pack(side="right", fill="y")
        self.error_logs_listbox.config(yscrollcommand=error_scrollbar.set)
        error_scrollbar.config(command=self.error_logs_listbox.yview)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
