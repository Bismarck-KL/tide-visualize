import pygame

class LoadingScreen:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(None, 16)
        self.width = width
        self.height = height

    def show_message(self, message):
        self.screen.fill((0, 0, 0))  # Black background
        text = self.font.render(message, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(self.width/2, self.height/2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()