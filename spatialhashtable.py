# import logging
# 
# logging.basicConfig(filename='spatialhashtable.log',
                    # filemode='w',
                    # format='%(levelname)s:%(message)s',
                    # level=logging.INFO)
# 
# logger = logging.getLogger(__name__)

import numpy as np
import pygame
from functools import lru_cache
from my_colors import *

class spatialhashtable:
    def __init__(self, cell_size):
        self.flock = None
        self.ENLARGE_FACTOR = 1.1
        self.cell_size = cell_size
        self.table = {}
        self.search_box_vector = np.array([cell_size, cell_size])
        self.search_box_vector_times_two = 2.0 * self.search_box_vector
        self.search_box = pygame.Rect(np.array([0.0, 0.0]), self.search_box_vector_times_two)

    def set_cell_size(self, value):
        self.cell_size = value
        
    def reset(self):
        self.table = {}
        
    def draw_table(self, pygame, screen):
        #logging.debug(f"draw_table: self.table: {self.table}")
        for key, value in self.table.items():
            if not len(value) == 0:
                x_min, y_min = key[0]*self.cell_size, key[1]*self.cell_size
                x_max, y_max = (key[0] + 1) * self.cell_size, (key[1] + 1) * self.cell_size
                square_rect = pygame.Rect((x_min, y_min), (x_max - x_min, y_max - y_min))
                pygame.draw.rect(screen, BLUE, square_rect, width=1)
            
    def hash_pos(self, x, y):
        return int(x / self.cell_size), int(y / self.cell_size)

    #@lru_cache(maxsize=None)  # Unlimited cache
    def get_bins_from_hashed_corners(self, x_min_hash, y_min_hash, x_max_hash, y_max_hash):
        #logging.debug(f'x_min_hash: {x_min_hash}, y_min_hash: {y_min_hash}, x_min_hash: {x_min_hash}, y_min_hash: {y_min_hash}')
        bins = {(x, y) for x in range(x_min_hash, x_max_hash + 1) 
                          for y in range(y_min_hash, y_max_hash + 1)}
        return bins
        
    def bins(self, x_min, y_min, x_max, y_max):
        x_min_hash, y_min_hash = self.hash_pos(x_min, y_min)
        x_max_hash, y_max_hash = self.hash_pos(x_max, y_max)
        #logging.debug(f'x_min_hash: {x_min_hash}, y_min_hash: {y_min_hash}, x_min_hash: {x_min_hash}, y_min_hash: {y_min_hash}')
        bins = self.get_bins_from_hashed_corners(x_min_hash, y_min_hash, x_max_hash, y_max_hash)
        #logging.debug(f"bins leave: bins: {bins}")
        return bins

    def draw_bins(self, pygame, screen, bins, color = BLUE):
        #logging.debug(f"draw_table: self.table: {self.table}")
        for bin in bins:
            x_min, y_min = bin[0]*self.cell_size, bin[1]*self.cell_size
            square_rect = pygame.Rect((x_min, y_min), (self.cell_size, self.cell_size))
            pygame.draw.rect(screen, color, square_rect, width=1)
    
    def insert(self, obj):
        #logging.debug(f"insert enter: obj: {obj}")
        obj.bin = self.hash_pos(*obj.position)
        bbox = obj.find_bbox(obj.position)
        x_min, y_min = bbox.topleft
        x_max, y_max = bbox.bottomright
        bins = self.bins( x_min, y_min, x_max, y_max)
        #logging.debug(f"insert: bins: {bins}")
        for bin in bins:
            if bin not in self.table:
                #logging.debug(f"insert: setting self.table[{h}]")
                self.table[bin] = set()
            self.table[bin].add(obj.index)
            obj.bins.add(bin)

    def remove(self, obj):
        for bin in obj.bins:
            self.table[bin].remove(obj.index)
        obj.bins = set()

    def expand_interval(self, a, b, f):
        if not a <= b:
            logging.error(f"should have a <= b, a: {a}, b: {b}")
        width = b - a
        extra = (width * (f - 1.0))/2.0
        return a - extra, b + extra
         
    def nearby_keys(self, bbox, enlargment):
        #logging.debug(f"nearby_keys:enter: bbox: {bbox}")
        potential = set()

        # Assuming bbox is a pygame Rect object
        # Get the top-left and bottom-right corners
        x_min, y_min = bbox.topleft
        x_max, y_max = bbox.bottomright
        #logging.debug(f'nearby_keys: x_min: {x_min}, y_min: {y_min}, x_min: {x_min}, y_min: {y_min}')
        if not enlargment == 0.0:
            x_min, x_max = self.expand_interval(x_min, x_max, enlargment)
            y_min, y_max = self.expand_interval(y_min, y_max, enlargment)  
        #logging.debug(f'nearby_keys: x_min: {x_min}, y_min: {y_min}, x_min: {x_min}, y_min: {y_min}')
        bins = self.bins(x_min, y_min, x_max, y_max)
        #logging.debug(f"nearby_keys: bins: {bins}")
        for bin in bins:
            if bin in self.table:
                #logging.debug(f"nearby_keys: self.table[{bin}]:{self.table[bin]}")
                if not len(self.table[bin]) == 0:
                    potential |= self.table[bin]
        #logging.debug(f"nearby_keys:leave: potential: {potential}")
        return potential

    def nearest(self, x, y):
        index = 0
        f = self.flock
        click_position = np.array([x, y])
        self.search_box.topleft = click_position - self.search_box_vector
        potential = self.nearby_keys(self.search_box, 0.0)
        if not len(potential) == 0:
            potential_list = [(np.sum(np.abs (f.boids[index].position - click_position)), index) for index in potential]
            sorted_list = sorted(potential_list, key=lambda x: x[0])
            index = sorted_list[0][1]
        return index

