import pygame
import sys
import random
import os
import time
pygame.init()

# ---------------- Initial temporary screen ---------------- #
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Pixel Runner")
clock = pygame.time.Clock()

# ---------------- Assets ---------------- #
backgroundImg = pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/pixilart-drawing.png")

female_imgs = [
    pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/femmovewalkanim1-pixilart (3).png").convert_alpha(),
    pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/femmovewalkanim2-pixilart (5).png").convert_alpha()
]

male_imgs = [
    pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/malewalkanim1.png").convert_alpha(),
    pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/malewalkanim2.png").convert_alpha()
]

obstacle_img = pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/seat-model-pixilart.png").convert_alpha()
overhead_img = pygame.image.load("C:/Users/bmcmonigle8180/Documents/SE/SE.git/pygame models/brick-over-head-pixilart.png").convert_alpha()

# ---------------- Constants ---------------- #
gravity = 0.6
jump_strength = -9
ground_level_ratio = 0.82
LEADERBOARD_FILE = "leaderboard.txt"

BASE_SPEED = 5
MAX_SPEED = 15
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

#----------- Spawn Checker ---------------#
def can_spawn(new_x, obstacles, overheads):
    for r in obstacles:
        if abs(r.x - new_x) < MIN_SPACING:
            return False
    for r in overheads:
        if abs(r.x - new_x) < MIN_SPACING:
            return False
    return True
#change spacings in contents
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

    while True:
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

        # Player physics
        velocity_y += gravity
        player_y += velocity_y
        if player_y > ground_level - player_imgs[0].get_height():
            player_y = ground_level - player_imgs[0].get_height()
            velocity_y = 0

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

        # ---------------- Spawn Obstacles ---------------- #
        if len(obstacles) == 0 or obstacles[-1].x < WIDTH - 300:
            for _ in range(10):
                new_x = WIDTH + random.randint(0, 200)
                if can_spawn(new_x, obstacles, overheads):
                    rect = obstacle_img_scaled.get_rect()
                    rect.x = new_x
                    rect.y = ground_level - rect.height
                    obstacles.append(rect)
                    break
        #-------- Spawn Overhead ---------------------------#
        if len(overheads) == 0 or overheads[-1].x < WIDTH - 500:
            for _ in range(10):
                new_x = WIDTH + random.randint(200, 400)
                if can_spawn(new_x, obstacles, overheads):
                    rect = overhead_img_scaled.get_rect()
                    rect.x = new_x
                    rect.y = ground_level - player_imgs[0].get_height() - OVERHEAD_HEIGHT_OFFSET
                    overheads.append(rect)
                    break

        # Move obstacles
        for r in obstacles:
            r.x -= scroll_speed
        for r in overheads:
            r.x -= scroll_speed

        # Remove off-screen objects
        obstacles = [r for r in obstacles if r.x > -100]
        overheads = [r for r in overheads if r.x > -100]

        # Collision
        player_rect = current_img.get_rect(topleft=(player_x, player_y))
        hit_type = None
        for r in obstacles:
            if player_rect.colliderect(r):
                hit_type = "Ground Obstacle"
        for r in overheads:
            if player_rect.colliderect(r):
                hit_type = "Overhead Obstacle"
        if hit_type:
            save_score(username, score)
            return score, hit_type

        # Draw
        for r in obstacles:
            screen.blit(obstacle_img_scaled, r)
        for r in overheads:
            screen.blit(overhead_img_scaled, r)
        screen.blit(current_img, (player_x, player_y))
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (20, HEIGHT - 40))

        pygame.display.update()
        clock.tick(60)

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
                    return "play"
                if event.key == pygame.K_2:
                    return "leaderboard"
                if event.key == pygame.K_3:
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

while True:
    choice = main_menu()
    if choice == "play":
        if not start_with_resolution():
            continue
        rescale_assets()
        gender = character_selection_menu()
        username = name_input_menu()
        player_imgs = female_imgs_scaled if gender == "female" else male_imgs_scaled
        while True:
            score, hit_type = run_game(username, player_imgs)
            break
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
