import time

class QueensSolver:
    def __init__(self, n, grid, enable_optimization=False):
        self.n = n
        self.grid = grid
        self.enable_optimization = enable_optimization
        self.solution = [[" " for _ in range(n)] for _ in range(n)]
        self.queen_positions = [-1] * n
        self.iterations = 0
        self.last_update_time = time.time()
        
    def is_valid_fullboard(self):  
        # Periksa kolom
        if len(set(self.queen_positions)) != self.n:
            return False
            
        # Periksa warna
        used_colors = set()
        for r in range(self.n):
            c = self.queen_positions[r]
            color = self.grid[r][c]
            if color in used_colors:
                return False
            used_colors.add(color)
            
        # Periksa tetangga diagonal
        for r in range(self.n - 1):
            c1 = self.queen_positions[r]
            c2 = self.queen_positions[r+1]
            if abs(c1 - c2) <= 1:
                return False         
        return True

    def is_valid_sofar(self, row, col):
        for r in range(row):
            if self.queen_positions[r] == col: 
                return False
        current_color = self.grid[row][col]
        for r in range(row):
            if self.grid[r][self.queen_positions[r]] == current_color: 
                return False
        if row > 0:
            if abs(self.queen_positions[row-1] - col) <= 1: 
                return False
        return True

    def live_update(self, gui_callback=None):
        current_time = time.time()
        # Iterasi bisa ditingkatkan untuk waktu efektivitas lebih cepat
        if self.iterations % 10000 == 0 or (current_time - self.last_update_time) > 0.3:
            if gui_callback:
                gui_callback(self.solution, self.iterations)
            self.last_update_time = current_time


    def solve(self, row, gui_callback=None, stop_check=None):
        if stop_check and stop_check(): 
            return False
        
        # Basis
        if row == self.n:
            if self.enable_optimization:
                return True
            else:
                return self.is_valid_fullboard()
        
        for col in range(self.n):
            if stop_check and stop_check(): 
                return False

            self.iterations += 1
            self.live_update(gui_callback)
            
            self.queen_positions[row] = col
            self.solution[row][col] = "#"
            
            if self.enable_optimization:
                # Pruning 
                if self.is_valid_sofar(row, col):
                    if self.solve(row + 1, gui_callback, stop_check): 
                        return True
            else:
                # Brute force
                if self.solve(row + 1, gui_callback, stop_check): 
                    return True
            
            # Reset (Backtrack)
            self.solution[row][col] = " "
            self.queen_positions[row] = -1

        return False