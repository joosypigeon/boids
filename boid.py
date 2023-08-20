import numpy as np
import pygame
from my_colors import *



class boid:
    def __init__(self, flock, index):
        self.flock = flock
        self.index = index
        self.velocity = np.random.normal(flock.velocity, flock.velocity_sd)
        self.position = self.random_position(flock.field_dimensions)
        self.displayed = False
        self.seperation = set()
        self.visual = set()
        self.bins = set()
        self.velocity_update = None
        self.position_update = None
        self.bin = "Unset"
        self.color = RED
        self.flock.sht.insert(self)
        self.predated = False

    def commit(self):
        self.flock.sht.remove(self)
        self.velocity = self.velocity_update
        self.position = self.position_update
        self.flock.sht.insert(self)

    def update(self):
        self.predated = False  
        
        self.velocity_update = self.velocity
        self.position_update = self.position 

        # find seperation and visual range boids
        self.seperation.clear()
        self.visual.clear()
        rect_check = pygame.Rect(self.position - self.flock.visual_range_vector, self.flock.visual_diameter_vector)
        potential = self.flock.sht.nearby_keys(rect_check, 0.0)
        # convert hash keys to boids
        #print(f"update: potential: {potential}")
        for index in potential:
            if index == self.index or index == self.flock.boid_size:
                continue
            distance_squared = np.sum(np.square(self.position - self.flock.boids[index].position))

            if distance_squared < self.flock.protected_range_squared:
                self.seperation.add(self.flock.boids[index])
            elif distance_squared < self.flock.visual_range_squared:
                self.visual.add(self.flock.boids[index])

        from_predator = self.position - self.flock.predator.position
        taxi_cab_distance = np.sum(np.abs(from_predator))
        if taxi_cab_distance < self.flock.predator_range_times_two and np.sum(np.square(from_predator)) < self.flock.predator_range_squared:
            # do predator
            self.predated = True
            if from_predator[0] >= 0.0:
                self.velocity_update[0] += self.flock.predator_avoid_factor
            elif from_predator[0] < 0.0:
                self.velocity_update[0] -= self.flock.predator_avoid_factor
            if from_predator[1] >= 0.0:
                self.velocity_update[1] += self.flock.predator_avoid_factor
            elif from_predator[1] < 0.0:
                self.velocity_update[1] -= self.flock.predator_avoid_factor
                
        # do seperation
        if not len(self.seperation) == 0:
            close = np.array([0.0, 0.0])
            for boid in self.seperation:
                close += self.position - boid.position
            self.velocity_update += close * self.flock.avoid_factor 
        
        # do alignment
        if not len(self.visual) == 0: 
            average_velocity = np.array([0.0, 0.0])
            for boid in self.visual:
                average_velocity += boid.velocity
            average_velocity /= len(self.visual)
            self.velocity_update += (average_velocity - self.velocity) * self.flock.matching_factor

        # do cohesion
        if not len(self.visual) == 0:
            average_position = np.array([0.0, 0.0])
            for boid in self.visual:
                average_position += boid.position
            average_position /= len(self.visual)
            self.velocity_update += (average_position - self.position) * self.flock.centering_factor   

        # screen edge
        if self.position[0] < self.flock.margin:
            self.velocity_update[0] += self.flock.turn_factor
        if self.position[0] > self.flock.field_dimensions[0] - self.flock.margin:
            self.velocity_update[0] -= self.flock.turn_factor
        if self.position[1] < self.flock.margin:
            self.velocity_update[1] += self.flock.turn_factor
        if self.position[1] > self.flock.field_dimensions[1] - self.flock.margin:
            self.velocity_update[1] -= self.flock.turn_factor

        # speed limit
        speed_squared = np.sum(np.square(self.velocity_update))
        if speed_squared > self.flock.maxspeed_squared:
            self.velocity_update *= np.sqrt(self.flock.maxspeed_squared/speed_squared)
        if speed_squared < self.flock.minspeed_squared:
            self.velocity_update *= np.sqrt(self.flock.minspeed_squared/speed_squared)

        delta = self.flock.time_delta*self.velocity_update
        self.position_update += delta

        return (self.index, self.position_update, self.velocity_update)

    def snap_to_edge(self, position, dimensions):
        new = np.array(
            [boid.snap_interval(position[0], 0.0, dimensions[0]), 
             boid.snap_interval(position[1], 0.0, dimensions[1])])
        #print(f"snap: index: {self.index}, old: {position}, new: {new}")
        return new
    
    def wrap_interval(self, value, min, max):
        if value < min:
            value += max - min
        if value > max:
            value -= max - min
        return value
    
    def wrap(self, position, dimensions):
        new = np.array(
            [self.wrap_interval(position[0], 0, dimensions[0]), 
             self.wrap_interval(position[1], 0, dimensions[1])])
        #print(f"snap: index: {self.index}, old: {position}, new: {new}")
        return new

    def to_hashable(self):
        return (*self.top_left(self.position), self.flock.boid_size, self.flock.boid_size)

    @staticmethod
    def clockwise_angle(v):
        j = np.array([0, 1])
        
        dot_product = np.dot(j, v)
        magnitude_v = np.linalg.norm(v)
        angle = np.arccos(dot_product / magnitude_v)
    
        # Determine if the vector v is on the left or right side of j
        if v[0] < 0:
            angle = 2*np.pi - angle
        
        return angle

    def draw_base_image(self, pygame, screen, size, color):
        radius = size//2
        center = (int(1.5 * size), int(1.5 * size))
        start = (int(1.5 * size), size*3)
        end = (int(1.5 * size), size*2)
        boid_surface = pygame.Surface((size*3, size*3), pygame.SRCALPHA)  # SRCALPHA to make background transparent
        boid_rect = boid_surface.get_rect()
        boid_rect.center = self.position
        pygame.draw.circle(boid_surface, color, center, radius, 2)
        pygame.draw.circle(boid_surface, color if not self.predated else GREEN, center, 2.0)
        pygame.draw.line(boid_surface, color, start, end, 2)   
        return boid_rect, boid_surface

    def draw(self, pygame, screen, color = None):
        if not color:
            color = self.color
        boid_rect, boid_surface = self.draw_base_image(pygame, screen, self.flock.boid_size, color)
        angle = boid.clockwise_angle(self.velocity)
        boid_rotated = pygame.transform.rotate(boid_surface, np.degrees(angle) + 180.0)
        rotated_boid_rect = boid_rotated.get_rect(center=boid_rect.center)
        screen.blit(boid_rotated, rotated_boid_rect)

    def top_left(self, position):
        top_left = position - self.flock.boid_size_vector_half
        return top_left
    
    def find_bbox(self, position):
        top_left = self.top_left(position)
        bbox = pygame.Rect(*top_left, self.flock.boid_size, self.flock.boid_size)
        return bbox

    @staticmethod
    def position_from_bbox(bbox):
        return (bbox.x + bbox.width//2, bbox.y + bbox.height//2)
    
    def random_position(self, dimensions):
        while True:
            position = self.randomise_pos(dimensions)
            bbox = self.find_bbox(position)
            potential = self.flock.sht.nearby_keys(bbox, 1.1)
            collision = any(bbox.colliderect(pygame.Rect(*self.flock.boids[index].to_hashable())) for index in potential)
            if not collision:
                break
        return position
    
    def randomise_pos(self, dimensions):
        position = np.random.normal(dimensions//2, self.flock.space_sd)
        return self.snap(position, dimensions)

    @staticmethod
    def snap_interval(value, min, max):
        if value < min:
            value = min
        if value > max:
            value = max
        return value

    
    def snap(self, position, dimensions):
        radius = self.flock.boid_size//2
        new = np.array(
            [boid.snap_interval(position[0], radius, dimensions[0] - radius), 
             boid.snap_interval(position[1], radius, dimensions[1] - radius)])
        #print(f"snap: index: {self.index}, old: {position}, new: {new}")
        return new
            

    def __str__(self):
        return f"boid: index: {self.index}, position: {self.position}, velocity: {self.velocity}"


class boid_predator(boid):
    def __init__(self, flock, index):
        super().__init__(flock, index)
        assert index == self.flock.n_boids
        self.color = YELLOW

    def draw(self, pygame, screen, color = None):
        boid.draw(self, pygame, screen, color)
        pygame.draw.circle(screen, MIDNIGHTBLUE, self.position, self.flock.predator_range, 1)

    def update(self):
        self.velocity_update = self.velocity
        self.position_update = self.position 

        # screen edge
        if self.position[0] < self.flock.margin:
            self.velocity_update[0] += self.flock.predator_turn_factor
        if self.position[0] > self.flock.field_dimensions[0] - self.flock.margin:
            self.velocity_update[0] -= self.flock.predator_turn_factor
        if self.position[1] < self.flock.margin:
            self.velocity_update[1] += self.flock.predator_turn_factor
        if self.position[1] > self.flock.field_dimensions[1] - self.flock.margin:
            self.velocity_update[1] -= self.flock.predator_turn_factor

        # speed limit
        speed_squared = np.sum(np.square(self.velocity_update))
        if speed_squared > self.flock.predator_maxspeed_squared:
            self.velocity_update *= np.sqrt(self.flock.predator_maxspeed_squared/speed_squared)
        if speed_squared < self.flock.predator_minspeed_squared:
            self.velocity_update *= np.sqrt(self.flock.predator_minspeed_squared/speed_squared)

        delta = self.flock.time_delta*self.velocity_update
        self.position_update += delta

        return (self.index, self.position_update, self.velocity_update)