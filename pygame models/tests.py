import pygame
import sys
import random
import os

pygame.init()

# ------------------- Sound Effects & Music Playlist ------------------- #
# Placeholder paths for sound effects
sound_effect_paths = {
    "menu_click": "C:/Users/mcmon/Documents/PixelRunner/pygame models/MenuClicks.mp3",
    "jump": "C:/Users/mcmon/Documents/PixelRunner/pygame models/GameJump.mp3",
    "lose": "C:/Users/mcmon/Documents/PixelRunner/pygame models/GameLoss.mp3",
}

# Load sound effects
sound_effects = {}
for key, path in sound_effect_paths.items():
    sound_effects[key] = pygame.mixer.Sound(path)

# Set initial volumes
sound_volumes = {
    "menu_click": 1.0,
    "jump": 0.04,
    "lose": 0.2
}
for key, sound in sound_effects.items():
    sound.set_volume(sound_volumes[key])

# ------------------- Music Management ------------------- #
menu_music_paths = [
    "C:/Users/mcmon/Documents/PixelRunner/pygame models/MenuMusic.mp3",
    "C:/Users/mcmon/Documents/PixelRunner/pygame models/MenuMusic.mp3"
]
game_music_paths = [
    "C:/Users/mcmon/Documents/PixelRunner/pygame models/GameMusic-1.mp3",
    "C:/Users/mcmon/Documents/PixelRunner/pygame models/GameMusic-2.mp3",
    "C:/Users/mcmon/Documents/PixelRunner/pygame models/GameMusic-3.mp3"
]

menu_music_playlist = []
game_music_playlist = []

def play_menu_music():
    global menu_music_playlist
    if not menu_music_playlist:
        menu_music_playlist = menu_music_paths.copy()
        random.shuffle(menu_music_playlist)
    track = menu_music_playlist.pop()
    pygame.mixer.music.load(track)
    pygame.mixer.music.set_volume(0.03)
    pygame.mixer.music.play(-1)

def play_game_music():
    global game_music_playlist
    if not game_music_playlist:
        game_music_playlist = game_music_paths.copy()
        random.shuffle(game_music_playlist)
    track = game_music_playlist.pop()
    pygame.mixer.music.load(track)
    pygame.mixer.music.set_volume(0.08)
    pygame.mixer.music.play()

def check_music():
    if not pygame.mixer.music.get_busy():
        # For simplicity, keep playing game music
        play_game_music()

# Helper function for menu click sound
def play_menu_click():
    sound_effects["menu_click"].play()

# ------------------ Rest of your code ------------------ #
# Replace previous sound effect initializations with the new structure
# and call play_menu_music() at start of menu, play_game_music() at game start

# ---------------- Initial temporary screen ---------------- #
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Pixel Runner")
clock = pygame.time.Clock()

# ---------------- Assets ---------------- #
backgroundImg = pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/pixilart-drawing.png")
female_imgs = [
    pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/femmovewalkanim1-pixilart (3).png").convert_alpha(),
    pygame.image.load("C:/Users//mcmon/Documents/PixelRunner/pygame models/femmovewalkanim2-pixilart (5).png").convert_alpha()
]
male_imgs = [
    pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/malewalkanim1.png").convert_alpha(),
    pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/malewalkanim2.png").convert_alpha()
]
obstacle_img = pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/seat-model-pixilart.png").convert_alpha()
overhead_img = pygame.image.load("C:/Users/mcmon/Documents/PixelRunner/pygame models/brick-over-head-pixilart.png").convert_alpha()

# ---------------- Constants ---------------- #
gravity = 0.6
jump_strength = -9
ground_level_ratio = 0.82
LEADERBOARD_FILE = "leaderboard.txt"

BASE_SPEED = 6
MAX_SPEED = 200
BASE_ACCEL = 0.0025

MAX_SPACING = 1000
MIN_SPACING = 150
OVERHEAD_HEIGHT_OFFSET = 105

