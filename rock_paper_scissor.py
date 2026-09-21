"""
============================================================
  ROCK PAPER SCISSORS - Professional Edition
  Author: AI Assistant
  Language: Python 3 (Tkinter - built-in)
  Run: python rock_paper_scissors.py
============================================================
"""

import tkinter as tk
from tkinter import messagebox
import random

# ---------------- CONFIGURATION ----------------
COLORS = {
    "bg":        "#0f172a",
    "panel":     "#1e293b",
    "panel2":    "#334155",
    "fg":        "#e2e8f0",
    "accent":    "#38bdf8",
    "success":   "#22c55e",
    "danger":    "#ef4444",
    "warning":   "#f59e0b",
    "muted":     "#94a3b8",
    "rock":      "#f97316",
    "paper":     "#3b82f6",
    "scissors":  "#a855f7",
}

CHOICES = {
    "Rock":     {"emoji": "🪨", "color": COLORS["rock"]},
    "Paper":    {"emoji": "📄", "color": COLORS["paper"]},
    "Scissors": {"emoji": "✂️", "color": COLORS["scissors"]},
}


class RockPaperScissors:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Rock Paper Scissors")
        self.root.geometry("1000x700")
        self.root.minsize(950, 650)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # Center the window
        self.root.update_idletasks()
        w, h = 1000, 700
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Game state
        self.player_score = 0
        self.computer_score = 0
        self.draws = 0
        self.total_games = 0
        self.history = []

        self._build_ui()
        self._reset_game()

        # Keyboard bindings
        self.root.bind("<r>", lambda e: self._play("Rock"))
        self.root.bind("<R>", lambda e: self._play("Rock"))
        self.root.bind("<p>", lambda e: self._play("Paper"))
        self.root.bind("<P>", lambda e: self._play("Paper"))
        self.root.bind("<s>", lambda e: self._play("Scissors"))
        self.root.bind("<S>", lambda e: self._play("Scissors"))

    # ---------------- UI BUILD ----------------
    def _build_ui(self):
        # Title
        title = tk.Label(
            self.root, text="🎮 ROCK PAPER SCISSORS",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        )
        title.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root, text="Choose wisely! Best of luck! 🍀",
            font=("Segoe UI", 11),
            bg=COLORS["bg"], fg=COLORS["muted"]
        )
        subtitle.pack()

        # Main container
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # LEFT PANEL - Game Controls
        left = tk.Frame(main, bg=COLORS["panel"], highlightbackground=COLORS["panel2"], highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Score display
        score_frame = tk.Frame(left, bg=COLORS["panel"])
        score_frame.pack(pady=20, fill="x", padx=20)

        # Player score
        player_frame = tk.Frame(score_frame, bg=COLORS["panel2"], bd=0, highlightbackground=COLORS["accent"], highlightthickness=2)
        player_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(player_frame, text="👤 YOU", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel2"], fg=COLORS["accent"]).pack(pady=(10, 0))
        self.player_score_label = tk.Label(player_frame, text="0",
                                           font=("Segoe UI", 32, "bold"),
                                           bg=COLORS["panel2"], fg=COLORS["success"])
        self.player_score_label.pack(pady=(0, 10))

        # VS
        tk.Label(score_frame, text="VS", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["panel"], fg=COLORS["warning"]).pack(side="left", padx=10)

        # Computer score
        comp_frame = tk.Frame(score_frame, bg=COLORS["panel2"], bd=0, highlightbackground=COLORS["danger"], highlightthickness=2)
        comp_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(comp_frame, text="🤖 COMPUTER", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel2"], fg=COLORS["danger"]).pack(pady=(10, 0))
        self.comp_score_label = tk.Label(comp_frame, text="0",
                                         font=("Segoe UI", 32, "bold"),
                                         bg=COLORS["panel2"], fg=COLORS["danger"])
        self.comp_score_label.pack(pady=(0, 10))

        # Result display area
        self.result_frame = tk.Frame(left, bg=COLORS["panel2"], height=120,
                                     highlightbackground=COLORS["panel"], highlightthickness=2)
        self.result_frame.pack(fill="x", padx=20, pady=10)
        self.result_frame.pack_propagate(False)

        self.result_label = tk.Label(self.result_frame, text="Make your choice!",
                                     font=("Segoe UI", 16, "bold"),
                                     bg=COLORS["panel2"], fg=COLORS["fg"])
        self.result_label.pack(expand=True)

        # Choice buttons
        btn_frame = tk.Frame(left, bg=COLORS["panel"])
        btn_frame.pack(pady=20)

        self.rock_btn = tk.Button(
            btn_frame, text="🪨\nROCK", font=("Segoe UI", 14, "bold"),
            bg=COLORS["rock"], fg="white", activebackground="#ea580c",
            relief="flat", padx=25, pady=15, cursor="hand2",
            command=lambda: self._play("Rock")
        )
        self.rock_btn.pack(side="left", padx=10)

        self.paper_btn = tk.Button(
            btn_frame, text="📄\nPAPER", font=("Segoe UI", 14, "bold"),
            bg=COLORS["paper"], fg="white", activebackground="#2563eb",
            relief="flat", padx=25, pady=15, cursor="hand2",
            command=lambda: self._play("Paper")
        )
        self.paper_btn.pack(side="left", padx=10)

        self.scissors_btn = tk.Button(
            btn_frame, text="✂️\nSCISSORS", font=("Segoe UI", 14, "bold"),
            bg=COLORS["scissors"], fg="white", activebackground="#9333ea",
            relief="flat", padx=25, pady=15, cursor="hand2",
            command=lambda: self._play("Scissors")
        )
        self.scissors_btn.pack(side="left", padx=10)

        # Reset button
        self.reset_btn = tk.Button(
            left, text="🔄 Reset Game", font=("Segoe UI", 12, "bold"),
            bg=COLORS["panel2"], fg=COLORS["fg"], activebackground=COLORS["accent"],
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._reset_game
        )
        self.reset_btn.pack(pady=10)

        # RIGHT PANEL - Statistics & History
        right = tk.Frame(main, bg=COLORS["panel"], highlightbackground=COLORS["panel2"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Statistics
        tk.Label(right, text="📊 Statistics", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(15, 10))

        stats_frame = tk.Frame(right, bg=COLORS["panel2"])
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.stats_labels = {}
        stats_data = [
            ("total", "Total Games:", "0"),
            ("wins", "Wins:", "0"),
            ("losses", "Losses:", "0"),
            ("draws", "Draws:", "0"),
            ("rate", "Win Rate:", "0%"),
        ]

        for key, label_text, value in stats_data:
            row = tk.Frame(stats_frame, bg=COLORS["panel2"])
            row.pack(fill="x", padx=10, pady=5)
            tk.Label(row, text=label_text, font=("Segoe UI", 11),
                     bg=COLORS["panel2"], fg=COLORS["fg"], anchor="w").pack(side="left")
            lbl = tk.Label(row, text=value, font=("Segoe UI", 11, "bold"),
                           bg=COLORS["panel2"], fg=COLORS["success"], anchor="e")
            lbl.pack(side="right")
            self.stats_labels[key] = lbl

        # History
        tk.Label(right, text="📜 Recent History", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(10, 5))

        history_frame = tk.Frame(right, bg=COLORS["panel2"])
        history_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.history_list = tk.Listbox(
            history_frame, font=("Consolas", 10),
            bg=COLORS["panel2"], fg=COLORS["fg"],
            selectbackground=COLORS["accent"],
            relief="flat", bd=0, highlightthickness=0
        )
        scrollbar = tk.Scrollbar(history_frame, command=self.history_list.yview)
        self.history_list.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.history_list.pack(side="left", fill="both", expand=True)

        # Status bar
        self.status = tk.Label(self.root, text="Ready to play! Press R, P, or S key, or click a button.",
                               font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["muted"],
                               anchor="w", padx=20)
        self.status.pack(side="bottom", fill="x", pady=5)

    # ---------------- GAME LOGIC ----------------
    def _play(self, player_choice):
        computer_choice = random.choice(list(CHOICES.keys()))
        result = self._determine_winner(player_choice, computer_choice)

        # Update scores
        self.total_games += 1
        if result == "win":
            self.player_score += 1
            result_text = f"🎉 YOU WIN!"
            result_color = COLORS["success"]
        elif result == "lose":
            self.computer_score += 1
            result_text = f"💀 YOU LOSE!"
            result_color = COLORS["danger"]
        else:
            self.draws += 1
            result_text = f"🤝 DRAW!"
            result_color = COLORS["warning"]

        # Update UI
        self.player_score_label.config(text=str(self.player_score))
        self.comp_score_label.config(text=str(self.computer_score))

        # Show result with animation
        self.result_label.config(
            text=f"{result_text}\n\n"
                 f"You: {CHOICES[player_choice]['emoji']} {player_choice}\n"
                 f"Computer: {CHOICES[computer_choice]['emoji']} {computer_choice}",
            fg=result_color
        )

        # Add to history
        history_entry = f"#{self.total_games:02d} | {player_choice} vs {computer_choice} | {result.upper()}"
        self.history.insert(0, history_entry)
        if len(self.history) > 10:
            self.history.pop()
        self._update_history_display()

        # Update statistics
        self._update_stats()

        self.status.config(text=f"Round {self.total_games}: {result_text}")

    def _determine_winner(self, player, computer):
        if player == computer:
            return "draw"
        wins = {
            "Rock": "Scissors",
            "Paper": "Rock",
            "Scissors": "Paper"
        }
        if wins[player] == computer:
            return "win"
        return "lose"

    def _update_history_display(self):
        self.history_list.delete(0, tk.END)
        for entry in self.history:
            self.history_list.insert(tk.END, entry)

    def _update_stats(self):
        self.stats_labels["total"].config(text=str(self.total_games))
        self.stats_labels["wins"].config(text=str(self.player_score))
        self.stats_labels["losses"].config(text=str(self.computer_score))
        self.stats_labels["draws"].config(text=str(self.draws))
        win_rate = (self.player_score / self.total_games * 100) if self.total_games > 0 else 0
        self.stats_labels["rate"].config(text=f"{win_rate:.1f}%")

    def _reset_game(self):
        self.player_score = 0
        self.computer_score = 0
        self.draws = 0
        self.total_games = 0
        self.history = []

        self.player_score_label.config(text="0")
        self.comp_score_label.config(text="0")
        self.result_label.config(text="Make your choice!", fg=COLORS["fg"])
        self.history_list.delete(0, tk.END)
        self._update_stats()

        self.status.config(text="Game reset! Ready to play!")
        messagebox.showinfo("🔄 Reset", "Game has been reset. Good luck!")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = RockPaperScissors(root)
    root.mainloop()