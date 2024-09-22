import pygame
from .player import Spaceship
from .bullet import Bullet
from .enemy import Enemy
from .powerup import PowerUp
from .utils import draw_hud, spawn_enemy, spawn_powerup

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Load images
        self.spaceship_image = pygame.image.load("images/spaceship.png")
        self.bullet_image = pygame.image.load("images/bullet.png")
        self.enemy_image = pygame.image.load("images/alien.png")
        self.rapid_fire_image = pygame.image.load("images/rapid_fire.png")
        self.shield_image = pygame.image.load("images/shield.png")
        self.bomb_image = pygame.image.load("images/bomb.png")

        # Player initialization
        self.player = Spaceship(self.spaceship_image)
        self.all_sprites.add(self.player)

        # Game state
        self.missed_aliens = 0
        self.level = 1
        self.max_missed_aliens = 10

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Spawn enemies and powerups
            spawn_enemy(self)
            if self.level >= 3:
                spawn_powerup(self)

            # Update sprites
            self.all_sprites.update()

            # Draw everything
            self.screen.fill((0, 0, 0))
            self.all_sprites.draw(self.screen)
            draw_hud(self.screen, self.level, self.missed_aliens, self.max_missed_aliens)

            pygame.display.flip()
            clock.tick(60)
