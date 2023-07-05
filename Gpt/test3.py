import tkinter as tk
from tkinter import filedialog, scrolledtext

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # 文件浏览框
        self.file_path = tk.StringVar()
        self.file_label = tk.Label(self, textvariable=self.file_path)
        self.file_label.pack()

        self.browse_button = tk.Button(self, text="选择文件", command=self.open_file)
        self.browse_button.pack()

        # 提交按钮
        self.submit_button = tk.Button(self, text="提交", command=self.submit)
        self.submit_button.pack()

        # 完成度滚动条
        self.progressbar = tk.Scrollbar(self, orient="horizontal")
        self.progressbar.pack(fill="x")

        # 动态文本显示框
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, xscrollcommand=self.progressbar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.progressbar.config(command=self.text_area.xview)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path.set(file_path)

    def submit(self):
        file_path = self.file_path.get()
        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
                total_lines = len(lines)

                for i, line in enumerate(lines):
                    line_number = i + 1
                    character_count = len(line.strip())
                    message = f"第{line_number}行：字符个数：{character_count}\n"
                    self.text_area.insert(tk.END, message)
                    self.text_area.see(tk.END)  # 滚动到最新内容

                    # 更新滚动条位置
                    completion = (line_number / total_lines) * 100
                    self.progressbar.set(completion)

root = tk.Tk()
app = Application(master=root)
app.mainloop()