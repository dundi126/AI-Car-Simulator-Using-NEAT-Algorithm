import math
import sys
import neat
import pygame
import logging

# Constants
WIDTH = 1920
HEIGHT = 1080
CAR_SIZE_X = 50    
CAR_SIZE_Y = 50
BORDER_COLOR = (255, 255, 255, 255)  # Color to Crash on Hit
current_generation = 0  # Generation counter

# Configure logging
logging.basicConfig(filename='simulation_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

class Car:

    def __init__(self):
        self.sprite = pygame.image.load('assets/car.png').convert()  # Load car sprite
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        self.position = [1475, 930]  # Starting position
        self.angle = 40
        self.speed = 0

        self.speed_set = False  # Flag for default speed later on
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]  # Calculate center
        self.radars = []  # List for sensors/radars
        self.drawing_radars = []  # Radars to be drawn
        self.alive = True  # Boolean to check if car is crashed
        self.distance = 0  # Distance driven
        self.time = 0  # Time passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw car sprite
        self.draw_radar(screen)  # Optionally draw sensors

    def draw_radar(self, screen):
        # Optionally draw all sensors/radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, game_map):
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        self.distance += self.speed
        self.time += 1

        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], HEIGHT - 120)

        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(game_map)
        self.radars.clear()

        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive
# Calculates the fitness score
    def get_reward(self):
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image

def log_car_status(car, generation, car_index):
    logging.info(f"Generation {generation} - Car {car_index}: Speed: {car.speed}, " f"Angle: {car.angle}, Distance: {car.distance}, Alive: {car.alive}")
# Each genome represents a neural network controlling a car, and fitness scores determine their success. WE run the NEAT config
def run_simulation(genomes, config):
    nets = []
    cars = []
    

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Car())

    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 20)
    alive_font = pygame.font.SysFont("Arial", 16)
    circute_font = pygame.font.SysFont("Arial", 40)
    game_map = pygame.image.load('assets/mexico.png').convert()

    global current_generation
    current_generation += 1

    logging.info(f"Starting Generation {current_generation}")

    counter = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Simulation quit by user")
                sys.exit(0)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow down
            else:
                car.speed += 2  # Speed up

        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()
                log_car_status(car, current_generation, i)

        if still_alive == 0:
            logging.info(f"All cars crashed in Generation {current_generation}")
            break

        counter += 1
        if counter == 30 * 40:  # Stop after about 20 seconds
            logging.info(f"Generation {current_generation} stopped after max time")
            print
            break
        # Visualizes progress in real time, making it easier to observe how the AI evolves.
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1780, 50)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1780, 80)
        screen.blit(text, text_rect)

        text = circute_font.render("AI-CarSimulation ", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (990, 370)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    logging.info(f"Generation {current_generation} ended")

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 150 Generations
    population.run(run_simulation, 150)
