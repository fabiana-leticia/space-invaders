import pygame
import random
import os

pygame.init()

# -----------------------------
# SCREEN SETUP
# -----------------------------
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# -----------------------------
# COLORS AND FONTS
# -----------------------------
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# -----------------------------
# PATHS
# -----------------------------
CURRENT_PATH = os.path.dirname(__file__)
ALIENS_PATH = os.path.join(CURRENT_PATH, "aliens")

# -----------------------------
# PLAYER CLASS
# -----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT - 30))
        self.speed = 5
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

# -----------------------------
# LASER CLASSES
# -----------------------------
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

# -----------------------------
# ENEMY BASE CLASS (COM CORREÇÃO)
# -----------------------------
class Enemy(pygame.sprite.Sprite):
    direction = 1  # Variável de classe: TODOS os inimigos compartilham essa direção
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 30, 20)
        self.speed = 1  # Velocidade individual por tipo de alien

    def update(self):
        # Apenas movimento HORIZONTAL (vertical e direção tratados no grupo)
        self.rect.x += self.speed * Enemy.direction

# -----------------------------
# ALIEN CLASSES WITH RESIZED IMAGES (INTACTAS!)
# -----------------------------
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 40

class AlienType1(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(os.path.join(ALIENS_PATH, "alien1.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))

class AlienType2(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(os.path.join(ALIENS_PATH, "alien2.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 1.5

class AlienType3(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(os.path.join(ALIENS_PATH, "alien3.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 0.7

# -----------------------------
# GAME LOOP (COM CORREÇÃO NA MOVIMENTAÇÃO DOS INIMIGOS)
# -----------------------------
def run_game():
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    laser_group = pygame.sprite.Group()
    enemy_laser_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    # Create enemies
    for row in range(3):
        for col in range(8):
            if row == 0:
                enemy = AlienType1(100 + col * 70, 50 + row * 50)
            elif row == 1:
                enemy = AlienType2(100 + col * 70, 50 + row * 50)
            else:
                enemy = AlienType3(100 + col * 70, 50 + row * 50)
            enemy_group.add(enemy)

    score = 0
    difficulty = 1
    running = True

    # Create star background
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    laser = Laser(player.rect.midtop)
                    laser_group.add(laser)

        difficulty += 0.001

        keys = pygame.key.get_pressed()
        player_group.update(keys)
        laser_group.update()
        enemy_laser_group.update()

        # ---------------------------
        # NOVA LÓGICA: VERIFICA BORDA E DESCE (APENAS UMA VEZ POR VEZ)
        # ---------------------------
        edge_hit = False
        # Checa se QUALQUER inimigo tocou na borda esquerda/direita
        for enemy in enemy_group:
            if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                edge_hit = True
                break  # Não precisa checar os outros se um já tocou

        if edge_hit:
            Enemy.direction *= -1  # Inverte direção de TODOS os inimigos
            # Faz TODOS os inimigos descerem 20px (apenas uma vez!)
            for enemy in enemy_group:
                enemy.rect.y += 20

        # Agora atualiza o movimento HORIZONTAL dos inimigos
        enemy_group.update()

        # Enemy shooting
        if len(enemy_group) > 0:
            if random.random() < 0.01 * difficulty:
                shooter = random.choice(enemy_group.sprites())
                enemy_laser = EnemyLaser(shooter.rect.midbottom)
                enemy_laser_group.add(enemy_laser)

        # Collision: player laser hits enemy
        for laser in laser_group:
            hits = pygame.sprite.spritecollide(laser, enemy_group, True)
            if hits:
                laser.kill()
                score += len(hits)

        # Collision: enemy laser hits player
        if pygame.sprite.spritecollide(player, enemy_laser_group, True):
            player.lives -= 1
            if player.lives <= 0:
                return "lose", score

        # Enemy reaches bottom
        for enemy in enemy_group:
            if enemy.rect.bottom >= HEIGHT:
                return "lose", score

        # WIN condition
        if len(enemy_group) == 0:
            return "win", score

        # Increase speed when fewer enemies are alive
        for enemy in enemy_group:
            enemy.speed = 1 + (3 - len(enemy_group) / 8)

        # DRAW
        screen.fill(BLACK)
        for star in stars:
            pygame.draw.circle(screen, WHITE, star, 2)
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
# MENU SCREEN
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
                    if selected == 0:
                        return "play"
                    else:
                        return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(BLACK)
        title = font.render("SPACE INVADERS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        for i, text in enumerate(options):
            color = GREEN if i == selected else WHITE
            option_surf = small_font.render(text, True, color)
            option_rect = option_surf.get_rect(center=(WIDTH // 2, 300 + i * 60))

            if option_rect.collidepoint(mouse_pos):
                option_surf = small_font.render(text, True, GREEN)
                selected = i
                if click:
                    if i == 0:
                        return "play"
                    else:
                        return "quit"

            screen.blit(option_surf, option_rect)

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# GAME OVER SCREEN
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
        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 200))
        text2 = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 280))
        text3 = small_font.render("Press ENTER to return to menu", True, GREEN)
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, 340))
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
                    if selected == 0:
                        return "play"
                    else:
                        return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(BLACK)
        title = font.render("YOU WIN!", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 230))

        for i, text in enumerate(options):
            color = GREEN if i == selected else WHITE
            option_surf = small_font.render(text, True, color)
            option_rect = option_surf.get_rect(center=(WIDTH // 2, 330 + i * 60))

            if option_rect.collidepoint(mouse_pos):
                option_surf = small_font.render(text, True, GREEN)
                selected = i
                if click:
                    if i == 0:
                        return "play"
                    else:
                        return "quit"

            screen.blit(option_surf, option_rect)

        pygame.display.flip()
        clock.tick(60)

# -----------------------------
# MAIN LOOP
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




