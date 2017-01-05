import pygame
import random
import time

WIDTH = 640
HEIGHT = 400
FPS = 5

clock = pygame.time.Clock()
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))

while True:
  for event in pygame.event.get(): #check if we need to exit
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

  surface.fill((0, 0, 0))


  amt = random.random()
  rect = (WIDTH*amt, 0, WIDTH*amt, amt*HEIGHT)
  pygame.draw.rect(surface, (255, 0, 0), rect)

  pygame.display.update()
  clock.tick(FPS)

# https://www.panda3d.org/forums/viewtopic.php?t=13008

