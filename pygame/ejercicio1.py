import pygame
# Inicialización de Pygame
pygame.init()
# Inicialización de la superficie de dibujo
ventana = pygame.display.set_mode((640,480))
pygame.display.set_caption("Ejercicio 1")
# Bucle principal del juego
jugando = True
while jugando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jugando = False
# Se pinta la ventana con un color
# Esto borra los posibles elementos que teníamos anteriormente
ventana.fill((255, 255, 255))
# Todos los elementos del juego se vuelven a dibujar
pygame.display.flip()
# Controlamos la frecuencia de refresco (FPS)
pygame.time.Clock().tick(60)
pygame.quit()