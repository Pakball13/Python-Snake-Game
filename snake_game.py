# snake_game_V1.0
import tkinter as tk
import random
import math
from PIL import Image, ImageTk, ImageColor
import phrases

# ---------------- Constants ----------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 1600, 1200
SEG_SIZE = 20
PLAYER_SPEED = 10
NPC_SPEED = 8
MINIMAP_SIZE = 150
PIXEL_ICON_SIZE = 10
NPC_COLORS = ["blue","orange","purple","cyan","magenta","lime","pink","gold","dark blue","yellow","gray20"]
NPC_RANGE = 700

NPC_NAMES = [
    "Zyra","Kilo","Mako","Luna","Nova","Rex","Juno","Orion","Echo","Vega","Axel","Sora",
    "Lyra","Kael","Niko","Aria","Cyra","Drake","Eris","Talon","Nyx","Riven","Selin","Vior",
    "Kora","Axen","Lyric","Zane","Faye","Orin","Iris","Caius","Rhea","Jax","Liora","Veyra",
    "Tari","Dax","Saph","Noel","Kaia","Zorin","Eon","Mira","Ryker","Elara","Seth","Vexa",
    "Talon","Kira","Jace","Zylen","Novae","Luth","Nyra","Ober","Veyl","Cora","Ryn","Axia",
    "Lyven","Orla","Zyric","Kairo","Elys","Draven","Soren","Vira","Aeris","Kaelix","Nira",
    "Rogue","Zephyr","Lexus","Vyn","Orionis","Xyra","Celyn","Jorin","Myra","Axton","Lyricus",
    "Zypher","Kaelen","Rivena","Virael","Nox","Cairo","Selara","Drax","Veylin","Orya",
    "Jaxen","Liorael","Nyxen","Zyraen","Krynn","Axelus","Orvina","Erynd","Syla","Veyron",
    "Lyx","Kaelenor","Mavric","Rynel","Zypherin","Tavrix","Orlena","Veyla"
]

# ---------------- Helper Functions ----------------
def random_start_length():
    """Random length 1-7, rarer for 4-7"""
    r = random.random()
    if r < 0.6:
        return random.randint(1,3)
    elif r < 0.9:
        return 4
    elif r < 0.97:
        return 5
    elif r < 0.99:
        return 6
    return 7

def random_food_type():
    """Red=1, Yellow=2, Green=5 with rarities"""
    r = random.random()
    if r < 0.7: return ("red",1)
    elif r < 0.9: return ("yellow",2)
    return ("green",5)

