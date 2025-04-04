import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load & Play Battle Music
pygame.mixer.music.load("pokemon_gym_battle.mp3")  # Replace with your actual file
pygame.mixer.music.set_volume(0.5)

def start_battle_music():
    pygame.mixer.music.play(-1)  # Loop indefinitely

def stop_battle_music():
    pygame.mixer.music.stop()

# Screen Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game - 3 Rounds")

# Load & Scale Background Image
background = pygame.image.load("battle arena.jpeg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load & Resize Pokémon
def load_pokemon(name, size):
    img = pygame.image.load(f"{name}.png").convert_alpha()
    return pygame.transform.scale(img, size)

battle_size, selection_size = (200, 200), (150, 150)
pokemons = {
    "charmander": load_pokemon("Charmander", battle_size),
    "squirtle": load_pokemon("Squirtle", battle_size),
    "bulbasaur": load_pokemon("Bulbasaur", battle_size)
}
pokemon_selection_imgs = {
    name: pygame.transform.scale(img, selection_size) for name, img in pokemons.items()
}

# Flash Colors
FLASH_COLORS = {"charmander": (255, 69, 0), "squirtle": (30, 144, 255), "bulbasaur": (34, 139, 34)}

# Positions
player_pos, enemy_pos = (100, 300), (500, 100)

# Health Bars
HEALTH_WIDTH, HEALTH_HEIGHT = 120, 15

# Fonts & Colors
font = pygame.font.Font(None, 40)
WHITE, RED, GREEN, BLACK, YELLOW = (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 0), (255, 255, 0)

# Game State
player_health, enemy_health = 100, 100
attack_text, attack_timer = "", 0
display_attack_text = False
player_choice, ai_choice, selected_attack = None, None, 0
current_round, player_wins = 1, 0
player_attack_boost = 0  # Attack damage boost after winning 2 rounds

# Attack Moves
attack_moves = {
    "charmander": ["Flamethrower", "Scratch", "Ember", "Fire Spin"],
    "squirtle": ["Water Gun", "Tackle", "Bubble", "Aqua Tail"],
    "bulbasaur": ["Vine Whip", "Tackle", "Razor Leaf", "Solar Beam"]
}

# Flash Effect Variables
flash_start_time, flash_active, flash_color = 0, False, WHITE

# Draw Functions
def draw_health_bar(x, y, health):
    pygame.draw.rect(screen, RED, (x, y, HEALTH_WIDTH, HEALTH_HEIGHT))
    pygame.draw.rect(screen, GREEN, (x, y, HEALTH_WIDTH * (health / 100), HEALTH_HEIGHT))

def draw_text(text, x, y, color=WHITE):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

# Optimized Colored Flash Effect
def flash_effect(pokemon):
    global flash_start_time, flash_active, flash_color
    flash_color = FLASH_COLORS.get(pokemon, WHITE)
    flash_start_time, flash_active = pygame.time.get_ticks(), True

# Pokémon Selection
def pokemon_selection():
    global player_choice, ai_choice
    selected_pokemon, running = 0, True

    while running:
        screen.fill(BLACK)
        draw_text("Choose Your Pokémon!", 250, 80)

        positions = [150, 320, 500]
        for i, name in enumerate(["charmander", "squirtle", "bulbasaur"]):
            x_pos = positions[i]
            screen.blit(pokemon_selection_imgs[name], (x_pos, 250))

            if i == selected_pokemon:
                pygame.draw.rect(screen, YELLOW, (x_pos - 10, 240, 170, 170), 5)

        draw_text("← → to navigate, ENTER to select", 180, 500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_pokemon = (selected_pokemon - 1) % 3
                if event.key == pygame.K_RIGHT:
                    selected_pokemon = (selected_pokemon + 1) % 3
                if event.key == pygame.K_RETURN:
                    player_choice = ["charmander", "squirtle", "bulbasaur"][selected_pokemon]
                    ai_choice = random.choice(["charmander", "squirtle", "bulbasaur"])
                    running = False

        pygame.display.update()

# Start Game
pokemon_selection()
start_battle_music()
running, player_turn, ai_attack_pending = True, True, False

# Game Loop
while running and current_round <= 3:
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    screen.blit(pokemons[player_choice], player_pos)
    screen.blit(pokemons[ai_choice], enemy_pos)

    draw_health_bar(player_pos[0] + 20, player_pos[1] - 30, player_health)
    draw_health_bar(enemy_pos[0] + 20, enemy_pos[1] - 30, enemy_health)

    # Display Round Info
    draw_text(f"Round {current_round}/3 - Wins: {player_wins}", 300, 20)

    # Colored Flash Effect (Non-blocking)
    if flash_active and pygame.time.get_ticks() - flash_start_time < 300:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surface.fill(flash_color)
        flash_surface.set_alpha(120)
        screen.blit(flash_surface, (0, 0))
    else:
        flash_active = False

    # Display Attack Text for 1 sec
    if display_attack_text and pygame.time.get_ticks() - attack_timer < 1000:
        draw_text(attack_text, 250, 250)
    else:
        display_attack_text = False

        # Execute AI Attack if needed
        if ai_attack_pending:
            ai_move = random.choice(attack_moves[ai_choice])
            attack_text = f"{ai_choice.capitalize()} used {ai_move}!"
            attack_timer, display_attack_text = pygame.time.get_ticks(), True
            flash_effect(ai_choice)
            player_health -= random.randint(15, 25)
            player_turn, ai_attack_pending = True, False

    # Player Attack Options
    if player_turn:
        for i, move in enumerate(attack_moves[player_choice]):
            draw_text(f"{i+1}. {move}", 550, 450 + (i * 30), GREEN if i == selected_attack else WHITE)

    # Check for Round End
    if player_health <= 0 or enemy_health <= 0:
        if enemy_health <= 0:
            player_wins += 1
        current_round += 1
        # Reset for next round
        player_health, enemy_health = 100, 100
        ai_choice = random.choice(["charmander", "squirtle", "bulbasaur"])
        player_turn, ai_attack_pending = True, False
        
        # Apply boosts after winning 2 rounds
        if player_wins >= 2 and current_round <= 3:
            player_health = 150  # Health boost
            player_attack_boost = 10  # Attack boost
            draw_text("Your Pokémon got stronger!", 250, 300)
            pygame.display.update()
            pygame.time.delay(2000)

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if player_turn and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_attack = (selected_attack + 1) % 4
            if event.key == pygame.K_UP:
                selected_attack = (selected_attack - 1) % 4
            if event.key == pygame.K_RETURN:
                attack_text = f"{player_choice.capitalize()} used {attack_moves[player_choice][selected_attack]}!"
                attack_timer, display_attack_text = pygame.time.get_ticks(), True
                flash_effect(player_choice)
                enemy_health -= random.randint(15, 25) + player_attack_boost
                player_turn, ai_attack_pending = False, True

    pygame.display.update()

# End Game
stop_battle_music()
screen.fill(BLACK)
final_result = "You Won the Tournament!" if player_wins >= 2 else "AI Won the Tournament!"
draw_text(final_result, 250, 250)
draw_text(f"Final Score - Wins: {player_wins}/3", 250, 300)
pygame.display.update()
pygame.time.delay(3000)
pygame.quit()