import os
import sys
import json
import time
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

REPO_NAME = "onlinebabuijore-prog/gdrive-remote-uploader"
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")

class GDriveUploaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Cloud to Google Drive Remote Uploader")
        self.geometry("750x620")
        self.minsize(700, 580)

        # App Grid Config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header Title
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="🚀 Google Drive Remote Uploader", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        )
        self.header_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="High-Speed Cloud Transfer directly to your Google Drive (Zero PC Bandwidth)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 15))

        # URL Input Section
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=30, pady=5)
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.url_frame, text="Remote Download URL:", font=ctk.CTkFont(size=13, weight="bold"))
        self.url_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.url_input_box = ctk.CTkFrame(self.url_frame, fg_color="transparent")
        self.url_input_box.grid(row=1, column=0, sticky="ew")
        self.url_input_box.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            self.url_input_box, 
            placeholder_text="https://example.com/large-file.zip",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.paste_btn = ctk.CTkButton(
            self.url_input_box,
            text="📋 Paste",
            width=80,
            height=40,
            command=self.paste_clipboard
        )
        self.paste_btn.grid(row=0, column=1)

        # Options Frame (Folder name)
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=30, pady=(10, 5))
        self.options_frame.grid_columnconfigure(0, weight=1)

        self.folder_label = ctk.CTkLabel(self.options_frame, text="Drive Folder Name (Default: Remote_Uploads):", font=ctk.CTkFont(size=12))
        self.folder_label.grid(row=0, column=0, sticky="w")

        self.folder_entry = ctk.CTkEntry(
            self.options_frame,
            placeholder_text="Remote_Uploads",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.folder_entry.insert(0, "Remote_Uploads")
        self.folder_entry.grid(row=1, column=0, sticky="ew", pady=(3, 0))

        # Upload Button
        self.upload_btn = ctk.CTkButton(
            self.main_frame,
            text="⚡ Start Remote Upload to Google Drive",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#1f883d",
            hover_color="#1a7331",
            command=self.start_upload_thread
        )
        self.upload_btn.pack(fill="x", padx=30, pady=(15, 10))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", height=10)
        self.progress_bar.pack(fill="x", padx=30, pady=(5, 5))
        self.progress_bar.set(0)

        # Status Message
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4da6ff"
        )
        self.status_label.pack(pady=5)

        # Result Frame (Hidden by default, shown on success)
        self.result_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#1e2530")
        self.result_frame.pack(fill="both", expand=True, padx=30, pady=(5, 15))
        self.result_frame.grid_columnconfigure(1, weight=1)

        # File Name Label
        self.res_file_lbl = ctk.CTkLabel(self.result_frame, text="📁 File: -", font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        self.res_file_lbl.grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

        # Share Link Row
        self.link_lbl = ctk.CTkLabel(self.result_frame, text="🔗 Public Link:", font=ctk.CTkFont(size=12, weight="bold"))
        self.link_lbl.grid(row=1, column=0, padx=(15, 5), pady=5, sticky="w")

        self.link_entry = ctk.CTkEntry(self.result_frame, height=32, font=ctk.CTkFont(size=12))
        self.link_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.copy_link_btn = ctk.CTkButton(self.result_frame, text="📋 Copy", width=70, height=32, command=self.copy_share_link)
        self.copy_link_btn.grid(row=1, column=2, padx=(5, 15), pady=5)

        # Direct Link Row
        self.direct_lbl = ctk.CTkLabel(self.result_frame, text="⚡ Direct Link:", font=ctk.CTkFont(size=12, weight="bold"))
        self.direct_lbl.grid(row=2, column=0, padx=(15, 5), pady=5, sticky="w")

        self.direct_entry = ctk.CTkEntry(self.result_frame, height=32, font=ctk.CTkFont(size=12))
        self.direct_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.copy_direct_btn = ctk.CTkButton(self.result_frame, text="📋 Copy", width=70, height=32, command=self.copy_direct_link)
        self.copy_direct_btn.grid(row=2, column=2, padx=(5, 15), pady=5)

        # Open in Browser button
        self.open_btn = ctk.CTkButton(
            self.result_frame, 
            text="🌐 Open Google Drive Link in Browser",
            fg_color="#0066cc",
            hover_color="#0052a3",
            height=32,
            command=self.open_link_in_browser
        )
        self.open_btn.grid(row=3, column=0, columnspan=3, padx=15, pady=(8, 12), sticky="ew")

        self.is_running = False

    def paste_clipboard(self):
        try:
            clipboard_text = self.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text.strip())
        except Exception:
            pass

    def copy_share_link(self):
        link = self.link_entry.get().strip()
        if link:
            self.clipboard_clear()
            self.clipboard_append(link)
            messagebox.showinfo("Copied", "Public Share Link copied to clipboard!")

    def copy_direct_link(self):
        link = self.direct_entry.get().strip()
        if link:
            self.clipboard_clear()
            self.clipboard_append(link)
            messagebox.showinfo("Copied", "Direct Download Link copied to clipboard!")

    def open_link_in_browser(self):
        link = self.link_entry.get().strip()
        if link:
            webbrowser.open(link)

    def start_upload_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Empty URL", "Please enter a valid remote download URL!")
            return
        
        folder = self.folder_entry.get().strip() or "Remote_Uploads"

        self.upload_btn.configure(state="disabled")
        self.progress_bar.start()
        self.status_label.configure(text="🚀 Initiating Cloud Transfer...", text_color="#3399ff")
        self.is_running = True

        thread = threading.Thread(target=self.run_upload_process, args=(url, folder))
        thread.daemon = True
        thread.start()

    def run_upload_process(self, url, folder):
        try:
            # 1. Trigger GitHub Workflow via gh CLI
            self.update_status("📡 Sending download URL to Cloud Runner...")
            cmd_trigger = [
                "gh", "workflow", "run", "upload.yml",
                "-f", f"url={url}",
                "-f", f"folder={folder}",
                "--repo", REPO_NAME
            ]
            res = subprocess.run(cmd_trigger, capture_output=True, text=True)
            if res.returncode != 0:
                self.handle_error(f"Failed to trigger workflow: {res.stderr}")
                return

            time.sleep(3)

            # 2. Get the latest run ID
            self.update_status("🔄 Connecting to Cloud Job...")
            cmd_get_run = [
                "gh", "run", "list",
                "--workflow=upload.yml",
                "--limit", "1",
                "--json", "databaseId,status",
                "--repo", REPO_NAME
            ]
            
            run_id = None
            for _ in range(10):
                res = subprocess.run(cmd_get_run, capture_output=True, text=True)
                if res.returncode == 0:
                    runs = json.loads(res.stdout)
                    if runs:
                        run_id = runs[0]["databaseId"]
                        break
                time.sleep(2)

            if not run_id:
                self.handle_error("Could not find the cloud execution job.")
                return

            # 3. Monitor Run until completion
            start_time = time.time()
            while True:
                time.sleep(5)
                elapsed = int(time.time() - start_time)
                cmd_check = [
                    "gh", "run", "view", str(run_id),
                    "--json", "status,conclusion",
                    "--repo", REPO_NAME
                ]
                res = subprocess.run(cmd_check, capture_output=True, text=True)
                if res.returncode == 0:
                    data = json.loads(res.stdout)
                    status = data.get("status")
                    conclusion = data.get("conclusion")

                    if status == "in_progress":
                        self.update_status(f"⚡ Downloading & Uploading to Drive in Cloud... ({elapsed}s)")
                    elif status == "completed":
                        if conclusion == "success":
                            self.fetch_result_and_display(run_id)
                            break
                        else:
                            self.handle_error(f"Cloud process finished with status: {conclusion}")
                            break

        except Exception as e:
            self.handle_error(f"Unexpected error: {str(e)}")

    def fetch_result_and_display(self, run_id):
        self.update_status("🔗 Generating Public Share Link...")
        time.sleep(2)
        try:
            cmd_log = [
                "gh", "run", "view", str(run_id),
                "--repo", REPO_NAME,
                "--log"
            ]
            res = subprocess.run(cmd_log, capture_output=True, text=True)
            log_output = res.stdout

            public_link = ""
            direct_link = ""
            filename = "Uploaded File"

            for line in log_output.splitlines():
                if "PUBLIC_LINK=" in line:
                    public_link = line.split("PUBLIC_LINK=")[-1].strip()
                if "FILE_NAME=" in line:
                    filename = line.split("FILE_NAME=")[-1].strip()
                if "DIRECT_LINK=" in line:
                    direct_link = line.split("DIRECT_LINK=")[-1].strip()

            if not public_link:
                # Fallback extraction from rclone output
                for line in log_output.splitlines():
                    if "https://drive.google.com/" in line:
                        for token in line.split():
                            if token.startswith("https://drive.google.com/"):
                                public_link = token.strip()
                                break

            self.after(0, lambda: self.show_success(filename, public_link, direct_link))

        except Exception as e:
            self.handle_error(f"Failed to parse result link: {str(e)}")

    def show_success(self, filename, public_link, direct_link):
        self.progress_bar.stop()
        self.progress_bar.set(1.0)
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text="✅ Upload Completed Successfully!", text_color="#00e676")

        self.res_file_lbl.configure(text=f"📁 File: {filename}")
        
        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, public_link)

        self.direct_entry.delete(0, tk.END)
        self.direct_entry.insert(0, direct_link or public_link)

    def update_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text, text_color="#4da6ff"))

    def handle_error(self, message):
        self.after(0, lambda: self.show_error_ui(message))

    def show_error_ui(self, message):
        self.progress_bar.stop()
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text=f"❌ Error occurred", text_color="#ff5252")
        messagebox.showerror("Upload Failed", message)

if __name__ == "__main__":
    app = GDriveUploaderApp()
    app.mainloop()
