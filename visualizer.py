import tkinter as tk
from collections import deque
import time

ROWS = 20
COLS = 30
CELL_SIZE = 25

# 🌌 GLASS NEON THEME 
BG = "#0a0f1c"          
GRID = "#121a2b"       
WALL = "#2a3550"     
START = "#4ade80"      
END = "#fb7185"         
VISITED = "#818cf8"     
FRONTIER = "#22d3ee"    
PATH = "#facc15"        
TEXT = "#e5e7eb"        

class Node:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.wall = False
        self.visited = False
        self.parent = None

class Visualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Smart DSA Visualizer")
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(root,
                                width=COLS*CELL_SIZE,
                                height=ROWS*CELL_SIZE,
                                bg=BG,
                                highlightthickness=0)
        self.canvas.pack(pady=10)

        self.grid = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.rects = {}

        self.start = None
        self.end = None
        self.mode = "wall"
        self.drawing = False
        self.start_time = 0

        self.draw_grid()

        # 🖱️ Mouse
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, 'drawing', False))

        # 🎮 Controls
        frame = tk.Frame(root, bg=BG)
        frame.pack(pady=10)

        def styled_button(text, cmd):
            return tk.Button(frame,
                             text=text,
                             command=cmd,
                             bg="#1f2937",
                             fg="white",
                             activebackground="#374151",
                             relief="flat",
                             padx=10,
                             pady=5)

        styled_button("Start", lambda: self.set_mode("start")).pack(side="left", padx=5)
        styled_button("End", lambda: self.set_mode("end")).pack(side="left", padx=5)
        styled_button("Walls", lambda: self.set_mode("wall")).pack(side="left", padx=5)
        styled_button("BFS 🌊", self.start_bfs).pack(side="left", padx=5)
        styled_button("DFS 🔍", self.start_dfs).pack(side="left", padx=5)
        styled_button("Reset", self.reset).pack(side="left", padx=5)

        # 🎚️ Speed
        self.speed = tk.Scale(frame,
                              from_=1, to=100,
                              orient="horizontal",
                              label="Speed",
                              bg=BG,
                              fg=TEXT,
                              troughcolor="#1f2937",
                              highlightthickness=0)
        self.speed.set(40)
        self.speed.pack(side="left", padx=10)

        # 📊 Status Label
        self.status_label = tk.Label(root,
                                    text="Ready",
                                    bg=BG,
                                    fg=TEXT,
                                    font=("Segoe UI", 12))
        self.status_label.pack(pady=5)

    # 🧱 Grid
    def draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=GRID,
                    outline=BG
                )
                self.rects[(r, c)] = rect

    def color(self, r, c, color):
        self.canvas.itemconfig(self.rects[(r, c)], fill=color)

    def set_mode(self, mode):
        self.mode = mode

    def get_cell(self, event):
        return event.y // CELL_SIZE, event.x // CELL_SIZE

    # 🖱️ Interaction
    def click(self, event):
        self.drawing = True
        self.handle(event)

    def drag(self, event):
        if self.drawing:
            self.handle(event)

    def handle(self, event):
        r, c = self.get_cell(event)
        if r < 0 or c < 0 or r >= ROWS or c >= COLS:
            return

        node = self.grid[r][c]

        if self.mode == "start":
            if self.start:
                self.color(self.start.r, self.start.c, GRID)
            self.start = node
            self.color(r, c, START)

        elif self.mode == "end":
            if self.end:
                self.color(self.end.r, self.end.c, GRID)
            self.end = node
            self.color(r, c, END)

        elif self.mode == "wall":
            if node not in [self.start, self.end]:
                node.wall = True
                self.color(r, c, WALL)

    # 🔍 Neighbors
    def neighbors(self, node):
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        result = []
        for dr, dc in dirs:
            r, c = node.r + dr, node.c + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                if not self.grid[r][c].wall:
                    result.append(self.grid[r][c])
        return result

    # 🌊 Animation
    def animate_wave(self, structure, is_bfs=True):
        if not structure:
            # ❌ No path
            end_time = (time.time() - self.start_time) * 1000
            self.status_label.config(
                text=f"No path found 🚫 | Time: {end_time:.2f} ms"
            )
            return

        next_batch = []

        for _ in range(len(structure)):
            node = structure.popleft() if is_bfs else structure.pop()

            if node == self.end:
                # ✅ Found
                end_time = (time.time() - self.start_time) * 1000
                self.status_label.config(
                    text=f"Path found ✅ | Time: {end_time:.2f} ms"
                )
                self.show_path(node)
                return

            if node != self.start:
                self.color(node.r, node.c, VISITED)

            for n in self.neighbors(node):
                if not n.visited:
                    n.visited = True
                    n.parent = node
                    next_batch.append(n)

        for n in next_batch:
            if n != self.end:
                self.color(n.r, n.c, FRONTIER)

        delay = int(120 - self.speed.get())

        if is_bfs:
            structure.extend(next_batch)
        else:
            structure.extend(reversed(next_batch))

        self.root.after(delay, lambda: self.animate_wave(structure, is_bfs))

    # ▶️ Start
    def start_bfs(self):
        if not self.start or not self.end:
            self.status_label.config(text="Please set Start & End ⚠️")
            return
        self.clear()
        self.start_time = time.time()
        self.status_label.config(text="Running BFS...")
        q = deque([self.start])
        self.start.visited = True
        self.animate_wave(q, True)

    def start_dfs(self):
        if not self.start or not self.end:
            self.status_label.config(text="Please set Start & End ⚠️")
            return
        self.clear()
        self.start_time = time.time()
        self.status_label.config(text="Running DFS...")
        stack = [self.start]
        self.start.visited = True
        self.animate_wave(stack, False)

    # 🎯 Path animation
    def show_path(self, node):
        path = []
        while node.parent:
            path.append(node)
            node = node.parent
        self.animate_path(path[::-1], 0)

    def animate_path(self, path, i):
        if i >= len(path):
            return
        node = path[i]
        if node != self.end:
            self.color(node.r, node.c, PATH)
        self.root.after(30, lambda: self.animate_path(path, i + 1))

    # 🧹 Clear
    def clear(self):
        for row in self.grid:
            for node in row:
                node.visited = False
                node.parent = None
                if not node.wall and node not in [self.start, self.end]:
                    self.color(node.r, node.c, GRID)

    # 🔄 Reset
    def reset(self):
        for r in range(ROWS):
            for c in range(COLS):
                node = self.grid[r][c]
                node.wall = False
                node.visited = False
                node.parent = None
                self.color(r, c, GRID)
        self.start = None
        self.end = None
        self.status_label.config(text="Ready")


# 🚀 Run
if __name__ == "__main__":
    root = tk.Tk()
    app = Visualizer(root)
    root.mainloop()