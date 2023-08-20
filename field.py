import platform
import sys
print(platform.python_implementation())  # Outputs the Python implementation, e.g., CPython, PyPy, Jython, etc.
print(sys.version)  # Outputs detailed version information.
#import cProfile
import pygame
from spatialhashtable import *
import boid
from flocks import flock
import numpy as np
import time
from my_colors import *


NUMBER_BOIDS = 600
BOID_SIZE = 15
INITIAL_VELOCITY = np.array([50,100])
SD = 0.1
FPS = 30
GRAPHICAL_DEBUG = False
ENABLE_DEBUG = True

def main():
    index = 0
    #start_time = time.perf_counter()
    global GRAPHICAL_DEBUG
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont(None, 18)
    # Get screen resolution
    screen_resolution = (WIDTH, HEIGHT) = pygame.display.Info().current_w, pygame.display.Info().current_h
    print(f"screen_resolution: {screen_resolution}")
    
    # Create a screen with the specified dimensions
    # Set the display mode to full screen
    screen = pygame.display.set_mode(screen_resolution, pygame.FULLSCREEN)
    pygame.display.set_caption("boids")
    clock = pygame.time.Clock()
    f = flock(FPS, BOID_SIZE, NUMBER_BOIDS, np.array((WIDTH, HEIGHT)), INITIAL_VELOCITY, SD)
    screen.fill(BLACK)
    f.draw(pygame, screen)
    pygame.display.flip()
    clock.tick(FPS)
    running = True
    while running:
        screen.fill(BLACK)
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                running = False
                break
            if not f.controls.handle_event(event) and event.type == pygame.MOUSEBUTTONDOWN and ENABLE_DEBUG:
                GRAPHICAL_DEBUG = not GRAPHICAL_DEBUG
                index = f.sht.nearest(*event.pos)
    
        f.time_delta = clock.tick(FPS) / 1000.0
        #print(f"f.time_delta: {f.time_delta}")
        if GRAPHICAL_DEBUG:
            f.time_delta = 0.01
        
        f.update()
        f.draw(pygame, screen)
        
        if GRAPHICAL_DEBUG:
            # debug debug debug debug debug debug debug debug debug debug debug debug debug debug

            f.sht.draw_table(pygame, screen)

            for b in f.boids:
                text_surface = font.render(f"{b.index}:{b.bin}", True, RED)
                screen.blit(text_surface, b.position)
                
            boid = f.boids[index]
            boid.draw(pygame, screen, color = GREEN)
            pygame.draw.circle(screen, BLUE, boid.position, f.visual_range, 1)
            pygame.draw.circle(screen, RED, boid.position, f.protected_range, 1) 
            rect_check = pygame.Rect(boid.position - boid.flock.visual_range_vector, boid.flock.visual_diameter_vector)
            pygame.draw.rect(screen, ORANGE, rect_check, 1)
            pygame.draw.circle(screen, GREEN, rect_check.topleft, 3.0)
            pygame.draw.circle(screen, GREEN, rect_check.bottomright, 3.0)
             # Assuming bbox is a pygame Rect object
            # Get the top-left and bottom-right corners
            x_min, y_min = rect_check.topleft
            x_max, y_max = rect_check.bottomright
            #logging.debug(f'nearby_keys: x_min: {x_min}, y_min: {y_min}, x_min: {x_min}, y_min: {y_min}')
            bins = f.sht.bins(x_min, y_min, x_max, y_max)
            f.sht.draw_bins(pygame, screen, bins, color = YELLOW)
            
            x_min_hash, y_min_hash = f.sht.hash_pos(x_min, y_min)
            rect = pygame.Rect((x_min_hash*f.sht.cell_size, y_min_hash*f.sht.cell_size), (f.sht.cell_size, f.sht.cell_size))
            pygame.draw.rect(screen, AQUA, rect, 1)
            x_max_hash, y_max_hash = f.sht.hash_pos(x_max, y_max)
            rect = pygame.Rect((x_max_hash*f.sht.cell_size, y_max_hash*f.sht.cell_size), (f.sht.cell_size, f.sht.cell_size))
            pygame.draw.rect(screen, AQUA, rect, 1)
    
            for b in boid.visual:
                b.draw(pygame, screen, color = DARKGREEN)
                text_surface = font.render(str(b.index), True, DARKGREEN)
                screen.blit(text_surface, b.position)
                # distance = np.sqrt(np.sum(np.square(boid.position - b.position)))
                # text_surface = font.render(str(distance), True, YELLOW)
                # screen.blit(text_surface, b.position)
                
            for b in boid.seperation:
                b.draw(pygame, screen, color = DARKMAGENTA)
                text_surface = font.render(str(b.index), True, DARKMAGENTA)
                screen.blit(text_surface, b.position)
                # distance = np.sqrt(np.sum(np.square(boid.position - b.position)))
                # text_surface = font.render(str(distance), True, ORANGE)
                # screen.blit(text_surface, b.position)

            time.sleep(1.0)
            # debug end debug end debug end debug end debug end debug end debug end debug end

        
        f.controls.draw(screen)
        pygame.display.flip()

        # current_time = time.perf_counter()
        # if current_time - start_time > 180.0:
            # running = False

    pygame.quit()
    exit()
    
if __name__ == "__main__":
    # cProfile.run('main()', sort="cumtime")
    main()