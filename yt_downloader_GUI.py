import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Progressbar
import yt_dlp
import threading

def update_quality_options(*args):
    format_choice = format_combobox.get()
    url = url_entry.get()

    if not url:
        return

    def fetch_formats():
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', None)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法獲取格式資訊: {e}")
            root.config(cursor="")
            loading_label.grid_remove()
            return

        if not formats:
            root.config(cursor="")
            loading_label.grid_remove()
            return

        if format_choice in ['mp4', 'flv', 'webm']:
            video_qualities = sorted(set(f['height'] for f in formats if f.get('vcodec') != 'none' and f.get('height')))
            quality_combobox.config(values=video_qualities)
            quality_combobox.current(0)
            quality_combobox.grid(row=2, column=1, padx=10, pady=10)
            quality_label.grid(row=2, column=0, padx=10, pady=10)
        elif format_choice in ['mp3', 'm4a', 'aac']:
            audio_qualities = sorted(set(f['abr'] for f in formats if f.get('acodec') != 'none' and f.get('abr')))
            quality_combobox.config(values=audio_qualities)
            quality_combobox.current(0)
            quality_combobox.grid(row=2, column=1, padx=10, pady=10)
            quality_label.grid(row=2, column=0, padx=10, pady=10)
        else:
            quality_combobox.grid_remove()
            quality_label.grid_remove()

        root.config(cursor="")
        loading_label.grid_remove()

    root.config(cursor="wait")
    loading_label.grid(row=1, column=2, padx=10, pady=10)

    threading.Thread(target=fetch_formats).start()

def download_video():
    url = url_entry.get()
    file_format = format_combobox.get()
    quality = quality_combobox.get()

    if not url or not file_format or not quality:
        messagebox.showerror("錯誤", "請填寫所有欄位")
        return

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video')
    except Exception as e:
        messagebox.showerror("錯誤", f"無法獲取影片資訊: {e}")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=f".{file_format}",
                                             initialfile=video_title,
                                             filetypes=[(file_format.upper(), f"*.{file_format}")])

    if not save_path:
        return

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best' if file_format in ['mp4', 'flv', 'webm'] else 'bestaudio/best',
        'outtmpl': save_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
            'preferredquality': quality,
        }] if file_format in ['mp3', 'm4a', 'aac'] else []
    }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("成功", "下載完成")
        except Exception as e:
            messagebox.showerror("錯誤", f"下載失敗: {e}")
        finally:
            progress_bar.stop()
            progress_bar.grid_remove()
            download_button.config(state=tk.NORMAL)
            root.config(cursor="")

    progress_bar.grid(row=4, column=0, columnspan=2, pady=10)
    download_button.config(state=tk.DISABLED)
    root.config(cursor="wait")

    threading.Thread(target=run_download).start()

root = tk.Tk()
root.title("YT-DLP GUI")

tk.Label(root, text="影片網址:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="選擇格式:").grid(row=1, column=0, padx=10, pady=10)
format_combobox = ttk.Combobox(root, values=["mp4", "mp3", "m4a", "aac", "flv", "webm"])
format_combobox.grid(row=1, column=1, padx=10, pady=10)
format_combobox.current(0)
format_combobox.bind("<<ComboboxSelected>>", update_quality_options)

loading_label = tk.Label(root, text="請稍候...", fg="red")

quality_label = tk.Label(root, text="選擇畫質/音質:")
quality_combobox = ttk.Combobox(root)
quality_combobox.grid(row=2, column=1, padx=10, pady=10)
quality_label.grid(row=2, column=0, padx=10, pady=10)
update_quality_options()

download_button = tk.Button(root, text="下載", command=download_video)
download_button.grid(row=3, column=0, columnspan=2, pady=20)

progress_bar = Progressbar(root, mode='indeterminate')

root.mainloop()
