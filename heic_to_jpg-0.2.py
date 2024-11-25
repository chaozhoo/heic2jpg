import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pillow_heif
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def convert_heic_to_jpg(input_file, output_file):
    try:
        heif_file = pillow_heif.read_heif(input_file)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        image.save(output_file, "JPEG", quality=95, optimize=True)
        return True
    except Exception as e:
        print(f"转换 {input_file} 时出错: {e}")
        return False

def process_files(input_files, output_dir, progress_var, progress_label):
    os.makedirs(output_dir, exist_ok=True)

    total_files = len(input_files)
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_heic_to_jpg, input_file, os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.jpg")) 
                   for input_file in input_files]
        
        for i, future in enumerate(tqdm(as_completed(futures), total=total_files), 1):
            future.result()
            progress = int((i / total_files) * 100)
            progress_var.set(progress)
            progress_label.config(text=f"进度: {progress}%")
            root.update_idletasks()

    messagebox.showinfo("完成", "转换完成!你可以在输出文件夹中找到转换后的JPG图片。")

class HEICtoJPGConverter:
    def __init__(self, master):
        self.master = master
        master.title("HEIC转JPG小助手")
        master.geometry("500x350")

        style = ttk.Style()
        style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        # Configure main_frame to expand
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure column weights
        main_frame.columnconfigure(1, weight=1)  # Make the middle column (Entry widgets) expandable
        
        # Row 0: Input file selection
        ttk.Label(main_frame, text="HEIC文件:").grid(row=0, column=0, sticky="w", pady=5)
        self.input_entry = ttk.Entry(main_frame)  # Removed fixed width
        self.input_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(5, 0))
        ttk.Button(main_frame, text="选择文件", command=self.select_input).grid(row=0, column=2, padx=5, pady=5)

        # Row 1: Output directory selection
        ttk.Label(main_frame, text="JPG保存文件夹:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_entry = ttk.Entry(main_frame)  # Removed fixed width
        self.output_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(5, 0))
        ttk.Button(main_frame, text="选择文件夹", command=self.select_output_directory).grid(row=1, column=2, padx=5, pady=5)

        # Row 2: Convert button
        self.convert_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Row 3: Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var)  # Removed fixed length
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew", padx=5)

        # Row 4: Progress label
        self.progress_label = ttk.Label(main_frame, text="进度: 0%")
        self.progress_label.grid(row=4, column=0, columnspan=3)

    def select_input(self):
        files = filedialog.askopenfilenames(title="选择HEIC文件", filetypes=[("HEIC files", "*.heic")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, ", ".join(files))

    def select_output_directory(self):
        output_dir = filedialog.askdirectory(title="选择保存JPG图片的文件夹")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, output_dir)

    def start_conversion(self):
        input_files = self.input_entry.get().split(", ")
        output_dir = self.output_entry.get()
        if not input_files or not output_dir:
            messagebox.showerror("错误", "请选择输入文件和输出文件夹")
            return
        self.convert_button.config(state="disabled")
        process_files(input_files, output_dir, self.progress_var, self.progress_label)
        self.convert_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = HEICtoJPGConverter(root)
    root.mainloop()
