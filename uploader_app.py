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

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

REPO_NAME = "onlinebabuijore-prog/gdrive-remote-uploader"
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")

class ModernGDriveUploaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Cloud to Google Drive Remote Uploader v2.0")
        self.geometry("820x720")
        self.minsize(780, 680)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Scrollable Frame / Container
        self.main_frame = ctk.CTkFrame(self, corner_radius=18, fg_color="#101520")
        self.main_frame.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header Bar
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="#161e2e", corner_radius=12)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="⚡ Google Drive Remote Uploader",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#22c55e"
        )
        self.header_title.pack(anchor="w", padx=16, pady=(10, 2))

        self.header_sub = ctk.CTkLabel(
            self.header_frame,
            text="High-Speed Cloud Pipeline (Gigabit Speed, Zero PC Internet Usage)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94a3b8"
        )
        self.header_sub.pack(anchor="w", padx=16, pady=(0, 10))

        # URL Input Section
        self.input_card = ctk.CTkFrame(self.main_frame, fg_color="#141c2c", corner_radius=12)
        self.input_card.pack(fill="x", padx=20, pady=5)
        self.input_card.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(
            self.input_card, 
            text="🔗 Remote File URL or Magnet Link (HTTP / Torrent / Magnet):", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#e2e8f0"
        )
        self.url_label.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))

        self.url_input_box = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.url_input_box.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.url_input_box.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            self.url_input_box,
            placeholder_text="https://example.com/file.zip or magnet:?xt=urn:btih:...",
            height=42,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0b0f19",
            border_color="#2a3854"
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.paste_btn = ctk.CTkButton(
            self.url_input_box,
            text="📋 Paste",
            width=85,
            height=42,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.paste_clipboard
        )
        self.paste_btn.grid(row=0, column=1)

        # Folder row
        self.folder_box = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.folder_box.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 12))
        self.folder_box.grid_columnconfigure(1, weight=1)

        self.folder_lbl = ctk.CTkLabel(self.folder_box, text="📂 Target Folder:", font=ctk.CTkFont(size=12), text_color="#cbd5e1")
        self.folder_lbl.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.folder_entry = ctk.CTkEntry(self.folder_box, height=34, fg_color="#0b0f19", border_color="#2a3854", font=ctk.CTkFont(size=12))
        self.folder_entry.insert(0, "Remote_Uploads")
        self.folder_entry.grid(row=0, column=1, sticky="ew")

        # Start Button
        self.upload_btn = ctk.CTkButton(
            self.main_frame,
            text="🚀 Start Remote Upload to Google Drive",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=48,
            fg_color="#16a34a",
            hover_color="#15803d",
            corner_radius=12,
            command=self.start_upload_thread
        )
        self.upload_btn.pack(fill="x", padx=20, pady=(12, 8))

        # Live Stepper & Metrics Dashboard Frame
        self.metrics_frame = ctk.CTkFrame(self.main_frame, fg_color="#141c2c", corner_radius=12)
        self.metrics_frame.pack(fill="x", padx=20, pady=6)
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 4 Pipeline Stage Badges
        self.badge1 = ctk.CTkLabel(self.metrics_frame, text="1. Cloud Setup\n[ Ready ]", font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1e293b", corner_radius=8, height=45)
        self.badge1.grid(row=0, column=0, padx=6, pady=8, sticky="ew")

        self.badge2 = ctk.CTkLabel(self.metrics_frame, text="2. 16x Download\n[ Waiting ]", font=ctk.CTkFont(size=11), fg_color="#1e293b", corner_radius=8, height=45, text_color="#64748b")
        self.badge2.grid(row=0, column=1, padx=6, pady=8, sticky="ew")

        self.badge3 = ctk.CTkLabel(self.metrics_frame, text="3. Drive Upload\n[ Waiting ]", font=ctk.CTkFont(size=11), fg_color="#1e293b", corner_radius=8, height=45, text_color="#64748b")
        self.badge3.grid(row=0, column=2, padx=6, pady=8, sticky="ew")

        self.badge4 = ctk.CTkLabel(self.metrics_frame, text="4. Public Link\n[ Waiting ]", font=ctk.CTkFont(size=11), fg_color="#1e293b", corner_radius=8, height=45, text_color="#64748b")
        self.badge4.grid(row=0, column=3, padx=6, pady=8, sticky="ew")

        # Live Metrics Row
        self.metric_info = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.metric_info.pack(fill="x", padx=20, pady=(4, 4))
        self.metric_info.grid_columnconfigure((0, 1), weight=1)

        self.status_label = ctk.CTkLabel(self.metric_info, text="● System Ready", font=ctk.CTkFont(size=12, weight="bold"), text_color="#22c55e", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.timer_label = ctk.CTkLabel(self.metric_info, text="Speed: ~120 MB/s | Elapsed: 00:00", font=ctk.CTkFont(family="Consolas", size=12), text_color="#94a3b8", anchor="e")
        self.timer_label.grid(row=0, column=1, sticky="e")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=12, corner_radius=6, fg_color="#1e293b", progress_color="#22c55e")
        self.progress_bar.pack(fill="x", padx=20, pady=(2, 10))
        self.progress_bar.set(0)

        # Success Result Box
        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color="#111c16", border_color="#22c55e", border_width=1, corner_radius=12)
        self.result_frame.pack(fill="x", padx=20, pady=6)
        self.result_frame.grid_columnconfigure(1, weight=1)

        self.res_file_lbl = ctk.CTkLabel(self.result_frame, text="📁 File: Waiting for upload...", font=ctk.CTkFont(size=13, weight="bold"), text_color="#e2e8f0", anchor="w")
        self.res_file_lbl.grid(row=0, column=0, columnspan=3, padx=14, pady=(10, 4), sticky="w")

        # Public Link Row
        self.link_lbl = ctk.CTkLabel(self.result_frame, text="🔗 Public Link:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#22c55e")
        self.link_lbl.grid(row=1, column=0, padx=(14, 6), pady=4, sticky="w")

        self.link_entry = ctk.CTkEntry(self.result_frame, height=32, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#09130d", border_color="#1b4332")
        self.link_entry.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        self.copy_link_btn = ctk.CTkButton(self.result_frame, text="📋 Copy", width=75, height=32, fg_color="#16a34a", hover_color="#15803d", command=self.copy_share_link)
        self.copy_link_btn.grid(row=1, column=2, padx=(4, 14), pady=4)

        # Direct Link Row
        self.direct_lbl = ctk.CTkLabel(self.result_frame, text="⚡ Direct Link:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8")
        self.direct_lbl.grid(row=2, column=0, padx=(14, 6), pady=4, sticky="w")

        self.direct_entry = ctk.CTkEntry(self.result_frame, height=32, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#09130d", border_color="#1b4332")
        self.direct_entry.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        self.copy_direct_btn = ctk.CTkButton(self.result_frame, text="📋 Copy", width=75, height=32, fg_color="#0284c7", hover_color="#0369a1", command=self.copy_direct_link)
        self.copy_direct_btn.grid(row=2, column=2, padx=(4, 14), pady=4)

        # Open in Browser button
        self.open_btn = ctk.CTkButton(
            self.result_frame,
            text="🌐 Open Google Drive Link in Browser",
            fg_color="#1e293b",
            hover_color="#334155",
            height=34,
            command=self.open_link_in_browser
        )
        self.open_btn.grid(row=3, column=0, columnspan=3, padx=14, pady=(6, 12), sticky="ew")

        self.is_running = False
        self.elapsed_sec = 0

    def paste_clipboard(self):
        try:
            txt = self.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, txt.strip())
        except Exception:
            pass

    def copy_share_link(self):
        l = self.link_entry.get().strip()
        if l:
            self.clipboard_clear()
            self.clipboard_append(l)
            messagebox.showinfo("Copied", "Public Share Link copied to clipboard!")

    def copy_direct_link(self):
        l = self.direct_entry.get().strip()
        if l:
            self.clipboard_clear()
            self.clipboard_append(l)
            messagebox.showinfo("Copied", "Direct Download Link copied to clipboard!")

    def open_link_in_browser(self):
        l = self.link_entry.get().strip()
        if l:
            webbrowser.open(l)

    def set_badge_state(self, b1, b2, b3, b4):
        badges = [self.badge1, self.badge2, self.badge3, self.badge4]
        states = [b1, b2, b3, b4]
        titles = ["1. Cloud Setup", "2. 16x Download", "3. Drive Upload", "4. Public Link"]
        
        for i in range(4):
            st = states[i]
            if st == "done":
                badges[i].configure(text=f"{titles[i]}\n[ Done ✓ ]", fg_color="#14532d", text_color="#4ade80")
            elif st == "active":
                badges[i].configure(text=f"{titles[i]}\n[ Active ⚡ ]", fg_color="#1e3a8a", text_color="#60a5fa")
            else:
                badges[i].configure(text=f"{titles[i]}\n[ Waiting ]", fg_color="#1e293b", text_color="#64748b")

    def start_upload_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a download URL!")
            return
        
        folder = self.folder_entry.get().strip() or "Remote_Uploads"
        self.upload_btn.configure(state="disabled")
        self.is_running = True
        self.elapsed_sec = 0

        self.set_badge_state("active", "waiting", "waiting", "waiting")
        self.progress_bar.set(0.15)
        self.status_label.configure(text="⏳ Triggering Cloud Runner...", text_color="#38bdf8")

        threading.Thread(target=self.timer_loop, daemon=True).start()
        threading.Thread(target=self.run_upload, args=(url, folder), daemon=True).start()

    def timer_loop(self):
        while self.is_running:
            time.sleep(1)
            self.elapsed_sec += 1
            m = self.elapsed_sec // 60
            s = self.elapsed_sec % 60
            
            if self.elapsed_sec > 8 and self.elapsed_sec <= 28:
                self.set_badge_state("done", "active", "waiting", "waiting")
                self.progress_bar.set(0.45)
                self.status_label.configure(text="⚡ Downloading with Aria2c (16-Connections)...", text_color="#38bdf8")
            elif self.elapsed_sec > 28 and self.elapsed_sec <= 55:
                self.set_badge_state("done", "done", "active", "waiting")
                self.progress_bar.set(0.75)
                self.status_label.configure(text="☁️ Uploading directly to Google Drive...", text_color="#38bdf8")
            elif self.elapsed_sec > 55:
                self.set_badge_state("done", "done", "done", "active")
                self.progress_bar.set(0.90)
                self.status_label.configure(text="🔗 Generating Public Share Link...", text_color="#38bdf8")

            self.timer_label.configure(text=f"Speed: ~120 MB/s | Elapsed: {m:02d}:{s:02d}")

    def run_upload(self, url, folder):
        try:
            # 1. Trigger GitHub Workflow via gh CLI
            cmd = ["gh", "workflow", "run", "upload.yml", "-f", f"url={url}", "-f", f"folder={folder}", "--repo", REPO_NAME]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                self.handle_err(f"Workflow Trigger Error: {res.stderr}")
                return

            time.sleep(4)

            # 2. Get latest run ID
            cmd_run = ["gh", "run", "list", "--workflow=upload.yml", "--limit", "1", "--json", "databaseId", "--repo", REPO_NAME]
            run_id = None
            for _ in range(8):
                r = subprocess.run(cmd_run, capture_output=True, text=True)
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    if data:
                        run_id = data[0]["databaseId"]
                        break
                time.sleep(2)

            if not run_id:
                self.handle_err("Could not find active cloud execution job.")
                return

            # 3. Poll status
            while True:
                time.sleep(4)
                chk = subprocess.run(["gh", "run", "view", str(run_id), "--json", "status,conclusion", "--repo", REPO_NAME], capture_output=True, text=True)
                if chk.returncode == 0:
                    d = json.loads(chk.stdout)
                    if d.get("status") == "completed":
                        if d.get("conclusion") == "success":
                            self.fetch_result(run_id)
                            break
                        else:
                            self.handle_err(f"Workflow finished with status: {d.get('conclusion')}")
                            break
        except Exception as e:
            self.handle_err(str(e))

    def fetch_result(self, run_id):
        self.is_running = False
        self.set_badge_state("done", "done", "done", "done")
        self.progress_bar.set(1.0)

        log_res = subprocess.run(["gh", "run", "view", str(run_id), "--repo", REPO_NAME, "--log"], capture_output=True, text=True)
        txt = log_res.stdout

        pub, direct, fn = "", "", "Uploaded File"
        for line in txt.splitlines():
            if "PUBLIC_LINK=" in line:
                pub = line.split("PUBLIC_LINK=")[-1].strip()
            if "DIRECT_LINK=" in line:
                direct = line.split("DIRECT_LINK=")[-1].strip()
            if "FILE_NAME=" in line:
                fn = line.split("FILE_NAME=")[-1].strip()

        if not pub:
            pub = "https://drive.google.com/drive/folders/"

        self.after(0, lambda: self.show_success_ui(fn, pub, direct or pub))

    def show_success_ui(self, fn, pub, direct):
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text="✅ Upload Completed Successfully!", text_color="#22c55e")
        self.res_file_lbl.configure(text=f"📁 File: {fn}")
        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, pub)
        self.direct_entry.delete(0, tk.END)
        self.direct_entry.insert(0, direct)
        messagebox.showinfo("Success", f"File '{fn}' uploaded successfully to Google Drive!")

    def handle_err(self, err):
        self.is_running = False
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text="❌ Upload Failed", text_color="#ef4444")
        messagebox.showerror("Error", err)

if __name__ == "__main__":
    app = ModernGDriveUploaderApp()
    app.mainloop()
