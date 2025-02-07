#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
import webbrowser
import sv_ttk  # Make sure sv_ttk is installed: pip install sv_ttk

class DiffApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Diff Application with sv_ttk")
        self.geometry("1200x700")
        # Set dark theme
        sv_ttk.set_theme("dark")
        # History list to store comparisons; also store current file paths
        self.history = []
        self.left_file = None
        self.right_file = None
        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        # --- Options Frame ---
        options_frame = ttk.Frame(self)
        options_frame.pack(side="top", fill="x", padx=10, pady=5)

        # Checkbuttons for options: ignore case and ignore whitespace differences
        self.ignore_case = tk.BooleanVar(value=False)
        self.ignore_ws = tk.BooleanVar(value=False)
        case_cb = ttk.Checkbutton(options_frame, text="Ignore Case", variable=self.ignore_case)
        ws_cb = ttk.Checkbutton(options_frame, text="Ignore Whitespace", variable=self.ignore_ws)
        case_cb.pack(side="left", padx=5)
        ws_cb.pack(side="left", padx=5)

        # GitHub buttons
        github_frame = ttk.Frame(self)
        github_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        slamfunk_button = ttk.Button(github_frame, text="Slamfunk", command=lambda: self.open_github("https://github.com/slamfunk13"))
        profxed_button = ttk.Button(github_frame, text="Prof.Xed", command=lambda: self.open_github("https://github.com/prof-xed"))
        
        slamfunk_button.pack(side="left", padx=5, pady=5)
        profxed_button.pack(side="left", padx=5, pady=5)        

        # Action buttons for Compare and Clear
        compare_button = ttk.Button(options_frame, text="Compare", command=self.compare_texts)
        compare_button.pack(side="right", padx=5)
        clear_button = ttk.Button(options_frame, text="Clear", command=self.clear_texts)
        clear_button.pack(side="right", padx=5)

        # --- Paned Window for Side-by-Side Text Areas ---
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Left text frame
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        left_label = ttk.Label(left_frame, text="Left Text")
        left_label.pack(anchor="w", padx=5, pady=(5, 0))
        self.left_text = tk.Text(left_frame, wrap="none", undo=True)
        self.left_text.pack(fill="both", expand=True, padx=5, pady=5)
        left_scroll_y = ttk.Scrollbar(left_frame, command=self.left_text.yview)
        self.left_text.configure(yscrollcommand=left_scroll_y.set)
        left_scroll_y.pack(side="right", fill="y")

        # Right text frame
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        right_label = ttk.Label(right_frame, text="Right Text")
        right_label.pack(anchor="w", padx=5, pady=(5, 0))
        self.right_text = tk.Text(right_frame, wrap="none", undo=True)
        self.right_text.pack(fill="both", expand=True, padx=5, pady=5)
        right_scroll_y = ttk.Scrollbar(right_frame, command=self.right_text.yview)
        self.right_text.configure(yscrollcommand=right_scroll_y.set)
        right_scroll_y.pack(side="right", fill="y")

        # --- Configure Tags for Diff Highlighting ---
        # Adjust tag colors for dark backgrounds
        self.left_text.tag_configure("normal", foreground="white")
        self.left_text.tag_configure("diff", foreground="red", font=("Helvetica", 10, "bold"))
        self.left_text.tag_configure("missing", background="yellow")
        self.right_text.tag_configure("normal", foreground="white")
        self.right_text.tag_configure("diff", foreground="green", font=("Helvetica", 10, "bold"))
        self.right_text.tag_configure("missing", background="yellow")

    def open_github(self, url):
        webbrowser.open_new(url)


    def create_menu(self):
        menubar = tk.Menu(self)
        
        # File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Left...", command=self.open_file_left)
        filemenu.add_command(label="Open Right...", command=self.open_file_right)
        filemenu.add_command(label="Attach Files...", command=self.attach_files)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # History Menu
        historymenu = tk.Menu(menubar, tearoff=0)
        historymenu.add_command(label="View History", command=self.view_history)
        menubar.add_cascade(label="History", menu=historymenu)
        
        self.config(menu=menubar)

    def load_file_content(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Error opening file:\n{e}")
            return None

    def open_file_left(self):
        filepath = filedialog.askopenfilename(title="Open Left File")
        if filepath:
            content = self.load_file_content(filepath)
            if content is not None:
                self.left_text.delete("1.0", tk.END)
                self.left_text.insert(tk.END, content)
                self.left_file = filepath

    def open_file_right(self):
        filepath = filedialog.askopenfilename(title="Open Right File")
        if filepath:
            content = self.load_file_content(filepath)
            if content is not None:
                self.right_text.delete("1.0", tk.END)
                self.right_text.insert(tk.END, content)
                self.right_file = filepath

    def attach_files(self):
        filepaths = filedialog.askopenfilenames(title="Attach Files")
        if not filepaths:
            return
        if len(filepaths) == 1:
            # Load a single file into the left text area
            content = self.load_file_content(filepaths[0])
            if content is not None:
                self.left_text.delete("1.0", tk.END)
                self.left_text.insert(tk.END, content)
                self.left_file = filepaths[0]
        else:
            # If two or more files are selected, load the first into left and second into right
            content_left = self.load_file_content(filepaths[0])
            content_right = self.load_file_content(filepaths[1])
            if content_left is not None:
                self.left_text.delete("1.0", tk.END)
                self.left_text.insert(tk.END, content_left)
                self.left_file = filepaths[0]
            if content_right is not None:
                self.right_text.delete("1.0", tk.END)
                self.right_text.insert(tk.END, content_right)
                self.right_file = filepaths[1]

    def view_history(self):
        # Create a new window to display history
        history_win = tk.Toplevel(self)
        history_win.title("Comparison History")
        history_win.geometry("600x400")

        # Use a Treeview widget to list history items
        columns = ("timestamp", "left_file", "right_file")
        tree = ttk.Treeview(history_win, columns=columns, show="headings")
        tree.heading("timestamp", text="Timestamp")
        tree.heading("left_file", text="Left File")
        tree.heading("right_file", text="Right File")

        # Insert history records
        for item in self.history:
            tree.insert("", tk.END, values=(item["timestamp"], item["left_file"], item["right_file"]))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Button to load a selected history record into the text areas
        def load_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Info", "Please select a history item to load.")
                return
            item = tree.item(selected[0])["values"]
            left_path = item[1]
            right_path = item[2]
            left_content = self.load_file_content(left_path)
            right_content = self.load_file_content(right_path)
            if left_content is not None:
                self.left_text.delete("1.0", tk.END)
                self.left_text.insert(tk.END, left_content)
                self.left_file = left_path
            if right_content is not None:
                self.right_text.delete("1.0", tk.END)
                self.right_text.insert(tk.END, right_content)
                self.right_file = right_path
            history_win.destroy()

        load_button = ttk.Button(history_win, text="Load Selected", command=load_selected)
        load_button.pack(pady=5)

    def clear_texts(self):
        self.left_text.delete("1.0", tk.END)
        self.right_text.delete("1.0", tk.END)
        self.left_file = None
        self.right_file = None

    def compare_texts(self):
        """
        Compare the two texts character-by-character.
        - Matching characters are inserted with the "normal" tag.
        - Differences are highlighted:
            Left text differences: "diff" tag (red bold).
            Right text differences: "diff" tag (green bold).
        - Extra characters (when one text is shorter) are shown with a "missing" tag.
        Options to ignore case or whitespace differences are applied.
        """
        left_content = self.left_text.get("1.0", tk.END).rstrip("\n")
        right_content = self.right_text.get("1.0", tk.END).rstrip("\n")
        ignore_case = self.ignore_case.get()
        ignore_ws = self.ignore_ws.get()

        # Clear the text widgets so that we can reinsert highlighted content.
        self.left_text.delete("1.0", tk.END)
        self.right_text.delete("1.0", tk.END)

        max_len = max(len(left_content), len(right_content))
        for i in range(max_len):
            left_char = left_content[i] if i < len(left_content) else None
            right_char = right_content[i] if i < len(right_content) else None

            if left_char is not None and right_char is not None:
                if ignore_ws and left_char.isspace() and right_char.isspace():
                    equal = True
                elif ignore_case:
                    equal = left_char.lower() == right_char.lower()
                else:
                    equal = left_char == right_char

                if equal:
                    self.left_text.insert(tk.END, left_char, "normal")
                    self.right_text.insert(tk.END, right_char, "normal")
                else:
                    self.left_text.insert(tk.END, left_char, "diff")
                    self.right_text.insert(tk.END, right_char, "diff")
            elif left_char is not None:
                self.left_text.insert(tk.END, left_char, "diff")
                self.right_text.insert(tk.END, " ", "missing")
            elif right_char is not None:
                self.left_text.insert(tk.END, " ", "missing")
                self.right_text.insert(tk.END, right_char, "diff")

        # Scroll both text widgets back to the top.
        self.left_text.see("1.0")
        self.right_text.see("1.0")

        # Save this comparison in the history if both files are available.
        if self.left_file and self.right_file:
            self.history.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "left_file": self.left_file,
                "right_file": self.right_file
            })

if __name__ == "__main__":
    app = DiffApp()
    app.mainloop()
