import pygame

pygame.init()

gameDisplay = pygame.display.set_mode((800,600))
pygame.display.set_caption("Test")

gameExit= False
while not gameExit:
    for event in pygame.event.get():
        print(event)