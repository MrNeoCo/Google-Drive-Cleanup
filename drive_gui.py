import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from threading import Thread
import sys
import io
from datetime import datetime

# Import backend functions
from cleanup import authenticate, cleanup_old_files
from googleapiclient.http import MediaFileUpload

# Redirect print output to the UI console
class ConsoleRedirect(io.StringIO):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def write(self, message):
        self.textbox.insert(tk.END, message)
        self.textbox.see(tk.END)
        self.textbox.update_idletasks()

    def flush(self):
        pass

# Main GUI app
class DriveCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive Cleanup Tool 🧹")
        self.root.geometry("750x550")

        self.service = None
        self.preview_mode = tk.BooleanVar(value=True)

        # Buttons
        tk.Button(root, text="🔐 Authenticate", width=20, command=self.authenticate_drive).pack(pady=8)
        tk.Button(root, text="📄 List Files", width=20, command=self.list_files).pack(pady=8)
        tk.Button(root, text="📤 Upload File", width=20, command=self.upload_file).pack(pady=8)
        tk.Button(root, text="🧹 Cleanup Old Files", width=20, command=self.cleanup_files).pack(pady=8)

        # Toggle for preview mode
        tk.Checkbutton(
            root,
            text="Preview Mode (ON = Only show, OFF = Delete for real)",
            variable=self.preview_mode,
            onvalue=True,
            offvalue=False
        ).pack(pady=4)

        # Console log box
        self.console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=18, width=90)
        self.console.pack(padx=10, pady=10)
        sys.stdout = ConsoleRedirect(self.console)

    def log(self, text):
        """Helper to print in console area."""
        self.console.insert(tk.END, f"{text}\n")
        self.console.see(tk.END)
        self.console.update_idletasks()

    def run_in_thread(self, func):
        """Run heavy function in thread so UI doesn’t freeze."""
        Thread(target=func, daemon=True).start()

    # ----------- Button Handlers -----------
    def authenticate_drive(self):
        self.log("🔐 Authenticating with Google Drive...")
        self.run_in_thread(self._auth_thread)

    def _auth_thread(self):
        try:
            self.service = authenticate()
            self.log("✅ Authentication successful!\n")
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")

    def list_files(self):
        if not self.service:
            messagebox.showerror("Error", "Please authenticate first!")
            return
        self.run_in_thread(self._list_files_thread)

    def _list_files_thread(self):
        self.log("📂 Fetching file list...")
        try:
            results = self.service.files().list(
                pageSize=5,
                fields="files(id, name, modifiedTime)"
            ).execute()
            items = results.get('files', [])
            if not items:
                self.log("No files found.")
            else:
                self.log("all files in Drive:\n")
                for f in items:
                    mod_time = datetime.fromisoformat(f['modifiedTime'].replace('Z', '+00:00'))
                    self.log(f"📄 {f['name']} | Modified: {mod_time:%Y-%m-%d %H:%M:%S} | ID: {f['id']}")
            self.log("✅ Listing complete.\n")
        except Exception as e:
            self.log(f"❌ Error listing files: {e}")

    def upload_file(self):
        if not self.service:
            messagebox.showerror("Error", "Please authenticate first!")
            return
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if not file_path:
            return
        self.run_in_thread(lambda: self._upload_thread(file_path))

    def _upload_thread(self, file_path):
        self.log(f"📤 Uploading file: {file_path}")
        try:
            file_name = file_path.split("/")[-1]
            metadata = {'name': file_name}
            media = MediaFileUpload(file_path, resumable=True)
            uploaded = self.service.files().create(
                body=metadata, media_body=media, fields="id, name"
            ).execute()
            self.log(f"✅ File uploaded: {uploaded['name']} ({uploaded['id']})\n")
        except Exception as e:
            self.log(f"❌ Upload failed: {e}")

    def cleanup_files(self):
        if not self.service:
            messagebox.showerror("Error", "Please authenticate first!")
            return
        preview = self.preview_mode.get()
        self.run_in_thread(lambda: self._cleanup_thread(preview))

    def _cleanup_thread(self, preview):
        self.log("🧹 Running cleanup...")
        try:
            # The cleanup_old_files function must accept preview_mode
            cleanup_old_files(self.service, preview_mode=preview)
            self.log("✅ Cleanup finished!\n")
        except TypeError:
            self.log("⚠️ Note: Update your cleanup_old_files() to accept `preview_mode` argument.")
        except Exception as e:
            self.log(f"❌ Cleanup error: {e}")

# ----------- Run GUI -----------
if __name__ == "__main__":
    root = tk.Tk()
    app = DriveCleanerApp(root)
    root.mainloop()
