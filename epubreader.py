import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage, Listbox, Frame
from ebooklib import epub
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import io

class EPUBReader:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB 閱讀器")
        self.root.geometry("1000x600")

        self.book = None
        self.spine = []
        self.toc = []
        self.href_to_index = {}  # 建立 href 對應 spine index
        self.current_index = 0
        self.text_size = 14
        self.dark_mode = False
        self.images = []
        self.book_title = ""

        self.create_widgets()

    def create_widgets(self):
        self.left_frame = Frame(self.root, width=250)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.toggle_toc_button = tk.Button(self.left_frame, text="顯示/隱藏目錄", command=self.toggle_toc)
        self.toggle_toc_button.pack(fill=tk.X)
        
        self.toc_listbox = Listbox(self.left_frame)
        self.toc_listbox.pack(fill=tk.BOTH, expand=True)
        self.toc_listbox.bind("<<ListboxSelect>>", self.load_toc_page)
        
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.open_button = tk.Button(top_frame, text="開啟 EPUB", command=self.load_epub)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = tk.Button(top_frame, text="上一頁", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(top_frame, text="下一頁", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.font_button = tk.Button(top_frame, text="放大字體", command=self.increase_font)
        self.font_button.pack(side=tk.LEFT, padx=5)

        self.small_font_button = tk.Button(top_frame, text="縮小字體", command=self.decrease_font)
        self.small_font_button.pack(side=tk.LEFT, padx=5)

        self.dark_mode_button = tk.Button(top_frame, text="切換深色模式", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side=tk.LEFT, padx=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", self.text_size))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_page()

    def next_page(self):
        if self.current_index < len(self.spine) - 1:
            self.current_index += 1
            self.display_page()

    def toggle_toc(self):
        if self.toc_listbox.winfo_ismapped():
            self.toc_listbox.pack_forget()
        else:
            self.toc_listbox.pack(fill=tk.BOTH, expand=True)
    
    def update_toc(self):
        self.toc_listbox.delete(0, tk.END)
        for title, _ in self.toc:
            self.toc_listbox.insert(tk.END, title)
    
    def load_toc_page(self, event):
        selection = self.toc_listbox.curselection()
        if selection:
            _, href = self.toc[selection[0]]
            href = href.split("#")[0].lstrip('/')  # 處理內部連結
            if href in self.href_to_index:
                self.current_index = self.href_to_index[href]
                self.display_page()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = "black" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"
        self.text_area.config(bg=bg_color, fg=fg_color)

    def increase_font(self):
        self.text_size += 2
        self.text_area.config(font=("Arial", self.text_size))

    def decrease_font(self):
        if self.text_size > 8:
            self.text_size -= 2
            self.text_area.config(font=("Arial", self.text_size))

    def load_epub(self):
        file_path = filedialog.askopenfilename(filetypes=[("EPUB", "*.epub")])
        if not file_path:
            return

        self.book = epub.read_epub(file_path)
        self.spine = [item[0] for item in self.book.spine]
        self.book_title = self.book.get_metadata("DC", "title")[0][0] if self.book.get_metadata("DC", "title") else "Unknown Title"
        
        self.toc = []
        self.href_to_index = {}

        def parse_toc(toc_list):
            """ 遞迴解析 EPUB 目錄 """
            for item in toc_list:
                if isinstance(item, epub.Link):
                    self.toc.append((item.title, item.href))
                elif isinstance(item, epub.Section):
                    self.toc.append((item.title, ""))  # 顯示章節標題
                    parse_toc(item.subsections)

        parse_toc(self.book.toc)

        # 建立 href 對 spine 的索引
        for index, spine_id in enumerate(self.spine):
            item = self.book.get_item_with_id(spine_id)
            if item:
                self.href_to_index[item.get_name()] = index

        self.current_index = 0
        self.update_toc()
        self.display_page()
    
    def display_page(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        if self.spine:
            item = self.book.get_item_with_id(self.spine[self.current_index])
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            self.text_area.insert(tk.END, soup.get_text())
        
        self.text_area.config(state=tk.DISABLED)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = EPUBReader(root)
    root.mainloop()
