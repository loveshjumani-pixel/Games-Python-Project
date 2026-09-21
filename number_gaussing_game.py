"""
============================================================
  NUMBER GUESSING GAME - Professional Edition
  Author: AI Assistant
  Language: Python 3 (Tkinter - built-in)
  Run: python guessing_game.py
============================================================
"""

import tkinter as tk
from tkinter import messagebox
import random
import math

# ---------------- CONFIGURATION ----------------
DIFFICULTY = {
    "Easy":   {"range": 50,  "attempts": 10, "color": "#4ade80"},
    "Medium": {"range": 100, "attempts": 7,  "color": "#facc15"},
    "Hard":   {"range": 500, "attempts": 10, "color": "#f87171"},
}

COLORS = {
    "bg":        "#0f172a",
    "panel":     "#1e293b",
    "panel2":    "#334155",
    "fg":        "#e2e8f0",
    "accent":    "#38bdf8",
    "accent2":   "#818cf8",
    "success":   "#22c55e",
    "danger":    "#ef4444",
    "warning":   "#f59e0b",
    "muted":     "#94a3b8",
}


class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Number Guessing Game")
        self.root.geometry("900x650")
        self.root.minsize(850, 600)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # Center the window
        self.root.update_idletasks()
        w, h = 900, 650
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Game state
        self.secret = 0
        self.max_num = 100
        self.max_attempts = 7
        self.attempts_left = 7
        self.guesses = []
        self.game_over = False
        self.total_score = 0
        self.games_played = 0
        self.difficulty = "Medium"

        self._build_ui()
        self.new_game()

        # Keyboard binding
        self.root.bind("<Return>", lambda e: self.submit_guess())

    # ---------------- UI BUILD ----------------
    def _build_ui(self):
        # Title
        title = tk.Label(
            self.root, text="🎯 NUMBER GUESSING GAME",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        )
        title.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root, text="Apna dimaag lagao aur secret number dhundho!",
            font=("Segoe UI", 11),
            bg=COLORS["bg"], fg=COLORS["muted"]
        )
        subtitle.pack()

        # Main container
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # LEFT PANEL - Game Controls
        left = tk.Frame(main, bg=COLORS["panel"], bd=0, highlightbackground=COLORS["panel2"], highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Difficulty selector
        diff_frame = tk.Frame(left, bg=COLORS["panel"])
        diff_frame.pack(pady=15)
        tk.Label(diff_frame, text="Difficulty:", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left", padx=5)
        self.diff_var = tk.StringVar(value=self.difficulty)
        for name in DIFFICULTY:
            rb = tk.Radiobutton(
                diff_frame, text=name, variable=self.diff_var, value=name,
                font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["fg"],
                selectcolor=COLORS["panel2"], activebackground=COLORS["panel"],
                activeforeground=COLORS["accent"],
                command=self._on_diff_change
            )
            rb.pack(side="left", padx=8)

        # Info display
        self.info_label = tk.Label(left, text="", font=("Segoe UI", 12),
                                   bg=COLORS["panel"], fg=COLORS["fg"], wraplength=380)
        self.info_label.pack(pady=10)

        # Attempts progress bar
        prog_frame = tk.Frame(left, bg=COLORS["panel"])
        prog_frame.pack(fill="x", padx=20, pady=5)
        self.prog_label = tk.Label(prog_frame, text="Attempts: 0/0",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["fg"])
        self.prog_label.pack(anchor="w")
        self.progress_canvas = tk.Canvas(prog_frame, height=18, bg=COLORS["panel2"],
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x", pady=(5, 0))

        # Input area
        input_frame = tk.Frame(left, bg=COLORS["panel"])
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="Your Guess:", font=("Segoe UI", 11),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left", padx=5)
        self.entry = tk.Entry(input_frame, font=("Segoe UI", 16, "bold"), width=10,
                              bg=COLORS["panel2"], fg=COLORS["fg"],
                              insertbackground=COLORS["fg"],
                              relief="flat", bd=5, justify="center")
        self.entry.pack(side="left", padx=5)
        self.entry.focus_set()

        # Buttons
        btn_frame = tk.Frame(left, bg=COLORS["panel"])
        btn_frame.pack(pady=10)
        self.submit_btn = tk.Button(
            btn_frame, text="✔ Guess", font=("Segoe UI", 12, "bold"),
            bg=COLORS["accent"], fg="#0f172a", activebackground=COLORS["accent2"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self.submit_guess
        )
        self.submit_btn.pack(side="left", padx=5)

        self.new_btn = tk.Button(
            btn_frame, text="🔄 New Game", font=("Segoe UI", 12, "bold"),
            bg=COLORS["panel2"], fg=COLORS["fg"], activebackground=COLORS["accent"],
            relief="flat", padx=15, pady=8, cursor="hand2",
            command=self.new_game
        )
        self.new_btn.pack(side="left", padx=5)

        self.quit_btn = tk.Button(
            btn_frame, text="✖ Quit", font=("Segoe UI", 12, "bold"),
            bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
            relief="flat", padx=15, pady=8, cursor="hand2",
            command=self.root.quit
        )
        self.quit_btn.pack(side="left", padx=5)

        # Hint / message
        self.hint_label = tk.Label(left, text="", font=("Segoe UI", 13, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["warning"], wraplength=380)
        self.hint_label.pack(pady=10)

        # RIGHT PANEL - History & Score
        right = tk.Frame(main, bg=COLORS["panel"], highlightbackground=COLORS["panel2"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Score
        score_frame = tk.Frame(right, bg=COLORS["panel"])
        score_frame.pack(pady=15, fill="x", padx=15)
        self.score_label = tk.Label(score_frame, text="🏆 Score: 0",
                                    font=("Segoe UI", 14, "bold"),
                                    bg=COLORS["panel"], fg=COLORS["success"])
        self.score_label.pack(side="left")
        self.games_label = tk.Label(score_frame, text="Games: 0",
                                    font=("Segoe UI", 12),
                                    bg=COLORS["panel"], fg=COLORS["muted"])
        self.games_label.pack(side="right")

        # History title
        tk.Label(right, text="📜 Guess History", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(0, 5))

        # History listbox
        list_frame = tk.Frame(right, bg=COLORS["panel2"])
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.history_list = tk.Listbox(
            list_frame, font=("Consolas", 11),
            bg=COLORS["panel2"], fg=COLORS["fg"],
            selectbackground=COLORS["accent"],
            relief="flat", bd=0, highlightthickness=0
        )
        scrollbar = tk.Scrollbar(list_frame, command=self.history_list.yview)
        self.history_list.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.history_list.pack(side="left", fill="both", expand=True)

        # Status bar
        self.status = tk.Label(self.root, text="Ready to play? Enter a number and press Guess!",
                               font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["muted"],
                               anchor="w", padx=20)
        self.status.pack(side="bottom", fill="x", pady=5)

    # ---------------- GAME LOGIC ----------------
    def _on_diff_change(self):
        self.difficulty = self.diff_var.get()
        self.new_game()

    def new_game(self):
        cfg = DIFFICULTY[self.difficulty]
        self.max_num = cfg["range"]
        self.max_attempts = cfg["attempts"]
        self.attempts_left = self.max_attempts
        self.secret = random.randint(1, self.max_num)
        self.guesses = []
        self.game_over = False

        self.info_label.config(
            text=f"🎲 Maine 1 se {self.max_num} ke beech ek number socha hai.\n"
                 f"Aapke paas {self.max_attempts} attempts hain. Best of luck!",
            fg=COLORS["fg"]
        )
        self.hint_label.config(text="", fg=COLORS["warning"])
        self.entry.delete(0, tk.END)
        self.entry.config(state="normal")
        self.submit_btn.config(state="normal", bg=COLORS["accent"])
        self.history_list.delete(0, tk.END)
        self._update_progress()
        self.entry.focus_set()
        self.status.config(text=f"New game started! Range: 1 - {self.max_num}")

    def _update_progress(self):
        used = self.max_attempts - self.attempts_left
        self.prog_label.config(text=f"Attempts: {used}/{self.max_attempts}")
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width() or 380
        h = 18
        fill_ratio = used / self.max_attempts if self.max_attempts else 0
        # Color transitions: green -> yellow -> red
        if fill_ratio < 0.5:
            color = COLORS["success"]
        elif fill_ratio < 0.8:
            color = COLORS["warning"]
        else:
            color = COLORS["danger"]
        self.progress_canvas.create_rectangle(0, 0, w * fill_ratio, h, fill=color, outline="")

    def submit_guess(self):
        if self.game_over:
            return
        raw = self.entry.get().strip()
        if not raw:
            self._flash_message("⚠ Please enter a number!", COLORS["danger"])
            return
        try:
            guess = int(raw)
        except ValueError:
            self._flash_message("⚠ Sirf numbers allowed hain!", COLORS["danger"])
            self.entry.delete(0, tk.END)
            return

        if guess < 1 or guess > self.max_num:
            self._flash_message(f"⚠ Number 1 se {self.max_num} ke beech hona chahiye!", COLORS["danger"])
            self.entry.delete(0, tk.END)
            return

        self.attempts_left -= 1
        self.guesses.append(guess)

        # Determine hint
        if guess == self.secret:
            self._win(guess)
        elif self.attempts_left == 0:
            self._lose()
        else:
            direction = "📈 TOO LOW!  Try bigger." if guess < self.secret else "📉 TOO HIGH! Try smaller."
            diff = abs(guess - self.secret)
            # Hot/Cold
            range_size = self.max_num
            if diff <= range_size * 0.05:
                hot = " 🔥 BILKUL PAAS!"
            elif diff <= range_size * 0.15:
                hot = " 🌡️ Hot!"
            elif diff <= range_size * 0.30:
                hot = " 😐 Warm"
            else:
                hot = " ❄️ Cold"
            self.hint_label.config(text=direction + hot, fg=COLORS["warning"])
            self._add_history(guess, "❯" if guess < self.secret else "❮")
            self._update_progress()
            self.status.config(text=f"Attempts left: {self.attempts_left}")

        self.entry.delete(0, tk.END)
        self.entry.focus_set()

    def _add_history(self, guess, arrow):
        tag = f"#{len(self.guesses):02d}  {arrow}  {guess}"
        self.history_list.insert(0, tag)
        self.history_list.yview_moveto(0)

    def _win(self, guess):
        self.game_over = True
        used = self.max_attempts - self.attempts_left
        # Score: more points for harder difficulty and fewer attempts
        base = {"Easy": 50, "Medium": 100, "Hard": 200}[self.difficulty]
        bonus = max(0, (self.max_attempts - used + 1) * 10)
        earned = base + bonus
        self.total_score += earned
        self.games_played += 1

        self.info_label.config(
            text=f"🎉 CONGRATULATIONS!\nAapne number {guess} sirf {used} attempt(s) me dhundh liya!",
            fg=COLORS["success"]
        )
        self.hint_label.config(text=f"+{earned} points earned! 🏆", fg=COLORS["success"])
        self.score_label.config(text=f"🏆 Score: {self.total_score}")
        self.games_label.config(text=f"Games: {self.games_played}")
        self.entry.config(state="disabled")
        self.submit_btn.config(state="disabled", bg=COLORS["muted"])
        self._add_history(guess, "✔")
        self._update_progress()
        self.status.config(text="You won! Click 'New Game' to play again.")
        messagebox.showinfo("🎉 You Win!",
                            f"Secret number tha: {self.secret}\n"
                            f"Attempts used: {used}/{self.max_attempts}\n"
                            f"Points earned: +{earned}")

    def _lose(self):
        self.game_over = True
        self.games_played += 1
        self.info_label.config(
            text=f"💀 GAME OVER!\nSecret number tha: {self.secret}",
            fg=COLORS["danger"]
        )
        self.hint_label.config(text="Better luck next time!", fg=COLORS["danger"])
        self.entry.config(state="disabled")
        self.submit_btn.config(state="disabled", bg=COLORS["muted"])
        self._add_history(self.secret, "✖")
        self._update_progress()
        self.games_label.config(text=f"Games: {self.games_played}")
        self.status.config(text="Game over. Click 'New Game' to try again.")
        messagebox.showwarning("💀 Game Over",
                               f"Secret number tha: {self.secret}\n"
                               f"Aapke attempts khatam ho gaye!")

    def _flash_message(self, msg, color):
        self.hint_label.config(text=msg, fg=color)
        self.root.after(1500, lambda: self.hint_label.config(text="", fg=COLORS["warning"]))


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    root = tk.Tk()
    # Try to set a nicer icon (optional, ignore if fails)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = NumberGuessingGame(root)
    root.mainloop()