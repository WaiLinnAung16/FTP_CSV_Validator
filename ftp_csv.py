import ftplib
from tkinter import Tk, Frame, Button, Entry, Listbox, Label, Toplevel, StringVar, messagebox


class FTPClient:
    def __init__(self):
        self.ftp = None

    def connect(self, host, user, password):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host)
        self.ftp.login(user, password)
        return True, "Connected to FTP server"

    def disconnect(self):
        self.ftp.quit()
        return False, "Disconnected to FTP server"


class App:
    def __init__(self, root):
        self.root = root
        self.ftp_client = FTPClient()
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

            # Connection Button
            self.ftp_connect_btn.config(
                text="Connect to FTP", command=self.ftp_client_connect, bg='teal')
            messagebox.showinfo(
                "Disconnected", "Disconnected from FTP Server")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")

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
        self.pass_entry = Entry(navbar_frame, textvariable=self.pass_var, show='*')
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
        Button(file_header_frame, text="Clear Search", width=10, pady=0, foreground='teal',
               ).pack(side="right")
        Button(file_header_frame, text="Search", width=10, pady=0, foreground='teal'
               ).pack(side="right", padx=3)
        Entry(file_header_frame, width=30).pack(side="right")

        # File Lists
        file_frame = Frame(main_frame)
        file_frame.pack(fill="both", expand=True, pady=5)
        self.file_listbox = Listbox(file_frame, width=60, height=10)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        # File Lists Footer
        file_footer_frame = Frame(main_frame)
        file_footer_frame.pack(fill="x", expand=True)
        # Download Button
        Label(file_footer_frame, text="Download Status: Downloading...", font=("Arial", 10)).pack(
            side="left")
        Button(file_footer_frame, text="Download File", width=20, pady=3, foreground='white', background='teal',
               ).pack(side="right")

        # Valid Files Frame
        valid_files_frame = Frame(main_frame)
        valid_files_frame.pack(fill="both", expand=True, pady=5)
        Label(valid_files_frame, text="Valid Files", font=(
            "Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.valid_files_listbox = Listbox(
            valid_files_frame, width=60, height=5)
        self.valid_files_listbox.pack(side="left", fill="both", expand=True)

        # Error Logs Frame
        error_logs_frame = Frame(main_frame)
        error_logs_frame.pack(fill="both", expand=True, pady=5)
        Label(error_logs_frame, text="Error Logs", font=(
            "Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.error_logs_listbox = Listbox(error_logs_frame, width=60, height=5)
        self.error_logs_listbox.pack(side="left", fill="both", expand=True)


root = Tk()
app = App(root)
root.mainloop()
