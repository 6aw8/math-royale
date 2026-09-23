import random
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import db_helper

#also plz remember to actually import game assets and icons this time lmao
#things to fix are timer logic, question generation and few other fixes along with smoothening of UI

db_helper.init_db()
current_user = "Player"
user_high_score = 0
selected_difficulty = "Easy"
score = 0
lives = 2
timer_seconds = 12
time_left = 12
num1 = 0
num2 = 0
op = "+"
correct_ans = 0
timer_job = None

def load_leaderboard():
    items = leaderboard_tree.get_children()
    if items:
        leaderboard_tree.delete(*items)
    try:
        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, high_score, games_played FROM players ORDER BY high_score DESC LIMIT 10")
        players = cursor.fetchall()
        conn.close()
        ranks = ["🥇 1st", "🥈 2nd", "🥉 3rd"]
        for idx, (user, p_score, games) in enumerate(players):
            rank = ranks[idx] if idx < 3 else f"#{idx + 1}"
            leaderboard_tree.insert("", "end", values=(rank, user, f"{p_score} pts", games))
    except Exception as e:
        print("Leaderboard fetch error:", e)

def set_difficulty(level):
    global selected_difficulty
    selected_difficulty = level
    btn_easy.configure(bootstyle="info" if level == "Easy" else "outline-info")
    btn_medium.configure(bootstyle="warning" if level == "Medium" else "outline-warning")
    btn_hard.configure(bootstyle="danger" if level == "Hard" else "outline-danger")

def handle_login():
    global current_user, user_high_score
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    if not username or not password:
        lbl_auth_status.configure(text="Please fill in all fields.", bootstyle="danger")
        return
    ok, high = db_helper.login_player(username, password)
    if ok:
        current_user = username
        user_high_score = high
        lbl_welcome.configure(text=f"Welcome back, {current_user}!")
        lbl_user_score.configure(text=f"High Score: {user_high_score} pts")
        auth_frame.pack_forget()
        lobby_frame.pack(fill=BOTH, expand=True)
        load_leaderboard()
    else:
        lbl_auth_status.configure(text="Invalid username or password.", bootstyle="danger")

def handle_register():
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    if not username or not password:
        lbl_auth_status.configure(text="Please fill in all fields.", bootstyle="danger")
        return
    ok, msg = db_helper.register_player(username, password)
    if ok:
        lbl_auth_status.configure(text="Account created! You can now log in.", bootstyle="warning")
    else:
        lbl_auth_status.configure(text=msg, bootstyle="danger")


def generate_question():
    global num1, num2, op, correct_ans, timer_seconds, time_left, timer_job
    if timer_job:
        root.after_cancel(timer_job)
    if selected_difficulty == "Easy":
        op = random.choice(["+", "-", "*", "/"])
        if op == "/":
            num2 = random.randint(2, 10)
            correct_ans = random.randint(1, 10)
            num1 = num2 * correct_ans
        elif op == "*":
            num1 = random.randint(2, 10)
            num2 = random.randint(2, 10)
            correct_ans = num1 * num2
        else:
            num1 = random.randint(5, 30)
            num2 = random.randint(5, 30)
            if op == "-" and num2 > num1:
                num1, num2 = num2, num1
            correct_ans = num1 + num2 if op == "+" else num1 - num2
        timer_seconds = 12
    elif selected_difficulty == "Medium":
        op = random.choice(["+", "-", "*", "/"])
        if op == "/":
            num2 = random.randint(3, 12)
            correct_ans = random.randint(5, 15)
            num1 = num2 * correct_ans
        elif op == "*":
            num1 = random.randint(3, 15)
            num2 = random.randint(3, 12)
            correct_ans = num1 * num2
        else:
            num1 = random.randint(20, 80)
            num2 = random.randint(20, 80)
            if op == "-" and num2 > num1:
                num1, num2 = num2, num1
            correct_ans = num1 + num2 if op == "+" else num1 - num2
        timer_seconds = 10
    else:  # Hard
        op = random.choice(["+", "-", "*", "/"])
        if op == "/":
            num2 = random.randint(4, 20)
            correct_ans = random.randint(8, 25)
            num1 = num2 * correct_ans
        elif op == "*":
            num1 = random.randint(6, 20)
            num2 = random.randint(4, 15)
            correct_ans = num1 * num2
        else:
            num1 = random.randint(50, 150)
            num2 = random.randint(50, 150)
            if op == "-" and num2 > num1:
                num1, num2 = num2, num1
            correct_ans = num1 + num2 if op == "+" else num1 - num2
        timer_seconds = 8
    display_op = op
    if op == "*":
        display_op = "×"
    elif op == "/":
        display_op = "÷"
    time_left = timer_seconds
    lbl_block_num1.configure(text=str(num1))
    lbl_block_op.configure(text=display_op)
    lbl_block_num2.configure(text=str(num2))
    entry_ans.delete(0, 'end')
    entry_ans.focus()
    run_timer()

