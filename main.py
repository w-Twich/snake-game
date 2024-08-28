import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Simple Slither.io')

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Snake settings
SNAKE_SIZE = 10
SNAKE_SPEED = 15
NUM_AI_SNAKES = 5  # Number of AI-controlled snakes
VARIABILITY = 0.2  # Probability of AI snake moving randomly instead of towards the food (0 to 1)

# Food settings
FOOD_SIZE = 10

# Snake spawn regions
SPAWN_REGIONS = [
    ((0, SCREEN_WIDTH // 2), (0, SCREEN_HEIGHT // 2)),
    ((SCREEN_WIDTH // 2, SCREEN_WIDTH), (0, SCREEN_HEIGHT // 2)),
    ((0, SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2, SCREEN_HEIGHT)),
    ((SCREEN_WIDTH // 2, SCREEN_WIDTH), (SCREEN_HEIGHT // 2, SCREEN_HEIGHT)),
    ((SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4), (SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4))
]

class Snake:
    def __init__(self, is_human=True, spawn_region=None):
        if spawn_region:
            spawn_x_range, spawn_y_range = spawn_region
            start_x = random.randint(spawn_x_range[0], spawn_x_range[1]) // SNAKE_SIZE * SNAKE_SIZE
            start_y = random.randint(spawn_y_range[0], spawn_y_range[1]) // SNAKE_SIZE * SNAKE_SIZE
            self.positions = [(start_x, start_y)]
        else:
            self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        
        self.length = 1
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])  # Use tuples for direction
        self.color = GREEN if is_human else WHITE
        self.score = 0
        self.is_human = is_human
        self.alive = True

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        if not self.alive:
            return

        cur = self.get_head_position()
        x, y = self.direction  # Now x and y will correctly unpack the direction tuple
        new = (((cur[0] + (x * SNAKE_SIZE)) % SCREEN_WIDTH), (cur[1] + (y * SNAKE_SIZE)) % SCREEN_HEIGHT)
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.score = 0
        self.alive = True

    def draw(self, surface):
        if self.alive:
            for p in self.positions:
                pygame.draw.rect(surface, self.color, (p[0], p[1], SNAKE_SIZE, SNAKE_SIZE))

    def handle_keys(self):
        if self.is_human:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.turn((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.turn((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.turn((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.turn((1, 0))

    def move_ai(self, food_position):
        if not self.alive:
            return

        head_x, head_y = self.get_head_position()
        food_x, food_y = food_position

        if random.random() < VARIABILITY:
            # Move in a random direction
            self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        else:
            # Move towards the food
            if head_x < food_x:
                self.direction = (1, 0)  # Move right
            elif head_x > food_x:
                self.direction = (-1, 0)  # Move left
            elif head_y < food_y:
                self.direction = (0, 1)  # Move down
            elif head_y > food_y:
                self.direction = (0, -1)  # Move up

        self.move()

class Food:
    def __init__(self, position=None):
        if position:
            self.position = position
        else:
            self.position = (0, 0)
            self.randomize_position()
        self.color = RED

    def randomize_position(self):
        self.position = (random.randint(0, (SCREEN_WIDTH // FOOD_SIZE) - 1) * FOOD_SIZE,
                         random.randint(0, (SCREEN_HEIGHT // FOOD_SIZE) - 1) * FOOD_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], FOOD_SIZE, FOOD_SIZE))

def check_collision(snake, snakes):
    head_pos = snake.get_head_position()
    for s in snakes:
        if s != snake and s.alive and head_pos in s.positions:  # Only check against alive snakes
            return True
    if snake.length > 1 and head_pos in snake.positions[1:]:  # Self-collision
        return True
    return False

def handle_death(snake, food_list):
    snake.alive = False
    for pos in snake.positions:
        food_list.append(Food(position=pos))

def check_food_collection(snake, food_list):
    head_pos = snake.get_head_position()
    for food in food_list[:]:  # Iterate over a copy of the list to allow modification during iteration
        if head_pos == food.position:
            snake.length += 1
            snake.score += 1
            food_list.remove(food)  # Remove the collected food from the list

def main():
    human_snake = Snake(is_human=True, spawn_region=SPAWN_REGIONS[0])
    ai_snakes = [Snake(is_human=False, spawn_region=SPAWN_REGIONS[(i + 1) % len(SPAWN_REGIONS)]) for i in range(NUM_AI_SNAKES)]
    all_snakes = [human_snake] + ai_snakes
    food = Food()
    food_list = [food]

    while True:
        clock.tick(SNAKE_SPEED)
        human_snake.handle_keys()
        human_snake.move()

        for ai_snake in ai_snakes:
            ai_snake.move_ai(food.position)

        # Check collisions
        for s in all_snakes:
            if s.alive and check_collision(s, all_snakes):
                handle_death(s, food_list)

        # Check if any snake collected food
        check_food_collection(human_snake, food_list)
        for ai_snake in ai_snakes:
            check_food_collection(ai_snake, food_list)

        # Add new food if the current one is collected
        if not food_list:  # If the food list is empty, add new food
            new_food = Food()
            food_list.append(new_food)

        screen.fill(BLACK)

        # Draw snakes and food
        human_snake.draw(screen)
        for ai_snake in ai_snakes:
            ai_snake.draw(screen)
        for food_item in food_list:
            food_item.draw(screen)

        pygame.display.update()

if __name__ == '__main__':
    main()
