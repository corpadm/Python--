import tkinter as tk  
from tkinter import filedialog  
import os
import sys
class Application(tk.Frame):  
    def __init__(self, master=None):  
        super().__init__(master)  
        self.master = master  
        self.pack()  
        self.file_content=[]
        self.create_widgets()
    def create_widgets(self):  
        self.btn_open = tk.Button(self)  
        self.btn_open["text"] = "打开文件"  
        self.btn_open["command"] = self.open_file  
        self.btn_open.grid(row=0, column=0, padx=5, pady=5)
        self.btn_submit = tk.Button(self)  
        self.btn_submit["text"] = "提交"  
        self.btn_submit["command"] = self.submit  
        self.btn_submit.grid(row=0, column=1, padx=5, pady=5)
        self.lbl_progress = tk.Label(self)  
        self.lbl_progress["text"] = "完成度：0%"  
        self.lbl_progress["pady"] = 5  
        self.lbl_progress.grid(row=1, column=0, padx=5, pady=5)
        self.lbl_text = tk.Label(self)  
        self.lbl_text["text"] = ""  
        self.lbl_text["pady"] = 5  
        self.lbl_text.grid(row=1, column=1, padx=5, pady=5)
        self.txt_scroll = tk.Text(self)  
        self.txt_scroll["wrap"] = "word"  
        self.txt_scroll["pady"] = 5  
        self.txt_scroll.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.txt_scroll.insert(tk.END, "请选择要打开的文本文件\n")
        
    #打开文件并读取文件内容到file_content中
    def open_file(self):  
        file_path = filedialog.askopenfilename()  
        if file_path:  
            with open(file_path, "r") as f:  
                self.file_content=f.readlines()  
    
    #读取文件内容，解析并显示解析进度            
    def submit(self):  
        #file_content = self.txt_scroll.get("1.0", tk.END)  
        self.lbl_progress["text"] = "解读文件中，请稍候..."  
        progress = 0  
        #lines = file_content.split("\n")  
        for i, line in enumerate(self.file_content):              
            self.lbl_progress["text"] = f"完成度：{i}/{len(self.file_content)}"  
            self.update_text(f"第{i}行，字符数{len(line)}\n")
        self.lbl_progress["text"] = "解读完成"  
    
    def update_text(self,tip):  
        self.txt_scroll.delete(tk.END)  
        self.txt_scroll.insert(tk.END, tip)
        self.master.update()
        
root = tk.Tk()  
app = Application(master=root)  
app.mainloop()  