def run_timer():  #time logic gotta fix this bro
    global time_left, timer_job, lives
    lbl_timer.configure(text=f"⏱️ {time_left}s")
    if time_left <= 3:
        lbl_timer.configure(bootstyle="danger")
    else:
        lbl_timer.configure(bootstyle="info")

    if time_left > 0:
        time_left -= 1
        timer_job = root.after(1000, run_timer)
    else:
        lives -= 1
        lbl_lives.configure(text=f"❤️ Lives: {lives}")
        if lives <= 0:
            end_game()
        else:
            generate_question()

def check_answer(event=None):
    global score, lives
    user_input = entry_ans.get().strip()
    if user_input.lstrip('-').isdigit() and int(user_input) == correct_ans:
        speed_bonus = time_left * 15
        score += (100 + speed_bonus)
        lbl_score.configure(text=f"🏆 Score: {score}")
        generate_question()
    else:
        lives -= 1
        lbl_lives.configure(text=f"❤️ Lives: {lives}")
        if lives <= 0:
            end_game()
        else:
            generate_question()

def give_up():
    if messagebox.askyesno("Give Up", "Forfeit this match and record your score?"):
        end_game()

def start_game():
    global score, lives
    score = 0
    lives = 2
    lbl_score.configure(text="🏆 Score: 0")
    lbl_lives.configure(text="❤️ Lives: 2")
    lobby_frame.pack_forget()
    game_frame.pack(fill=BOTH, expand=True)
    generate_question()

def end_game():
    global user_high_score, timer_job
    if timer_job:
        root.after_cancel(timer_job)
    user_high_score = db_helper.save_score(current_user, score)
    messagebox.showinfo("Game Over", f"Final Score: {score}\nPersonal Best: {user_high_score}")
    game_frame.pack_forget()
    lobby_frame.pack(fill=BOTH, expand=True)
    lbl_user_score.configure(text=f"High Score: {user_high_score} pts")
    load_leaderboard()

def logout():
    global timer_job
    if timer_job:
        root.after_cancel(timer_job)
    lobby_frame.pack_forget()
    auth_frame.pack(fill=BOTH, expand=True)
    entry_user.delete(0, 'end')
    entry_pass.delete(0, 'end')
    lbl_auth_status.configure(text="")


root = tb.Window(title="Math Royale", themename="darkly", size=(1050, 680))
root.resizable(False, False)
FONT_BRAND = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_SUBHEADER = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MATH = ("Consolas", 32, "bold")
style = tb.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
auth_frame = tb.Frame(root)
auth_frame.pack(fill=BOTH, expand=True)
auth_card = tb.Labelframe(auth_frame, padding=35, bootstyle="info")
auth_card.place(relx=0.5, rely=0.5, anchor=CENTER, width=420, height=480)
lbl_brand = tb.Label(auth_card, text="Math Royale", font=FONT_BRAND, bootstyle="info", anchor=CENTER)
lbl_brand.pack(fill=X)
lbl_subtitle = tb.Label(auth_card, text="Sign in or create an account to play", font=FONT_SUBTITLE, bootstyle="warning", anchor=CENTER)
lbl_subtitle.pack(fill=X, pady=(2, 25))
lbl_user = tb.Label(auth_card, text="Username", font=FONT_SUBHEADER, bootstyle="light")
lbl_user.pack(anchor=W, pady=(0, 4))

entry_user = tb.Entry(auth_card, font=FONT_BODY, bootstyle="info")
entry_user.pack(fill=X, pady=(0, 16))

lbl_pass = tb.Label(auth_card, text="Password", font=FONT_SUBHEADER, bootstyle="light")
lbl_pass.pack(anchor=W, pady=(0, 4))

entry_pass = tb.Entry(auth_card, font=FONT_BODY, show="•", bootstyle="info")
entry_pass.pack(fill=X, pady=(0, 8))


lbl_auth_status = tb.Label(auth_card, text="", font=FONT_BODY, anchor=CENTER)
lbl_auth_status.pack(fill=X, pady=(0, 12))


