
import tkinter as tk

from tkinter import filedialog, scrolledtext

import os



class FileParserApp(tk.Tk):

    def __init__(self):

        super().__init__()

        print("hello1")

        self.title("文件解析器")

        self.geometry("800x600")

        

        # 创建文件浏览框

        self.file_path = None

        self.file_button = tk.Button(self, text="选择文件", command=self.open_file)

        self.file_button.pack(side=tk.LEFT, padx=10)

        

        # 创建提交按钮

        self.submit_button = tk.Button(self, text="提交", command=self.parse_file)

        self.submit_button.pack(side=tk.LEFT, padx=10)

        

        # 创建完成度滚动条

        self.progress_bar = tk.Scale(self, from_=0, to=100, resolution=1, length=400, orient=tk.HORIZONTAL)

        self.progress_bar.pack(side=tk.LEFT, padx=10)

        

        # 创建动态文本显示框

        self.text_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=25)

        self.text_display.pack(side=tk.LEFT, padx=10)

        

        # 初始化完成度为0

        self.progress = 0

        

    def open_file(self):

        file_path = filedialog.askopenfilename()

        if file_path:

            self.file_path = file_path

            self.update_status("正在打开文件")

    

    def parse_file(self):

        if not self.file_path:

            self.update_status("请先选择文件")

            return

        

        with open(self.file_path, "r") as f:

            lines = f.readlines()

            

        for i, line in enumerate(lines):

            self.progress += len(line) + 100  # 每行字符数+100作为进度值

            self.update_status("解析第{}行".format(i+1))

            

            # 在文本栏中显示当前行的字符数和内容

            chars = len(line) + "个字符" if len(line) else "空行"

            self.text_display.insert(tk.END, "第{}行：{}".format(i+1, chars))

            self.text_display.see(tk.END)

            

            # 更新完成度滚动条的位置和值

            self.progress_bar["value"] = int(self.progress/len(lines)*100) if lines else 0

    

    def update_status(self, status):

        status_label = tk.Label(self, text=status, anchor=tk.W)

        status_label.pack(pady=10)


if(__file__=="__main__"):
    fp=FileParserApp()
    
    fp.mainloop()