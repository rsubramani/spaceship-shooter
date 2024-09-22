import pygame
from .enemy import Enemy
from .powerup import PowerUp

def start_screen(screen):
    font = pygame.font.Font(None, 72)
    option_font = pygame.font.Font(None, 36)

    # Title
    title_text = font.render("Space Shooter", True, (255, 255, 255))
    screen.blit(title_text, (400 - title_text.get_width() // 2, 100))

    # Difficulty options
    easy_text = option_font.render("Press 1 for Easy", True, (0, 255, 0))
    medium_text = option_font.render("Press 2 for Medium", True, (0, 0, 255))
    hard_text = option_font.render("Press 3 for Hard", True, (255, 0, 0))
    tutorial_text = option_font.render("Press T for Tutorial", True, (255, 255, 255))

    # Display options
    screen.blit(easy_text, (400 - easy_text.get_width() // 2, 300))
    screen.blit(medium_text, (400 - medium_text.get_width() // 2, 350))
    screen.blit(hard_text, (400 - hard_text.get_width() // 2, 400))
    screen.blit(tutorial_text, (400 - tutorial_text.get_width() // 2, 450))


def draw_hud(screen, level, missed_aliens, max_missed_aliens):
    font = pygame.font.Font(None, 36)
    pygame.draw.rect(screen, (0, 0, 255), (0, 0, 800, 50))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    missed_text = font.render(f"Missed: {missed_aliens}/{max_missed_aliens}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))
    screen.blit(missed_text, (200, 10))

def spawn_enemy(game):
    if pygame.time.get_ticks() % 100 == 0:  # Spawn an enemy every 100 ticks
        enemy = Enemy(game.enemy_image)
        game.all_sprites.add(enemy)
        game.enemies.add(enemy)

def spawn_powerup(game):
    if pygame.time.get_ticks() % 500 == 0:  # Spawn a power-up every 500 ticks
        powerup_type = random.choice(['rapid_fire', 'shield', 'bomb'])
        if powerup_type == 'rapid_fire':
            powerup = PowerUp('rapid_fire', game.rapid_fire_image)
        elif powerup_type == 'shield':
            powerup = PowerUp('shield', game.shield_image)
        else:
            powerup = PowerUp('bomb', game.bomb_image)
        game.all_sprites.add(powerup)
        game.powerups.add(powerup)

def start_screen(screen):
    font = pygame.font.Font(None, 72)
    title_text = font.render("Space Shooter", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(title_text, (400 - title_text.get_width() // 2, 100))
    pygame.display.flip()

def tutorial_screen(screen):
    font = pygame.font.Font(None, 36)
    screen.fill((0, 0, 0))
    tutorial_text = font.render("Press S to skip the tutorial", True, (0, 255, 0))
    screen.blit(tutorial_text, (400 - tutorial_text.get_width() // 2, 300))
    pygame.display.flip()

def set_difficulty(level, game):
    if level == 'easy':
        game.max_missed_aliens = 15
    elif level == 'medium':
        game.max_missed_aliens = 10
    elif level == 'hard':
        game.max_missed_aliens = 5