btn_login = tb.Button(auth_card, text="Log In", bootstyle="info", command=handle_login)
btn_login.pack(fill=X, pady=(0, 8), ipady=5)
btn_register = tb.Button(auth_card, text="Create Account", bootstyle="outline-warning", command=handle_register)
btn_register.pack(fill=X, ipady=4)
lobby_frame = tb.Frame(root, padding=30)
header_frame = tb.Frame(lobby_frame)
header_frame.pack(fill=X, pady=(0, 20))
lbl_welcome = tb.Label(header_frame, text="Welcome!", font=FONT_HEADER, bootstyle="info")
lbl_welcome.pack(side=LEFT)
tb.Button(header_frame, text="Log Out", bootstyle="outline-danger", command=logout).pack(side=RIGHT)
content_split = tb.Frame(lobby_frame)
content_split.pack(fill=BOTH, expand=True)
content_split.columnconfigure(0, weight=1, uniform="group1")
content_split.columnconfigure(1, weight=1, uniform="group1")
content_split.rowconfigure(0, weight=1)
left_side = tb.LabelFrame(content_split, text=" Game Controls ", padding=20, bootstyle="info")
left_side.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
lbl_user_score = tb.Label(left_side, text="High Score: 0 pts", font=FONT_SUBHEADER, bootstyle="warning")
lbl_user_score.pack(anchor=W, pady=(0, 25))
tb.Label(left_side, text="Select Difficulty:", font=FONT_SUBHEADER, bootstyle="light").pack(anchor=W, pady=(0, 10))
btn_easy = tb.Button(left_side, text="Easy (12s)", bootstyle="info", command=lambda: set_difficulty("Easy"))
btn_easy.pack(fill=X, pady=8)
btn_medium = tb.Button(left_side, text="Medium (10s)", bootstyle="outline-warning", command=lambda: set_difficulty("Medium"))
btn_medium.pack(fill=X, pady=8)
btn_hard = tb.Button(left_side, text="Hard (8s)", bootstyle="outline-danger", command=lambda: set_difficulty("Hard"))
btn_hard.pack(fill=X, pady=8)
tb.Separator(left_side, bootstyle="info").pack(fill=X, pady=25)
tb.Button(left_side, text="Start Game", bootstyle="info", command=start_game).pack(fill=X, ipady=8)
right_side = tb.LabelFrame(content_split, text="Leaderboard ", padding=15, bootstyle="warning")
right_side.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
columns = ("rank", "username", "high_score", "games_played")
leaderboard_tree = tb.Treeview(right_side, columns=columns, show="headings", bootstyle="dark", height=10)
leaderboard_tree.heading("rank", text="Rank")
leaderboard_tree.heading("username", text="Player")
leaderboard_tree.heading("high_score", text="Score")
leaderboard_tree.heading("games_played", text="Games")
leaderboard_tree.column("rank", width=70, anchor=CENTER)
leaderboard_tree.column("username", width=130, anchor=W)
leaderboard_tree.column("high_score", width=90, anchor=CENTER)
leaderboard_tree.column("games_played", width=60, anchor=CENTER)
leaderboard_tree.pack(fill=BOTH, expand=True, pady=(0, 15))
tb.Button(right_side, text="Refresh Leaderboard", bootstyle="outline-warning", command=load_leaderboard).pack(fill=X)
game_frame = tb.Frame(root, padding=40)
game_container = tb.LabelFrame(game_frame, text=" Live Match ", padding=35, bootstyle="info")
game_container.place(relx=0.5, rely=0.5, anchor=CENTER, width=850, height=520)
hud_frame = tb.Frame(game_container)
hud_frame.pack(fill=X, pady=(0, 30))
lbl_score = tb.Label(hud_frame, text="🏆 Score: 0", font=FONT_HEADER, bootstyle="warning")
lbl_score.pack(side=LEFT)
lbl_lives = tb.Label(hud_frame, text="❤️ Lives: 2", font=FONT_HEADER, bootstyle="danger")
lbl_lives.pack(side=LEFT, padx=40)
tb.Button(hud_frame, text="Give Up", bootstyle="outline-danger", command=give_up).pack(side=LEFT, padx=10)
lbl_timer = tb.Label(hud_frame, text="⏱️ 12s", font=FONT_HEADER, bootstyle="info")
lbl_timer.pack(side=RIGHT)
math_blocks_frame = tb.Frame(game_container)
math_blocks_frame.pack(pady=20)
lbl_block_num1 = tb.Label(math_blocks_frame, text="0", font=FONT_MATH, bootstyle="info-inverse", padding=(20, 12))
lbl_block_num1.pack(side=LEFT, padx=6)
lbl_block_op = tb.Label(math_blocks_frame, text="+", font=FONT_MATH, bootstyle="danger-inverse", padding=(20, 12))
lbl_block_op.pack(side=LEFT, padx=6)
lbl_block_num2 = tb.Label(math_blocks_frame, text="0", font=FONT_MATH, bootstyle="warning-inverse", padding=(20, 12))
lbl_block_num2.pack(side=LEFT, padx=6)
lbl_block_eq = tb.Label(math_blocks_frame, text="=", font=FONT_MATH, bootstyle="secondary-inverse", padding=(20, 12))
lbl_block_eq.pack(side=LEFT, padx=6)
lbl_block_q = tb.Label(math_blocks_frame, text="?", font=FONT_MATH, bootstyle="info-inverse", padding=(20, 12))
lbl_block_q.pack(side=LEFT, padx=6)
input_frame = tb.Frame(game_container)
input_frame.pack(pady=30)
entry_ans = tb.Entry(input_frame, font=("Segoe UI", 20, "bold"), justify=CENTER, width=8, bootstyle="info")
entry_ans.pack(side=LEFT, padx=12)
entry_ans.bind("<Return>", check_answer)
tb.Button(input_frame, text="Submit Answer", bootstyle="info", command=check_answer).pack(side=LEFT, padx=12, ipady=6)

root.mainloop()