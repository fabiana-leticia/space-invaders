import pygame
import random

pygame.init()

# Screen
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

# -----------------------------
# FUNCTIONS
# -----------------------------
def generate_stars(num_stars):
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        stars.append([x, y, size])
    return stars

def draw_stars(stars):
    for star in stars:
        star[1] += 1
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        pygame.draw.rect(screen, WHITE, (star[0], star[1], star[2], star[2]))

# -----------------------------
# CLASSES
# -----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT - 30))
        self.speed = 5
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 7

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 1
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += 20

# -----------------------------
# GAME LOOP
# -----------------------------
def run_game():
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    laser_group = pygame.sprite.Group()
    enemy_laser_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    for row in range(3):
        for col in range(8):
            enemy_group.add(Enemy(100 + col*70, 50 + row*50))

    stars = generate_stars(100)
    score = 0
    difficulty = 1
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                laser_group.add(Laser(player.rect.midtop))

        difficulty += 0.001
        keys = pygame.key.get_pressed()
        player_group.update(keys)
        laser_group.update()
        enemy_group.update()
        enemy_laser_group.update()

        # Enemy shooting
        if len(enemy_group) > 0 and random.random() < 0.01 * difficulty:
            shooter = random.choice(enemy_group.sprites())
            enemy_laser_group.add(EnemyLaser(shooter.rect.midbottom))

        # Collisions
        for laser in laser_group:
            hits = pygame.sprite.spritecollide(laser, enemy_group, True)
            if hits:
                laser.kill()
                score += len(hits)

        if pygame.sprite.spritecollide(player, enemy_laser_group, True):
            player.lives -= 1
            if player.lives <= 0:
                return ("lose", score)

        for enemy in enemy_group:
            if enemy.rect.bottom >= HEIGHT:
                return ("lose", score)

        if len(enemy_group) == 0:
            return ("win", score)

        for enemy in enemy_group:
            enemy.speed = 1 + (3 - len(enemy_group)/8)

        # DRAW
        screen.fill(BLACK)
        draw_stars(stars)
        player_group.draw(screen)
        laser_group.draw(screen)
        enemy_group.draw(screen)
        enemy_laser_group.draw(screen)

        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = small_font.render(f"Lives: {player.lives}", True, GREEN)
        screen.blit(lives_text, (10, 50))

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# MENU
# -----------------------------
def menu_screen():
    selected = 0
    options = ["New Game", "Quit"]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 2
                elif event.key == pygame.K_RETURN:
                    return "play" if selected == 0 else "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(BLACK)
        title = font.render("SPACE INVADERS", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        for i, text in enumerate(options):
            color = GREEN if i == selected else WHITE
            surf = small_font.render(text, True, color)
            rect = surf.get_rect(center=(WIDTH//2, 300 + i*60))
            if rect.collidepoint(mouse_pos):
                surf = small_font.render(text, True, GREEN)
                selected = i
                if click:
                    return "play" if i == 0 else "quit"
            screen.blit(surf, rect)

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# GAME OVER
# -----------------------------
def game_over_screen(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return "menu"

        screen.fill(BLACK)
        text1 = font.render("GAME OVER", True, RED)
        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 200))
        text2 = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 280))
        text3 = small_font.render("Press ENTER to return to menu", True, GREEN)
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, 340))

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# WIN SCREEN
# -----------------------------
def win_screen(score):
    selected = 0
    options = ["Play Again", "Quit"]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 2
                elif event.key == pygame.K_RETURN:
                    return "play" if selected == 0 else "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(BLACK)
        title = font.render("YOU WIN!", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 230))

        for i, text in enumerate(options):
            color = GREEN if i == selected else WHITE
            surf = small_font.render(text, True, color)
            rect = surf.get_rect(center=(WIDTH//2, 330 + i*60))
            if rect.collidepoint(mouse_pos):
                surf = small_font.render(text, True, GREEN)
                selected = i
                if click:
                    return "play" if i == 0 else "quit"
            screen.blit(surf, rect)

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# MAIN APP LOOP
# -----------------------------
while True:
    choice = menu_screen()
    if choice == "quit":
        break

    result = run_game()
    if result == "quit":
        break

    state, score = result
    if state == "lose":
        reset = game_over_screen(score)
    elif state == "win":
        reset = win_screen(score)

    if reset == "quit":
        break

pygame.quit()