# ---------------- Resolution Menu ---------------- #
def resolution_menu():
    info = pygame.display.Info()
    max_width = info.current_w
    max_height = info.current_h

    options = ["720p", "Fullscreen"]
    selected = 0
    font = pygame.font.Font(None, 60)

    while True:
        screen.fill((0,0,0))
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_size()
        title = font.render("Select Resolution", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//8))
        screen.blit(font.render("Use arrow keys to scroll", True, (255,255,255)), (WIDTH//3, HEIGHT//4))
        for i, name in enumerate(options):
            color = (255,255,0) if i == selected else (255,255,255)
            text = font.render(name, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i*80))
        back_text = font.render("ESC = Back", True, (200,200,200))
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    play_menu_click()
                    chosen = options[selected]
                    if chosen == "Fullscreen":
                        return (max_width, max_height), pygame.FULLSCREEN
                    else:
                        return (1280, 720), 0
                elif event.key == pygame.K_ESCAPE:
                    return None

# ---------------- Scaling ---------------- #
def rescale_assets():
    global background, female_imgs_scaled, male_imgs_scaled
    global obstacle_img_scaled, overhead_img_scaled, ground_level

    base_scale = 2.0
    scale = base_scale * (HEIGHT / 720)

    background = pygame.transform.scale(backgroundImg, (WIDTH, HEIGHT))

    female_imgs_scaled = [
        pygame.transform.scale(img,
        (int(img.get_width()*scale), int(img.get_height()*scale)))
        for img in female_imgs
    ]

    male_imgs_scaled = [
        pygame.transform.scale(img,
        (int(img.get_width()*scale), int(img.get_height()*scale)))
        for img in male_imgs
    ]

    obstacle_img_scaled = pygame.transform.scale(
        obstacle_img,
        (int(obstacle_img.get_width()*scale),
         int(obstacle_img.get_height()*scale))
    )

    overhead_img_scaled = pygame.transform.scale(
        overhead_img,
        (int(overhead_img.get_width()*scale),
         int(overhead_img.get_height()*scale))
    )

    ground_level = int(HEIGHT * ground_level_ratio)

# ---------------- Leaderboard ---------------- #
def save_score(username, score):
    scores = {}
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            for line in f:
                try:
                    name, s = line.strip().split(",")
                    s = int(s)
                    if name not in scores or s > scores[name]:
                        scores[name] = s
                except:
                    continue
    if username not in scores or score > scores[username]:
        scores[username] = score
    with open(LEADERBOARD_FILE, "w") as f:
        for name, s in scores.items():
            f.write(f"{name},{s}\n")

def get_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    scores = {}
    with open(LEADERBOARD_FILE, "r") as f:
        for line in f:
            try:
                name, score = line.strip().split(",")
                score = int(score)
                if name not in scores or score > scores[name]:
                    scores[name] = score
            except:
                continue
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

# ----------- Spawn checker ----------- #
def can_spawn(new_x, obstacles, overheads, min_distance=MIN_SPACING):
    for r in obstacles + overheads:
        if abs(r.x - new_x) < min_distance:
            return False
    return True

# ----------- Dynamic min distance based on speed ----------- #
def get_dynamic_min_distance(speed):
    return max(MIN_SPACING, int(MIN_SPACING + (speed - BASE_SPEED) * 2))

# ---------------- Game Function ---------------- #
def run_game(username, player_imgs):
    player_x = 100
    player_y = ground_level - player_imgs[0].get_height()
    velocity_y = 0
    frame = 0
    score = 0
    speed = BASE_SPEED

    obstacles = []
    overheads = []

    global background, WIDTH, HEIGHT
    bg_x1 = 0
    bg_x2 = background.get_width()
    scroll_speed = speed

    font = pygame.font.Font(None, 40)

    def spawn_obstacles():
        for _ in range(20):
            new_x = WIDTH + random.randint(100, 1500)
            if can_spawn(new_x, obstacles, overheads, current_min_distance):
                rect = obstacle_img_scaled.get_rect()
                rect.x = new_x
                rect.y = ground_level - rect.height
                obstacles.append(rect)
                break

    def spawn_overheads():
        for _ in range(20):
            new_x = WIDTH + random.randint(200, 1500)
            if can_spawn(new_x, obstacles, overheads, current_min_distance):
                rect = overhead_img_scaled.get_rect()
                rect.x = new_x
                rect.y = ground_level - player_imgs[0].get_height() - OVERHEAD_HEIGHT_OFFSET
                overheads.append(rect)
                break

    while True:
        check_music()
        current_min_distance = get_dynamic_min_distance(scroll_speed)

        # Scroll background
        bg_x1 -= scroll_speed
        bg_x2 -= scroll_speed
        if bg_x1 <= -background.get_width():
            bg_x1 = bg_x2 + background.get_width()
        if bg_x2 <= -background.get_width():
            bg_x2 = bg_x1 + background.get_width()
        screen.blit(background, (bg_x1, 0))
        screen.blit(background, (bg_x2, 0))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(username, score)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_y >= ground_level - player_imgs[0].get_height():
                    velocity_y = jump_strength
                    sound_effects["jump"].play()
                # Menu click sound for menu navigation
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_1, pygame.K_2, pygame.K_RETURN]:
                    play_menu_click()

        # Player physics
        velocity_y += gravity
        player_y += velocity_y
        if player_y > ground_level - player_imgs[0].get_height():
            player_y = ground_level - player_imgs[0].get_height()
            velocity_y = 0

        # Increase speed gradually
        speed += BASE_ACCEL
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        scroll_speed = speed

        # Player animation
        prev_frame = frame
        frame = (frame + 1) % (len(player_imgs) * 10)
        current_img = player_imgs[frame // 10]
        if frame // 10 != prev_frame // 10:
            score += 1

        # Spawn obstacles and overheads
        if len(obstacles) == 0 or obstacles[-1].x < WIDTH - random.randint(50, 700):
            spawn_obstacles()
        if len(overheads) == 0 or overheads[-1].x < WIDTH - random.randint(50, 700):
            spawn_overheads()

        # Move obstacles
        for r in obstacles:
            r.x -= scroll_speed
        for r in overheads:
            r.x -= scroll_speed

        # Remove off-screen objects
        obstacles = [r for r in obstacles if r.x > -100]
        overheads = [r for r in overheads if r.x > -100]

        # Collision detection
        player_rect = current_img.get_rect(topleft=(player_x, player_y))
        hit_type = None
        for r in obstacles:
            if player_rect.colliderect(r):
                hit_type = "Ground Obstacle"
        for r in overheads:
            if player_rect.colliderect(r):
                hit_type = "Overhead Obstacle"
        if hit_type:
            # Stop background music
            pygame.mixer.music.stop()
            # Play lose sound effect
            sound_effects["lose"].play()
            # Wait until the sound finishes
            while pygame.mixer.get_busy():
                pygame.time.wait(100)
            save_score(username, score)
            display_game_over(score, hit_type)
            return

        # Draw everything
        for r in obstacles:
            screen.blit(obstacle_img_scaled, r)
        for r in overheads:
            screen.blit(overhead_img_scaled, r)
        screen.blit(current_img, (player_x, player_y))
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (20, HEIGHT - 40))

        pygame.display.update()
        clock.tick(60)

# ------------------- Game Over Screen ------------------- #
def display_game_over(score, hit_type):
    # Play the lose sound effect again in game over screen
    sound_effects["lose"].play()
    # Wait until the sound finishes before displaying the screen
    #while pygame.mixer.get_busy():
        #pygame.time.wait(15)
    play_menu_music()
    font = pygame.font.Font(None, 80)
    while True:
        screen.fill((0, 0, 0))
        screen.blit(font.render("Game Over", True, (255, 0, 0)), (WIDTH//3, HEIGHT//4))
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (WIDTH//3, HEIGHT//2))
        screen.blit(font.render(f"You lost by {hit_type}!", True, (255,255,255)), (WIDTH//3, HEIGHT//2 + 80))
        screen.blit(font.render("Press Enter to Restart", True, (0,255,0)), (WIDTH//3, HEIGHT//1.2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# ---------------- Menus ---------------- #
def main_menu():
    font = pygame.font.Font(None, 80)
    while True:
        screen.fill((0,0,0))
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_size()
        screen.blit(font.render("Pixel Runner", True, (0,255,0)), (WIDTH//3, HEIGHT//5))
        screen.blit(font.render("1. Play", True, (255,255,255)), (WIDTH//3, HEIGHT//3))
        screen.blit(font.render("2. Leaderboard", True, (255,255,255)), (WIDTH//3, HEIGHT//2))
        screen.blit(font.render("3. Quit", True, (255,255,255)), (WIDTH//3, HEIGHT//2 + 80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    play_menu_click()
                    return "play"
                if event.key == pygame.K_2:
                    play_menu_click()
                    return "leaderboard"
                if event.key == pygame.K_3:
                    play_menu_click()
                    pygame.quit()
                    sys.exit()

def character_selection_menu():
    font = pygame.font.Font(None, 60)
    selected = 0
    options = ["Female", "Male"]
    while True:
        screen.fill((0,0,0))
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_size()
        screen.blit(font.render("Use arrow keys to choose then hit enter", True, (0,255,0)), (WIDTH//3, HEIGHT//5))
        for i, opt in enumerate(options):
            color = (255,255,0) if i == selected else (255,255,255)
            screen.blit(font.render(f"{i+1}. {opt}", True, color),
                        (WIDTH//3, HEIGHT//3 + i*80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    play_menu_click()
                    return "female" if selected == 0 else "male"

def name_input_menu():
    username = ""
    font = pygame.font.Font(None, 60)
    while True:
        screen.fill((0,0,0))
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_size()
        screen.blit(font.render("Enter Name:", True, (255,255,255)), (WIDTH//3, HEIGHT//3))
        screen.blit(font.render(username, True, (255,255,255)), (WIDTH//3, HEIGHT//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username:
                    return username
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 12:
                        username += event.unicode

def start_with_resolution():
    global WIDTH, HEIGHT, screen
    res = resolution_menu()
    if res is None:
        return False
    (WIDTH, HEIGHT), flags = res
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    return True

# ---------------- Main Loop ---------------- #
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Start playing menu music
play_menu_music()

while True:
    choice = main_menu()
    if choice == "play":
        if not start_with_resolution():
            continue
        rescale_assets()
        gender = character_selection_menu()
        username = name_input_menu()
        player_imgs = female_imgs_scaled if gender == "female" else male_imgs_scaled
        play_game_music()
        run_game(username, player_imgs)
    elif choice == "leaderboard":
        scores = get_leaderboard()
        font = pygame.font.Font(None, 50)
        viewing = True
        while viewing:
            screen.fill((0,0,0))
            screen.blit(font.render("--Leaderboard --", True, (148,0,211)), (WIDTH//3, HEIGHT//12))
            screen.blit(font.render("(press ESC to leave)", True, (255,255,255)), (WIDTH//3, HEIGHT//1.5))
            for i, (name, score) in enumerate(scores):
                screen.blit(font.render(f"{i+1}. {name} - {score}", True, (255,255,255)),
                            (WIDTH//3, 100 + i*60))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    viewing = False
