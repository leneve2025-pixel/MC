import sys
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import ttk

import pygame
from PIL import Image, ImageDraw
import pystray

# ========== 配置 ==========
MUSIC_DIR = Path(__file__).parent / "changpian"
MC_UPDATES_URL = "https://www.minecraft.net/zh-hans/updates"
# ==========================

pygame.mixer.init()

class JukeboxApp:
    def __init__(self):
        self.playlist = sorted(MUSIC_DIR.glob("*.ogg"))
        if not self.playlist:
            from tkinter import messagebox
            messagebox.showerror("错误", f"{MUSIC_DIR} 里没找到 ogg！")
            sys.exit(1)

        self.playing = False
        self.tray_icon = None

        self.root = tk.Tk()
        self.root.title("MC 唱片机 💿")
        self.root.geometry("360x260")
        self.root.resizable(False, False)
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # ---------- 启动三连 ----------
        self._show_hello()
        self.root.after(100, self.play_random)
        self.root.after(200, lambda: webbrowser.open(MC_UPDATES_URL))

        # ✅ 一启动就进托盘
        self.root.withdraw()
        self.hide_to_tray()

    # ==================== hello ====================
    def _show_hello(self):
        hw = tk.Toplevel(self.root)
        hw.overrideredirect(True)
        hw.attributes("-topmost", True)
        hw.attributes("-alpha", 0.85)

        label = ttk.Label(hw, text="hello, minecraft",
                          font=("Consolas", 28, "bold"),
                          foreground="#4caf50", background="black")
        label.pack(padx=30, pady=18)
        label.configure(background="#1a1a1a")
        hw.configure(bg="#1a1a1a")

        hw.update_idletasks()
        sw, sh = hw.winfo_screenwidth(), hw.winfo_screenheight()
        ww, wh = hw.winfo_width(), hw.winfo_height()
        hw.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2 - 80}")

        hw.after(2000, hw.destroy)

    # ==================== UI ====================
    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=15)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=f"发现 {len(self.playlist)} 张唱片 (.ogg)",
                  font=("Microsoft YaHei", 12, "bold")).pack(pady=(0,10))

        self.info = ttk.Label(frm, text="— 未播放 —", foreground="gray")
        self.info.pack(pady=5)

        bf = ttk.Frame(frm); bf.pack(pady=10)
        ttk.Button(bf, text="▶ 随机一张", width=12,
                   command=self.play_random).grid(row=0, column=0, padx=5)
        ttk.Button(bf, text="⏸ 暂停/继续", width=12,
                   command=self.toggle_pause).grid(row=0, column=1, padx=5)
        ttk.Button(bf, text="⏹ 停止", width=12,
                   command=self.stop).grid(row=0, column=2, padx=5)

        ttk.Button(frm, text="🗕 缩到托盘", width=30,
                   command=self.hide_to_tray).pack(pady=(15,0))
        ttk.Button(frm, text="🌐 打开 MC 更新页", width=30,
                   command=lambda: webbrowser.open(MC_UPDATES_URL)).pack(pady=4)

        self._poll()

    # ==================== 播放 ====================
    def play_random(self):
        f = __import__("random").choice(self.playlist)
        pygame.mixer.music.load(str(f))
        pygame.mixer.music.play()
        self.playing = True
        self.info.config(text=f.stem, foreground="#2a7")

    def toggle_pause(self):
        (pygame.mixer.music.unpause if not self.playing else pygame.mixer.music.pause)()
        self.playing = not self.playing

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.info.config(text="— 已停止 —", foreground="gray")

    def _poll(self):
        if self.playing and not pygame.mixer.music.get_busy():
            self.play_random()
        self.root.after(500, self._poll)

    # ==================== 托盘 ====================
    def hide_to_tray(self):
        self.root.withdraw()
        if self.tray_icon is None:
            img = self._make_icon()
            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", lambda *a: self.root.after(0, self.root.deiconify)),
                pystray.MenuItem("随机一张", lambda *a: self.play_random()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("MC 更新页", lambda *a: webbrowser.open(MC_UPDATES_URL)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", lambda i,_: (i.stop(), self.root.after(0, self.root.destroy))),
            )
            self.tray_icon = pystray.Icon("mc_jukebox", img, "MC 唱片机", menu)
            __import__("threading").Thread(target=self.tray_icon.run, daemon=True).start()

    @staticmethod
    def _make_icon():
        img = Image.new("RGBA", (64,64), (0,0,0,0))
        d = ImageDraw.Draw(img)
        d.ellipse((4,4,60,60), fill=(40,40,40), outline=(180,180,180), width=2)
        d.ellipse((26,26,38,38), fill=(120,120,120))
        return img

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    JukeboxApp().run()