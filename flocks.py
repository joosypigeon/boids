import numpy as np
from boid import boid, boid_predator
import pygame
from spatialhashtable import spatialhashtable
from my_colors import *
from slider import *
#from multiprocessing import Pool

class flock:
    def __init__(self, fps, boid_size, n_boids, field_dimensions, velocity, sd):

        self.visual_range = boid_size * 5.0
        self.visual_range_squared = self.visual_range * self.visual_range
        self.visual_range_vector = np.array([self.visual_range, self.visual_range])
        self.visual_diameter_vector = 2.0 * self.visual_range_vector

        self.protected_range = boid_size * 4.5
        self.protected_range_squared = self.protected_range * self.protected_range
        self.protected_range_vector = np.array([self.protected_range, self.protected_range])
        
        self.centering_factor = boid_size * 0.001
        self.avoid_factor = boid_size * 0.01
        self.predator_avoid_factor = boid_size * 20.0
        self.matching_factor = boid_size * 0.01
        self.turn_factor = boid_size * 0.5
        
        self.maxspeed = boid_size * 15.0
        self.maxspeed_squared = self.maxspeed * self.maxspeed
        self.minspeed = boid_size * 10.0
        self.minspeed_squared = self.minspeed * self.minspeed
        
        self.predator_turn_factor = boid_size * 1.0 
        
        self.predator_range = boid_size * 6.0
        self.predator_range_times_two = 2.0 * self.predator_range
        self.predator_range_squared = self.predator_range * self.predator_range
        
        self.predator_maxspeed = boid_size * 25.0
        self.predator_maxspeed_squared = self.predator_maxspeed * self.predator_maxspeed
        self.predator_minspeed = boid_size * 20.0
        self.predator_minspeed_squared = self.predator_minspeed * self.predator_minspeed
        
        assert self.protected_range < self.visual_range
        assert self.visual_range < self.predator_range
        
        self.maxbias = 0.01
        self.bias_increment = 0.00004
        self.default_biasval = 0.001
        self.margin = 500

        self.time_delta = None

        self.fps = fps
        
        self.boid_size = boid_size
        self.boid_size_vector = np.array([boid_size, boid_size])
        self.boid_size_vector_half = np.array([boid_size/2, boid_size/2])    
        
        self.n_boids = n_boids
        self.field_dimensions = field_dimensions
        self.velocity = velocity
        self.space_sd = (sum(field_dimensions) / len(field_dimensions))*sd
        self.velocity_sd = (sum(velocity) / len(velocity)) * sd * 8.0
        self.sht = spatialhashtable(self.boid_size*1.5)
        self.sht.flock = self
        self.boids = []
        for index in range(self.n_boids):
            self.boids.append(boid(self, index))
        self.boids.append(boid_predator(self, n_boids))
        self.predator = self.boids[n_boids]
        self.part = 6
        self.controls = controls(self)
        print(f"self.predator.index: {self.predator.index}")
        print(f"len(self.boids): {len(self.boids)}")


    def set_boid_size(self, value):
        self.boid_size = value
        self.boid_size_vector = np.array([value, value])
        self.boid_size_vector_half = np.array([value/2, value/2])    
        self.sht.set_cell_size(2.0 * value)

    def set_visual_range(self, value):
        self.visual_range = self.boid_size * value
        self.visual_range_squared = self.visual_range * self.visual_range
        self.visual_range_vector = np.array([self.visual_range, self.visual_range])
        self.visual_diameter_vector = 2.0 * self.visual_range_vector
        
    def set_protected_range(self, value):
        self.protected_range = self.boid_size * value
        self.protected_range_squaredx = self.protected_range * self.protected_range
        self.protected_range_squared = self.protected_range * self.protected_range
        self.protected_range_vector = np.array([self.protected_range, self.protected_range])


    def set_predator_range(self, value):
        self.predator_range = self.boid_size * value
        self.predator_range_times_two = 2.0 * self.predator_range
        self.predator_range_squared = self.predator_range * self.predator_range
    
    def split_list(self, data):
        parts = self.parts
        length = len(data)
        return [data[i*length // parts: (i+1)*length // parts] for i in range(parts)]

    def draw(self, pygame, screen):
        for boid in self.boids:
            boid.draw(pygame, screen)
        pygame.draw.rect(screen, BLUE, pygame.Rect((self.margin, self.margin), (self.field_dimensions[0] - 2*self.margin, self.field_dimensions[1] - 2*self.margin)), width=1)
        #self.sht.draw_table(pygame, screen)

    def update(self):
        for boid in self.boids:
            boid.update()
        for boid in self.boids:
            boid.commit()
        
class controls:
    def __init__(self, flock):
        self.flock = flock
        margin = self.flock.margin
        boid_size = self.flock.boid_size
        offset = 100
        self.slider_boid_size = Slider(offset, offset, 300, 30, 5, 50, boid_size, "Boid size:", AQUA)
        self.slider_visual_range = Slider(offset, offset+100, 300, 30, 1, 20, 5, "Visual range:", AQUA)
        self.slider_protected_range = Slider(offset, offset+200, 300, 30, 1, 20, 4.5, "Protected range:", AQUA)
        self.slider_predator_range = Slider(offset, offset+300, 300, 30, 1, 20, 6.0, "Predator range:", AQUA)

    def handle_event(self, event):
        result = None
 
        result = self.slider_boid_size.handle_event(event)
        if result:
            self.flock.set_boid_size(result)
            visual_range = self.slider_visual_range.get_value()
            self.flock.set_visual_range(visual_range)
            protected_range = self.slider_protected_range.get_value()
            self.flock.set_protected_range(protected_range)
            protected_range = self.slider_predator_range.get_value()
            self.flock.set_predator_range(protected_range)
            return result

        result = self.slider_visual_range.handle_event(event)
        if result:
            self.flock.set_visual_range(result)
            return result
            
        result = self.slider_protected_range.handle_event(event)
        if result:
            self.flock.set_protected_range(result)
            return result
        
        result = self.slider_predator_range.handle_event(event)
        if result:
            self.flock.set_predator_range(result)
            return result
            
        return result

        
    def draw(self, screen):
        self.slider_boid_size.draw(screen)
        self.slider_visual_range.draw(screen)
        self.slider_protected_range.draw(screen)
        self.slider_predator_range.draw(screen)
        
def main():
    pygame.init()
    field_dimensions = np.array([pygame.display.Info().current_w, pygame.display.Info().current_h])
    sd = 0.1
    f = flock(1, field_dimensions, np.array([1,2]), np.array([3, 4]), sd)
    print(f.boids[0]) 
        
if __name__ == "__main__":
    main()

