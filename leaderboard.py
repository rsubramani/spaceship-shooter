import json
import os
import pygame


# Constants for leaderboard
LEADERBOARD_FILE = 'leaderboard.json'
MAX_LEADERBOARD_SIZE = 5

# Leaderboard loading and saving
def load_leaderboard():
    """Loads the leaderboard from a JSON file."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    else:
        return []  # Return an empty list if no file exists

def save_leaderboard(leaderboard):
    """Saves the leaderboard to a JSON file."""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=4)

def update_leaderboard(name, score):
    """Updates the leaderboard with a new score if it qualifies."""
    leaderboard = load_leaderboard()

    # Add the new score to the leaderboard
    leaderboard.append({"name": name, "score": score})

    # Sort the leaderboard by score in descending order
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    # Limit the leaderboard to the top MAX_LEADERBOARD_SIZE scores
    leaderboard = leaderboard[:MAX_LEADERBOARD_SIZE]

    # Save the updated leaderboard
    save_leaderboard(leaderboard)


# Displaying the leaderboard
def draw_leaderboard(screen, font, player_name=None, player_score=None):
    """Draws the leaderboard on the screen and highlights the player's score in yellow."""
    leaderboard = load_leaderboard()
    screen.fill((0, 0, 0))  # Black background

    title_text = font.render("Leaderboard", True, (255, 255, 255))  # White title text
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 50))

    for i, entry in enumerate(leaderboard):
        name = entry['name']
        score = entry['score']
        
        # Highlight the player's score in yellow
        if name == player_name and score == player_score:
            leaderboard_text = font.render(f"{i + 1}. {name}: {score}", True, (255, 255, 0))  # Yellow text
        else:
            leaderboard_text = font.render(f"{i + 1}. {name}: {score}", True, (255, 255, 255))  # White text
        
        screen.blit(leaderboard_text, (screen.get_width() // 2 - leaderboard_text.get_width() // 2, 100 + i * 40))

    pygame.display.flip()


# Prompting for player name
def get_player_name(screen, font):
    """Prompts the player to enter their name for the leaderboard."""
    name = ""
    input_active = True

    while input_active:
        screen.fill((0, 0, 0))  # Black background
        prompt_text = font.render("Enter your name:", True, (255, 255, 255))  # White text
        screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2, 100))

        # Display the player's current name input
        name_text = font.render(name, True, (255, 255, 255))  # White text
        screen.blit(name_text, (screen.get_width() // 2 - name_text.get_width() // 2, 200))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # When Enter is pressed
                    input_active = False  # Finish input
                elif event.key == pygame.K_BACKSPACE:  # Handle backspace
                    name = name[:-1]
                else:
                    name += event.unicode  # Add character to name input

    return name
