import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import json
import os

class WordPuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Advanced Word Puzzle Master 🔥")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
        # Word database
        self.words = {
            "easy": ["python", "coding", "game", "play", "word", "puzzle", "brain", "think",
                    "learn", "study", "read", "write", "code", "test", "pass", "fail",
                    "win", "lose", "draw", "move", "jump", "run", "walk", "talk",
                    "fast", "slow", "high", "low", "big", "small", "hot", "cold"],
            "medium": ["algorithm", "function", "variable", "database", "network", "server",
                      "browser", "program", "compile", "debug", "array", "string", "class",
                      "object", "method", "inherit", "polymorph", "abstract", "encapsulate",
                      "recursion", "iteration", "loop", "condition", "exception", "module"],
            "hard": ["entrepreneur", "bureaucracy", "conscientious", "idiosyncrasy",
                    "paraphernalia", "serendipity", "quintessential", "anachronistic",
                    "obfuscation", "perspicacious", "surreptitious", "vicissitude",
                    "cacophony", "ephemeral", "mellifluous", "pusillanimous",
                    "magnanimous", "loquacious", "gregarious", "perfunctory"],
            "expert": ["antidisestablishmentarianism", "pneumonoultramicroscopicsilicovolcanoconiosis",
                      "hippopotomonstrosesquippedaliophobia", "supercalifragilisticexpialidocious",
                      "floccinaucinihilipilification", "honorificabilitudinitatibus",
                      "pseudopseudohypoparathyroidism", "thyroparathyroidectomized"]
        }
        
        self.hints = {
            "python": "Popular programming language named after a comedy group",
            "algorithm": "Step-by-step procedure for calculations",
            "entrepreneur": "Someone who starts and runs a business",
            "serendipity": "Happy accident or fortunate discovery",
            "quintessential": "Representing the perfect example of something",
            "perspicacious": "Having keen mental perception and understanding",
            "bureaucracy": "System of government with many departments",
            "conscientious": "Wishing to do what is right",
            "idiosyncrasy": "Peculiar individual characteristic",
            "paraphernalia": "Miscellaneous articles or equipment"
        }
        
        # Game state
        self.score = 0
        self.lives = 3
        self.current_word = ""
        self.jumbled_word = ""
        self.difficulty = "medium"
        self.attempts = 0
        self.max_attempts = 6
        self.hints_used = 0
        self.max_hints = 3
        self.start_time = None
        self.high_scores = self.load_high_scores()
        self.words_solved = 0
        
        self.create_main_menu()
    
    def load_high_scores(self):
        try:
            if os.path.exists("high_scores.json"):
                with open("high_scores.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {"easy": 0, "medium": 0, "hard": 0, "expert": 0}
    
    def save_high_scores(self):
        try:
            with open("high_scores.json", "w") as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_frame = tk.Frame(self.root, bg="#16213e", height=100)
        title_frame.pack(fill=tk.X, pady=20)
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, text="🔥 WORD PUZZLE MASTER 🔥", 
                        font=("Arial", 32, "bold"), fg="#e94560", bg="#16213e")
        title.pack(pady=20)
        
        # Menu buttons
        menu_frame = tk.Frame(self.root, bg="#1a1a2e")
        menu_frame.pack(pady=30)
        
        buttons = [
            ("🎮 Play Game", self.select_difficulty),
            ("🏆 High Scores", self.show_high_scores),
            ("📖 How to Play", self.show_instructions),
            ("🚪 Exit", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, font=("Arial", 16, "bold"),
                          bg="#0f3460", fg="white", width=20, height=2,
                          command=command, cursor="hand2",
                          activebackground="#e94560", activeforeground="white",
                          relief=tk.FLAT, bd=0)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e94560"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#0f3460"))
    
    def select_difficulty(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title = tk.Label(self.root, text="Select Difficulty", 
                        font=("Arial", 28, "bold"), fg="#e94560", bg="#1a1a2e")
        title.pack(pady=30)
        
        diff_frame = tk.Frame(self.root, bg="#1a1a2e")
        diff_frame.pack(pady=20)
        
        difficulties = [
            ("Easy", "easy", "#4ecca3"),
            ("Medium", "medium", "#f9ed69"),
            ("Hard", "hard", "#f38181"),
            ("Expert", "expert", "#aa00ff")
        ]
        
        for text, diff, color in difficulties:
            btn = tk.Button(diff_frame, text=f"{text}\n(High Score: {self.high_scores[diff]})",
                          font=("Arial", 14, "bold"), bg=color, fg="black",
                          width=15, height=3, command=lambda d=diff: self.start_game(d),
                          cursor="hand2", relief=tk.FLAT, bd=0)
            btn.pack(pady=10)
        
        back_btn = tk.Button(self.root, text="← Back", font=("Arial", 12),
                            bg="#0f3460", fg="white", command=self.create_main_menu,
                            relief=tk.FLAT, cursor="hand2")
        back_btn.pack(pady=20)
    
    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.score = 0
        self.lives = 3
        self.hints_used = 0
        self.attempts = 0
        self.words_solved = 0
        self.start_time = time.time()
        
        self.create_game_ui()
        self.next_word()
    
    def create_game_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Top bar
        top_frame = tk.Frame(self.root, bg="#16213e", height=80)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        stats_frame = tk.Frame(top_frame, bg="#16213e")
        stats_frame.pack(pady=15, padx=20, fill=tk.X)
        
        self.score_label = tk.Label(stats_frame, text=f"Score: {self.score}",
                                   font=("Arial", 16, "bold"), fg="#4ecca3", bg="#16213e")
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.lives_label = tk.Label(stats_frame, text=f"Lives: {'❤️' * self.lives}",
                                   font=("Arial", 16), fg="#e94560", bg="#16213e")
        self.lives_label.pack(side=tk.LEFT, padx=10)
        
        self.hints_label = tk.Label(stats_frame, text=f"Hints: {self.max_hints - self.hints_used}",
                                   font=("Arial", 16), fg="#f9ed69", bg="#16213e")
        self.hints_label.pack(side=tk.LEFT, padx=10)
        
        self.diff_label = tk.Label(stats_frame, text=f"Difficulty: {self.difficulty.upper()}",
                                  font=("Arial", 14), fg="white", bg="#16213e")
        self.diff_label.pack(side=tk.RIGHT, padx=10)
        
        # Game area
        game_frame = tk.Frame(self.root, bg="#1a1a2e")
        game_frame.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)
        
        self.word_label = tk.Label(game_frame, text="", font=("Arial", 48, "bold"),
                                  fg="#e94560", bg="#1a1a2e")
        self.word_label.pack(pady=30)
        
        self.hint_label = tk.Label(game_frame, text="", font=("Arial", 12, "italic"),
                                  fg="#f9ed69", bg="#1a1a2e", wraplength=600)
        self.hint_label.pack(pady=10)
        
        self.entry = tk.Entry(game_frame, font=("Arial", 20), justify=tk.CENTER,
                             bg="#0f3460", fg="white", insertbackground="white",
                             relief=tk.FLAT, bd=5)
        self.entry.pack(pady=20, ipady=10, ipadx=50)
        self.entry.focus()
        self.entry.bind("<Return>", lambda e: self.check_answer())
        
        # Buttons
        btn_frame = tk.Frame(game_frame, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        submit_btn = tk.Button(btn_frame, text="✓ Submit", font=("Arial", 14, "bold"),
                              bg="#4ecca3", fg="black", width=12, height=2,
                              command=self.check_answer, cursor="hand2",
                              relief=tk.FLAT, bd=0)
        submit_btn.pack(side=tk.LEFT, padx=10)
        
        hint_btn = tk.Button(btn_frame, text="💡 Hint", font=("Arial", 14, "bold"),
                            bg="#f9ed69", fg="black", width=12, height=2,
                            command=self.use_hint, cursor="hand2",
                            relief=tk.FLAT, bd=0)
        hint_btn.pack(side=tk.LEFT, padx=10)
        
        skip_btn = tk.Button(btn_frame, text="→ Skip", font=("Arial", 14, "bold"),
                            bg="#f38181", fg="black", width=12, height=2,
                            command=self.next_word, cursor="hand2",
                            relief=tk.FLAT, bd=0)
        skip_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(btn_frame, text="✕ Quit", font=("Arial", 14, "bold"),
                            bg="#aa00ff", fg="white", width=12, height=2,
                            command=self.end_game, cursor="hand2",
                            relief=tk.FLAT, bd=0)
        quit_btn.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(game_frame, text="", font=("Arial", 14),
                                    fg="white", bg="#1a1a2e")
        self.status_label.pack(pady=10)
    
    def next_word(self):
        self.current_word = random.choice(self.words[self.difficulty])
        self.jumbled_word = self.jumble_word(self.current_word)
        self.word_label.config(text=self.jumbled_word)
        self.hint_label.config(text="")
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.attempts = 0
        self.status_label.config(text=f"Attempt {self.attempts + 1}/{self.max_attempts}")
    
    def jumble_word(self, word):
        if len(word) <= 3:
            return ''.join(random.sample(word, len(word)))
        word_list = list(word)
        random.shuffle(word_list)
        jumbled = ''.join(word_list)
        if jumbled == word:
            return self.jumble_word(word)
        return jumbled
    
    def check_answer(self):
        guess = self.entry.get().strip().lower()
        
        if not guess:
            return
        
        self.attempts += 1
        
        if guess == self.current_word:
            points = self.calculate_points()
            self.score += points
            self.words_solved += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.status_label.config(text=f"✓ Correct! +{points} points", fg="#4ecca3")
            self.root.after(1500, self.next_word)
        else:
            if self.attempts >= self.max_attempts:
                self.lives -= 1
                self.lives_label.config(text=f"Lives: {'❤️' * self.lives}")
                self.status_label.config(text=f"✗ Wrong! The word was: {self.current_word}", fg="#e94560")
                
                if self.lives <= 0:
                    self.root.after(1500, self.end_game)
                else:
                    self.root.after(2000, self.next_word)
            else:
                remaining = self.max_attempts - self.attempts
                self.status_label.config(text=f"✗ Wrong! {remaining} attempts left", fg="#f9ed69")
        
        self.entry.delete(0, tk.END)
    
    def calculate_points(self):
        base_points = {"easy": 10, "medium": 20, "hard": 30, "expert": 50}
        points = base_points[self.difficulty]
        
        if self.attempts == 1:
            points *= 2
        elif self.attempts <= 3:
            points = int(points * 1.5)
        
        if self.hints_used > 0:
            points = max(5, points - (self.hints_used * 5))
        
        return points
    
    def use_hint(self):
        if self.hints_used >= self.max_hints:
            self.status_label.config(text="No hints left!", fg="#e94560")
            return
        
        if self.current_word in self.hints:
            self.hint_label.config(text=f"Hint: {self.hints[self.current_word]}")
        else:
            self.hint_label.config(text=f"Hint: Word has {len(self.current_word)} letters, starts with '{self.current_word[0]}'")
        
        self.hints_used += 1
        self.hints_label.config(text=f"Hints: {self.max_hints - self.hints_used}")
    
    def end_game(self):
        elapsed_time = int(time.time() - self.start_time)
        
        if self.score > self.high_scores[self.difficulty]:
            self.high_scores[self.difficulty] = self.score
            self.save_high_scores()
            messagebox.showinfo("🏆 New High Score!", 
                              f"Congratulations!\nNew high score for {self.difficulty.upper()}: {self.score}")
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title = tk.Label(self.root, text="Game Over", font=("Arial", 36, "bold"),
                        fg="#e94560", bg="#1a1a2e")
        title.pack(pady=30)
        
        stats_text = f"""
        Final Score: {self.score}
        Words Solved: {self.words_solved}
        Difficulty: {self.difficulty.upper()}
        Time: {elapsed_time} seconds
        High Score: {self.high_scores[self.difficulty]}
        """
        
        stats = tk.Label(self.root, text=stats_text, font=("Arial", 16),
                        fg="white", bg="#1a1a2e", justify=tk.LEFT)
        stats.pack(pady=20)
        
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=30)
        
        play_again_btn = tk.Button(btn_frame, text="🔄 Play Again", font=("Arial", 14, "bold"),
                                  bg="#4ecca3", fg="black", width=15, height=2,
                                  command=self.select_difficulty, cursor="hand2",
                                  relief=tk.FLAT, bd=0)
        play_again_btn.pack(side=tk.LEFT, padx=10)
        
        menu_btn = tk.Button(btn_frame, text="🏠 Main Menu", font=("Arial", 14, "bold"),
                            bg="#0f3460", fg="white", width=15, height=2,
                            command=self.create_main_menu, cursor="hand2",
                            relief=tk.FLAT, bd=0)
        menu_btn.pack(side=tk.LEFT, padx=10)
    
    def show_high_scores(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title = tk.Label(self.root, text="🏆 High Scores", font=("Arial", 28, "bold"),
                        fg="#e94560", bg="#1a1a2e")
        title.pack(pady=30)
        
        scores_frame = tk.Frame(self.root, bg="#1a1a2e")
        scores_frame.pack(pady=20)
        
        for diff, score in self.high_scores.items():
            label = tk.Label(scores_frame, text=f"{diff.upper():10} : {score}",
                           font=("Arial", 16, "bold"), fg="white", bg="#1a1a2e")
            label.pack(pady=10)
        
        back_btn = tk.Button(self.root, text="← Back", font=("Arial", 12),
                            bg="#0f3460", fg="white", command=self.create_main_menu,
                            relief=tk.FLAT, cursor="hand2")
        back_btn.pack(pady=30)
    
    def show_instructions(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title = tk.Label(self.root, text="📖 How to Play", font=("Arial", 28, "bold"),
                        fg="#e94560", bg="#1a1a2e")
        title.pack(pady=20)
        
        instructions = """
        🎮 GAME RULES:
        
        • Unscramble the jumbled word
        • You have 6 attempts per word
        • You have 3 lives total
        • Use hints wisely (max 3 per game)
        • Faster solves = more points
        • First attempt = 2x points bonus
        
        🎯 SCORING:
        • Easy: 10 points base
        • Medium: 20 points base
        • Hard: 30 points base
        • Expert: 50 points base
        
        💡 TIPS:
        • Look for common letter patterns
        • Use hints when stuck
        • Skip difficult words
        • Practice makes perfect!
        """
        
        text = tk.Label(self.root, text=instructions, font=("Arial", 12),
                       fg="white", bg="#1a1a2e", justify=tk.LEFT)
        text.pack(pady=20)
        
        back_btn = tk.Button(self.root, text="← Back", font=("Arial", 12),
                            bg="#0f3460", fg="white", command=self.create_main_menu,
                            relief=tk.FLAT, cursor="hand2")
        back_btn.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    game = WordPuzzleGame(root)
    root.mainloop()