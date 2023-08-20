import pygame
from pygame.locals import *
from my_colors import *

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_value, label, label_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value
        self.label = label
        self.font = pygame.font.SysFont(None, 25)
        self.slider_width = 20
        self.slider_pos = ((initial_value - min_val) / (max_val - min_val)) * (width - self.slider_width)
        self.dragging = False
        self.color = label_color

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            return self.value
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            x = event.pos[0] - self.rect.x - self.slider_width/2
            x = max(0, min(x, self.rect.width - self.slider_width))
            self.slider_pos = x
            self.value = self.min_val + (x / (self.rect.width - self.slider_width)) * (self.max_val - self.min_val)
            return self.value
            
    def get_value(self):
        return self.value
        
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, DARKGRAY, (self.rect.x + self.slider_pos, self.rect.y, self.slider_width, self.rect.height))
        
        # Display the label
        label_surface = self.font.render(self.label, True, self.color)
        screen.blit(label_surface, (self.rect.x, self.rect.y - self.rect.height))
        
        # Display the current value
        value_surface = self.font.render(str(int(self.value * 10)/10), True, self.color)
        screen.blit(value_surface, (self.rect.x + self.rect.width  - self.rect.height, self.rect.y - self.rect.height))

if __name__ == "__main__":
    screen = pygame.display.set_mode((500, 300))
    pygame.display.set_caption("Slider with Label and Value in Pygame")
    
    slider = Slider(120, 100, 300, 30, 0, 100, 50, "Volume:")
    
    running = True
    while running:
        screen.fill(WHITE)
    
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            slider.handle_event(event)
    
        slider.draw(screen)
        pygame.display.flip()
    
    pygame.quit()