# ---------------- Main Class ----------------
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("HSnake HGame")
        self.calc_font = ("Comic Neue Angular", 16)
        self.calc_font_large = ("28 Days Later", 24)
        self.death_font = ("ArcadeClassic", 20)

        # ---------------- Username Screen ----------------
        self.username_frame = tk.Frame(root, bg="black")
        tk.Label(self.username_frame, text="Enter Username:", font=self.calc_font, fg="yellow", bg="black").pack(pady=10)
        self.username_entry = tk.Entry(self.username_frame, font=self.calc_font)
        self.username_entry.pack(pady=5)
        tk.Button(self.username_frame, text="Continue", font=self.calc_font,
                  command=self.go_to_menu, bg="gray20", fg="yellow").pack(pady=10)
        self.username_frame.pack(expand=True)

        # ---------------- Splash Text ----------------
        self.text_canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=50, bg="black", highlightthickness=0)
        self.animated_text_id = None
        self.text_size = 24
        self.text_growing = True

        # ---------------- Menu ----------------
        self.menu_frame = tk.Frame(root, bg="black")
        tk.Button(self.menu_frame, text="Start Game", font=self.calc_font,
                  command=self.start_game, bg="gray20", fg="yellow").pack(pady=5)
        tk.Button(self.menu_frame, text="Make Skin", font=self.calc_font,
                  command=self.make_skin, bg="gray20", fg="yellow").pack(pady=5)
        tk.Button(self.menu_frame, text="Make Pixel Icon", font=self.calc_font,
                  command=self.make_icon, bg="gray20", fg="yellow").pack(pady=5)

        # ---------------- Canvas ----------------
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="black")
        self.restart_button = tk.Button(root, text="Restart", font=self.calc_font,
                                        command=self.restart_game,
                                        bg="gray20", fg="yellow")

        # ---------------- Game State ----------------
        self.username = ""
        self.snake = []
        self.foods = []
        self.npc_snakes = []
        self.running = False
        self.paused = False
        self.score = 0
        self.camera_x = 0
        self.camera_y = 0
        self.mouse_x = SCREEN_WIDTH//2
        self.mouse_y = SCREEN_HEIGHT//2
        self.pause_frame = None
        self.skin_pattern = ["light blue"]
        self.first_segment_icon = None
        self.leaderboard = []

        # Pixel Editor
        self.pixel_grid = []
        self.undo_stack = []
        self.redo_stack = []

        # Bindings
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Control-z>", self.ctrl_z)
        self.root.bind("<Control-y>", self.ctrl_y)

    # ---------------- Username Screen ----------------
    def go_to_menu(self):
        self.username = self.username_entry.get() or "Player"
        self.username_frame.pack_forget()
        self.show_menu()

    def show_menu(self):
        self.text_canvas.pack()
        self.menu_frame.pack(pady=10)
        self.update_phrase()
        self.animate_text()

    # ---------------- Splash Text ----------------
    def update_phrase(self):
        self.text_canvas.delete("all")
        phrase = random.choice(phrases.phrases)
        self.animated_text_id = self.text_canvas.create_text(SCREEN_WIDTH//2, 25,
                                                             text=phrase,
                                                             font=("OCR A Extended", self.text_size),
                                                             fill="yellow")
        self.root.after(3000, self.update_phrase)

    def animate_text(self):
        if not self.animated_text_id:
            self.root.after(50, self.animate_text)
            return
        if self.text_growing:
            self.text_size += 1
            if self.text_size >= 36:
                self.text_growing = False
        else:
            self.text_size -= 1
            if self.text_size <= 24:
                self.text_growing = True
        self.text_canvas.itemconfig(self.animated_text_id, font=("OCR A Extended", self.text_size))
        self.root.after(50, self.animate_text)

    # ---------------- Controls ----------------
    def on_key_press(self, event):
        if event.keysym == "Escape":
            self.toggle_pause()

    def on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            if not self.pause_frame:
                self.create_pause_frame()
            self.pause_frame.lift()
        else:
            if self.pause_frame:
                self.pause_frame.lower()
                self.update_game()

    def create_pause_frame(self):
        self.pause_frame = tk.Frame(self.canvas, bg="black")
        self.pause_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.pause_frame, text="Paused", font=self.calc_font_large, fg="yellow", bg="black").pack(pady=10)
        tk.Button(self.pause_frame, text="Quit", font=self.calc_font,
                  command=self.root.quit, bg="gray20", fg="yellow").pack(pady=5)
        tk.Button(self.pause_frame, text="Resume", font=self.calc_font,
                  command=self.toggle_pause, bg="gray20", fg="yellow").pack(pady=5)
        self.pause_frame.lower()

    # ---------------- Start & Reset ----------------
    def start_game(self):
        self.menu_frame.pack_forget()
        self.text_canvas.pack_forget()
        self.canvas.pack()
        self.restart_button.pack(pady=5)
        self.reset_game()
        self.running = True
        self.update_game()

    def reset_game(self):
        self.canvas.delete("all")
        px = random.randint(SEG_SIZE, MAP_WIDTH - SEG_SIZE*2)
        py = random.randint(SEG_SIZE, MAP_HEIGHT - SEG_SIZE*2)
        start_len = random_start_length()
        self.snake = [(px, py)]*start_len
        self.foods = [self.create_food() for _ in range(10)]
        self.score = 0
        self.paused = False

        # NPCs
        self.npc_snakes = []
        used_names = set()
        for _ in range(5):
            x = random.randint(SEG_SIZE, MAP_WIDTH - SEG_SIZE*2)
            y = random.randint(SEG_SIZE, MAP_HEIGHT - SEG_SIZE*2)
            npc_name = random.choice(NPC_NAMES)
            while npc_name in used_names:
                npc_name = random.choice(NPC_NAMES)
            used_names.add(npc_name)
            npc_len = random_start_length()
            self.npc_snakes.append({
                "body": [(x,y)]*npc_len,
                "color": random.choice(NPC_COLORS),
                "name": npc_name
            })

    # ---------------- Food ----------------
    def create_food(self):
        while True:
            x = random.randint(SEG_SIZE*2, (MAP_WIDTH-SEG_SIZE*3)//SEG_SIZE)*SEG_SIZE
            y = random.randint(SEG_SIZE*2, (MAP_HEIGHT-SEG_SIZE*3)//SEG_SIZE)*SEG_SIZE
            if (x,y) not in self.snake and all((x,y) not in npc["body"] for npc in self.npc_snakes):
                ftype,value = random_food_type()
                return (x,y,ftype,value)

    # ---------------- Skin & Icon Editors ----------------
    def make_skin(self):
        win = tk.Toplevel(self.root)
        win.title("HSkin HEditor")
        tk.Label(win, text="Enter colors for your snake:", font=self.calc_font).pack()
        entries=[]
        for i in range(10):
            e = tk.Entry(win)
            e.insert(0, "light blue" if i==0 else "")
            e.pack()
            entries.append(e)
        def save():
            self.skin_pattern = [e.get() for e in entries if e.get()]
            if not self.skin_pattern: self.skin_pattern=["green"]
            win.destroy()
        tk.Button(win, text="Save", command=save).pack()

    def make_icon(self):
        win = tk.Toplevel(self.root)
        win.title("HPixel HIcon HEditor")
        grid=[]
        for i in range(PIXEL_ICON_SIZE):
            row=[]
            for j in range(PIXEL_ICON_SIZE):
                b = tk.Button(win, bg="white", width=2, height=1)
                b.grid(row=i,column=j)
                row.append(b)
            grid.append(row)
        tk.Label(win, text="Color:").grid(row=PIXEL_ICON_SIZE,column=0)
        color_entry = tk.Entry(win)
        color_entry.insert(0,"red")
        color_entry.grid(row=PIXEL_ICON_SIZE,column=1)
        def save_icon():
            img = Image.new("RGBA",(SEG_SIZE,SEG_SIZE))
            scale=SEG_SIZE//PIXEL_ICON_SIZE
            for i in range(PIXEL_ICON_SIZE):
                for j in range(PIXEL_ICON_SIZE):
                    color=grid[i][j]["bg"]
                    if color!="white":
                        for dx in range(scale):
                            for dy in range(scale):
                                img.putpixel((j*scale+dx,i*scale+dy), ImageColor.getrgb(color)+(255,))
            self.first_segment_icon = ImageTk.PhotoImage(img)
            win.destroy()
        tk.Button(win, text="Save", command=save_icon).grid(row=PIXEL_ICON_SIZE,column=2)

# ---------------- Run ----------------
if __name__=="__main__":
    root=tk.Tk()
    game=SnakeGame(root)
    root.mainloop()

