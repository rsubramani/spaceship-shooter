import pygame
from pygame.tests import test_utils
import unittest
from spaceship import Game, Spaceship, Enemy

class TestGameWithPygameTests(unittest.TestCase):

    def setUp(self):
        """Initialize Pygame and create a Game instance."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))  # Set up a real Pygame screen
        self.game = Game(self.screen)
        self.game.player = Spaceship(self.game.spaceship_image)  # Initialize spaceship

    def tearDown(self):
        """Quit Pygame after each test."""
        pygame.quit()

    def test_shield_prevents_missed_aliens(self):
        """Test that when the shield is active, missed aliens are not counted."""
        self.game.player.activate_shield()  # Activate shield
        self.game.missed_aliens = 0

        # Simulate an enemy moving past the screen without the shield affecting the count
        enemy = Enemy(self.game.enemy_image, speed=1)
        enemy.rect.top = self.screen.get_height() + 1  # Move enemy off-screen
        self.game.enemies.add(enemy)

        # Run the game loop to process this
        self.game.run()

        # Assert that missed_aliens count hasn't increased due to shield
        self.assertEqual(self.game.missed_aliens, 0)

    def test_missed_aliens_without_shield(self):
        """Test that without the shield, missed aliens are counted."""
        self.game.player.shield = False  # Ensure shield is inactive
        self.game.missed_aliens = 0

        # Simulate an enemy moving past the screen without the shield
        enemy = Enemy(self.game.enemy_image, speed=1)
        enemy.rect.top = self.screen.get_height() + 1  # Move enemy off-screen
        self.game.enemies.add(enemy)

        # Run the game loop to process this
        self.game.run()

        # Assert that missed_aliens count has increased
        self.assertEqual(self.game.missed_aliens, 1)

    def test_player_movement(self):
        """Test that the player moves left and right correctly."""
        # Mock Pygame key press events for left arrow and right arrow
        test_utils.press_key(pygame.K_LEFT)
        self.game.player.update()  # Update player based on key press
        self.assertLess(self.game.player.rect.centerx, 400)  # Ensure the player moved left

        test_utils.press_key(pygame.K_RIGHT)
        self.game.player.update()  # Update player based on key press
        self.assertGreater(self.game.player.rect.centerx, 400)  # Ensure the player moved right

    def test_power_up_activation(self):
        """Test that the shield power-up is activated when collected."""
        self.game.player.shield = False  # Ensure shield is not active
        self.game.player.activate_shield()  # Activate the shield power-up
        self.assertTrue(self.game.player.shield)  # Ensure the shield is now active

    def test_game_over_condition(self):
        """Test that the game ends when missed aliens exceed the limit."""
        self.game.missed_aliens = self.game.max_missed_aliens - 1  # Set to one less than max
        self.game.run()  # Run the game loop

        # Assert that the game has not ended yet
        self.assertLess(self.game.missed_aliens, self.game.max_missed_aliens)

        # Simulate missing one more alien, causing game over
        self.game.missed_aliens += 1
        self.game.run()  # Run the game loop

        # Assert that the game is now over
        self.assertEqual(self.game.missed_aliens, self.game.max_missed_aliens)

if __name__ == "__main__":
    unittest.main()
