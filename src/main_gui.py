import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import time
import threading
import os
import ctypes
import sys
from PIL import Image, ImageTk, ImageGrab  
from queens_solver import QueensSolver 


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass

class ModernQueensGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "..", "assets")
        
        icon_ico = os.path.join(self.assets_dir, "crowns.ico")
        icon_png = os.path.join(self.assets_dir, "crowns.png")  

        try:
            if sys.platform.startswith("win"):
                self.iconbitmap(icon_ico)
            else:
                img = Image.open(icon_png)
                self.iconphoto(False, ImageTk.PhotoImage(img))
        except Exception as e:
            print(f"Failed to set window icon: {e}")


        self.title("Queens Game Solver")
        self.geometry("900x850")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.file_path = ""
        self.grid_data = []
        self.stop_requested = False
        self.color_map = self._generate_pastel_colors()
        self.crown_image = None  
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.container.grid_columnconfigure(0, weight=1)

        self.page_intro()

    def _generate_pastel_colors(self):
        colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#D4A5A5", 
                  "#FF9AA2", "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA",
                  "#F8B195", "#F67280", "#C06C84", "#6C5B7B", "#355C7D", "#A8E6CF",
                  "#DCEDC1", "#FFD3B6", "#FFAAA5", "#FF8B94", "#D1D1D1", "#A2D2FF",
                  "#BDE0FE", "#FFC8DD"]
        return {chr(65+i): colors[i] for i in range(26)}
    
    def asset_path(self, filename: str) -> str:
        return os.path.join(self.assets_dir, filename)

    
    def _set_mode(self, mode_value: int):
        self.mode_var.set(mode_value)
        self._refresh_mode_cards()

    def _refresh_mode_cards(self):
        selected_bg = "#EEF2FF"     
        selected_border = "#4F46E5" 
        normal_bg = "#FFFFFF"
        normal_border = "#E5E7EB"

        for val, card in self._mode_cards.items():
            if self.mode_var.get() == val:
                card.configure(fg_color=selected_bg, border_color=selected_border, border_width=2)
            else:
                card.configure(fg_color=normal_bg, border_color=normal_border, border_width=1)


    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        for r in range(10):
            self.container.grid_rowconfigure(r, weight=0)
        for c in range(10):
            self.container.grid_columnconfigure(c, weight=0)


    def make_perfect_center(self) -> ctk.CTkFrame:
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=0)
        self.container.grid_rowconfigure(2, weight=1)

        wrapper = ctk.CTkFrame(self.container, fg_color="transparent")
        wrapper.grid(row=1, column=0) 
        return wrapper


    def make_top_header_center_body(self):
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=0) 
        self.container.grid_rowconfigure(1, weight=1)  

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(10, 0))

        body_area = ctk.CTkFrame(self.container, fg_color="transparent")
        body_area.grid(row=1, column=0, sticky="nsew")

        body_area.grid_columnconfigure(0, weight=1)
        body_area.grid_rowconfigure(0, weight=1)
        body_area.grid_rowconfigure(1, weight=0)
        body_area.grid_rowconfigure(2, weight=1)

        body = ctk.CTkFrame(body_area, fg_color="transparent")
        body.grid(row=1, column=0) 

        return header, body



    def page_intro(self):
        self.clear_container()
        self.stop_requested = False

        w = self.make_perfect_center()

        ctk.CTkLabel(w, text="Queens Game Solver", font=("Inter", 42, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(w, text="Insert your puzzle file to begin (Max 26x26)", font=("Inter", 16)).pack(pady=(0, 40))

        self.btn_browse = ctk.CTkButton(
            w, text="Select File (.txt)", width=200, height=45, corner_radius=22,
            command=self.browse_file, font=("Inter", 14, "bold")
        )
        self.btn_browse.pack(pady=10)

        self.lbl_filename = ctk.CTkLabel(w, text="No file selected", text_color="gray")
        self.lbl_filename.pack(pady=5)

        self.btn_next = ctk.CTkButton(
            w, text="Continue", width=200, height=45, corner_radius=22,
            fg_color="#E5E7EB", text_color="gray", state="disabled",
            command=self.page_method, font=("Inter", 14, "bold")
        )
        self.btn_next.pack(pady=40)



    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            is_valid, result = self.validate_file(path)
            
            if is_valid:
                self.file_path = path
                self.lbl_filename.configure(text=f"{os.path.basename(path)} ({result}x{result})", text_color="#4F46E5")
                self.btn_next.configure(state="normal", fg_color="#4F46E5", text_color="white")
            else:
                messagebox.showerror("Invalid Test Case", result)
                self.file_path = ""
                self.lbl_filename.configure(text="No file selected", text_color="gray")
                self.btn_next.configure(state="disabled", fg_color="#E5E7EB", text_color="gray")

    def page_method(self):
        self.clear_container()

        w = self.make_perfect_center()

        ctk.CTkLabel(w, text="Choose Strategy", font=("Inter", 32, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(w, text="Pick one method to solve the puzzle", font=("Inter", 14), text_color="#6B7280").pack(pady=(0, 30))

        self.mode_var = ctk.IntVar(value=1)
        self._mode_cards = {}

        cards = ctk.CTkFrame(w, fg_color="transparent")
        cards.pack(pady=0)

        def load_icon(filename: str, size=(42, 42)):
            path = self.asset_path(filename)
            try:
                img = Image.open(path)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception as e:
                print("Icon load failed:", path, e)
                return None


        self.brute_icon = load_icon("purebf_icon.png")
        self.opt_icon   = load_icon("optimization_icon.png")


        def make_card(parent, value: int, title: str, subtitle: str, icon):
            card = ctk.CTkFrame(
                parent,
                width=520,
                corner_radius=18,
                fg_color="#FFFFFF",
                border_color="#E5E7EB",
                border_width=1
            )
            card.pack(pady=10, fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=18, pady=16, fill="x")

            if icon is not None:
                icon_lbl = ctk.CTkLabel(inner, text="", image=icon)
                icon_lbl.pack(side="left", padx=(0, 14))
            else:
                icon_lbl = None

            text_col = ctk.CTkFrame(inner, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True)

            title_lbl = ctk.CTkLabel(text_col, text=title, font=("Inter", 18, "bold"), text_color="#111827")
            title_lbl.pack(anchor="w")

            sub_lbl = ctk.CTkLabel(text_col, text=subtitle, font=("Inter", 13), text_color="#6B7280")
            sub_lbl.pack(anchor="w", pady=(2, 0))


            hover_bg = "#F9FAFB"
            def on_enter(_=None):
                if self.mode_var.get() != value:
                    card.configure(fg_color=hover_bg)

            def on_leave(_=None):
                if self.mode_var.get() != value:
                    card.configure(fg_color="#FFFFFF")

            def on_click(_=None):
                self._set_mode(value)


            widgets_to_bind = [card, inner, text_col, title_lbl, sub_lbl]
            if icon_lbl is not None:
                widgets_to_bind.append(icon_lbl)

            for wd in widgets_to_bind:
                wd.bind("<Enter>", on_enter)
                wd.bind("<Leave>", on_leave)
                wd.bind("<Button-1>", on_click)
                wd.configure(cursor="hand2")

            return card


        brute_card = make_card(
            cards, 1,
            "Exhaustive Search (Brute Force)",
            "Try all possibilities. Slower on n > 8 boards.",
            self.brute_icon
        )

        self._mode_cards[1] = brute_card

        opt_card = make_card(
            cards, 2,
            "Optimization (Pruning)",
            "Prune invalid paths early. Much faster on larger boards.",
            self.opt_icon
        )

        self._mode_cards[2] = opt_card

        self._refresh_mode_cards()
    
        ctk.CTkButton(
            w, text="Launch Solver", text_color="#FFFFFF", width=220, height=48, corner_radius=24,
            fg_color="#10B981", hover_color="#059669", font=("Inter", 16, "bold"),
            command=self.page_solving
        ).pack(pady=(30, 0))



    def page_solving(self):
        with open(self.file_path, 'r') as f:
            self.grid_data = [line.strip() for line in f if line.strip()]
        self.n = len(self.grid_data)

        self.clear_container()

        header, body = self.make_top_header_center_body()

        self.lbl_iter = ctk.CTkLabel(header, text="Iterations: 0", font=("JetBrains Mono", 16, "bold"))
        self.lbl_iter.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(
            header, text="STOP",text_color="#FFFFFF", width=80, corner_radius=12, fg_color="#EF4444",
            command=self.request_stop, font=("Inter", 12, "bold")
        )
        self.btn_stop.pack(side="right", padx=10)

        size = 550
        self.cell_size = size // self.n

        try:
            img = Image.open(self.asset_path("crowns.png"))

            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS 

            img = img.resize(
                (int(self.cell_size * 0.8), int(self.cell_size * 0.8)),
                resample=resample
            )

            self.crown_image = ImageTk.PhotoImage(img)

        except Exception as e:
            messagebox.showwarning(
                "Image Error",
                f"Failed to load crowns.png: {e}\n"
            )
            self.crown_image = None


        self.canvas = tk.Canvas(body, width=size, height=size, bg="white", highlightthickness=0)
        self.canvas.pack(pady=(0, 20))
        self.draw_grid()

        mode = (self.mode_var.get() == 2)
        self.solver = QueensSolver(self.n, self.grid_data, enable_optimization=mode)
        threading.Thread(target=self.run_solver, daemon=True).start()
        self.solving_body = body

    def draw_grid(self):
        for r in range(self.n):
            for c in range(self.n):
                color = self.color_map.get(self.grid_data[r][c], "#FFFFFF")
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#D1D5DB")

    def request_stop(self):
        self.stop_requested = True
        messagebox.showinfo("Stopped", "Process terminated")
        self.page_intro()

    def update_ui(self, board_str, iters):
        if self.stop_requested:
            return

        try:
            if self.lbl_iter.winfo_exists():
                self.lbl_iter.configure(text=f"Iterations: {iters:,}")

            if not self.canvas.winfo_exists():
                return

            if self.crown_image is None:
                return

            self.canvas.delete("queen")

            for row_idx, col_idx in enumerate(self.solver.queen_positions):
                if col_idx != -1:
                    x = (col_idx * self.cell_size) + (self.cell_size // 2)
                    y = (row_idx * self.cell_size) + (self.cell_size // 2)
                    self.canvas.create_image(x, y, image=self.crown_image, tags="queen")

            self.update_idletasks()

        except (tk.TclError, RuntimeError):
            pass


    def run_solver(self):
        start_t = time.perf_counter()
        found = self.solver.solve(0, gui_callback=self.update_ui, stop_check=lambda: self.stop_requested)
        exec_ms = (time.perf_counter() - start_t) * 1000
        
        if self.stop_requested: 
            return
        
        if found:
            self.update_ui(None, self.solver.iterations)
            
            self.lbl_iter.configure(text=f"Total: {self.solver.iterations:,} cases | Searched in {int(exec_ms)}ms")
            
            if self.btn_stop.winfo_exists():
                self.btn_stop.pack_forget() 

            parent = getattr(self, "solving_body", self.container)
            self.action_frame = ctk.CTkFrame(parent, fg_color="transparent")

            self.action_frame.pack(pady=20)

            self.save_image_btn = ctk.CTkButton(self.action_frame, text="Save as Image",text_color="#FFFFFF", width=150, height=40, corner_radius=20,
                                                fg_color="#36A35F", hover_color="#2C8D50", font=("Inter", 12, "bold"),
                                                command=self.save_canvas_as_image)
            self.save_image_btn.pack(side="left", padx=10)

            self.save_txt_btn = ctk.CTkButton(self.action_frame, text="Save as .txt",text_color="#FFFFFF", width=150, height=40, corner_radius=20,
                                              fg_color="#4F46E5", hover_color="#4338CA", font=("Inter", 12, "bold"),
                                              command=lambda: self.save_results(exec_ms))
            self.save_txt_btn.pack(side="left", padx=10)

            self.back_btn = ctk.CTkButton(self.action_frame, text="Back", text_color="#FFFFFF", width=150, height=40, corner_radius=20,
                                          fg_color="#6B7280", hover_color="#4B5563", font=("Inter", 12, "bold"),
                                          command=self.page_intro)
            self.back_btn.pack(side="left", padx=10)
        else:
            messagebox.showwarning("Failed", "No solution found.")
            self.page_intro()

    def save_results(self, exec_ms):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, 'w') as f:
                for r in range(self.n):
                    row = "".join(["#" if self.solver.queen_positions[r] == c else self.grid_data[r][c] for c in range(self.n)])
                    f.write(row + "\n")
                f.write(f"\nTime: {int(exec_ms)} ms\nCases: {self.solver.iterations}")
            messagebox.showinfo("Saved", f"The solution saved as {os.path.basename(path)}.")

    def save_canvas_as_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

            from PIL import ImageGrab 
            ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(file_path)
            
            messagebox.showinfo("Saved", f"Board saved as {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")


    def validate_file(self, path):
        try:
            with open(path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                return False, "File is empty."
            
            n = len(lines)
            
            if n > 26:
                return False, f"Board size ({n}x{n}) is over the limit of 26x26."
            
            for i, line in enumerate(lines):
                if len(line) != n:
                    return False, f"Format must be NxN. Row {i+1} has length {len(line)}, should be {n}."
                if not line.isalpha() or not line.isupper():
                    return False, f"Invalid character on row {i+1}. Only capital letters A-Z are allowed."

            visited = [[False for _ in range(n)] for _ in range(n)]
            color_found = set() 

            for r in range(n):
                for c in range(n):
                    char = lines[r][c]
                    if not visited[r][c]:
                        if char in color_found:
                            return False, f"Color '{char}' is not valid because it is separated (disconnected)."
                        
                        self._flood_fill(lines, visited, r, c, char, n)
                        color_found.add(char)

            return True, n
        except Exception as e:
            return False, f"Failed to read file: {str(e)}"

    def _flood_fill(self, grid, visited, r, c, target_char, n):
        stack = [(r, c)]
        while stack:
            curr_r, curr_c = stack.pop()
            if curr_r < 0 or curr_r >= n or curr_c < 0 or curr_c >= n:
                continue
            if visited[curr_r][curr_c] or grid[curr_r][curr_c] != target_char:
                continue
            
            visited[curr_r][curr_c] = True
            stack.append((curr_r + 1, curr_c))
            stack.append((curr_r - 1, curr_c))
            stack.append((curr_r, curr_c + 1))
            stack.append((curr_r, curr_c - 1))


if __name__ == "__main__":
    app = ModernQueensGUI()
    app.mainloop()