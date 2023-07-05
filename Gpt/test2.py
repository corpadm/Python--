
import tkinter as tk

from tkinter import filedialog

from tkinter import scrolledtext



def open_file():

    global text, lines

    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    if file_path:

        with open(file_path, "r") as f:

            content = f.read()

            lines = content.splitlines()

            display_line_count()



def submit():

    global lines, progress_var

    total_chars = sum(len(line) for line in lines)

    progress_var.set(f"完成度：{total_chars}")



def display_line_count():

    global text, lines, progress_var

    text.delete(1.0, tk.END)

    for i, line in enumerate(lines):

        text.insert(tk.END, f"第{i + 1}行：字符个数{len(line)}\n")


        text.see(tk.END)

        text.update()

        root.after(1000, display_line_count)



root = tk.Tk()

root.title("文本解析工具")



frame = tk.Frame(root)

frame.pack(padx=10, pady=10)



file_button = tk.Button(frame, text="打开文件", command=open_file)

file_button.pack(side=tk.LEFT, padx=5)



submit_button = tk.Button(frame, text="提交", command=submit)

submit_button.pack(side=tk.LEFT, padx=5)

text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, yscrollcommand= tk.Scrollbar.set)

text.pack(side=tk.LEFT, padx=5, pady=5)


scrollbar = tk.Scrollbar(frame, command=text.yview)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)




progress_var = tk.StringVar()

progress_label = tk.Label(root, textvariable=progress_var)

progress_label.pack(padx=10, pady=10)



root.mainloop()

