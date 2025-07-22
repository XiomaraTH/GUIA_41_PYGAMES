import pygame
import random
import os

# Inicialización
pygame.init()
ventana = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Ejercicio 3 - Space Breakout")

# Obtener el directorio del script para cargar imágenes
script_dir = os.path.dirname(os.path.abspath(__file__))
sprites_dir = os.path.join(os.path.dirname(script_dir), "sprites")

# Pelota
ball = pygame.image.load(os.path.join(script_dir, "ball.png"))
ballrect = ball.get_rect()
speed_x = random.choice([-1, 1]) * random.randint(4, 8)
speed_y = random.choice([-1, 1]) * random.randint(4, 8)
speed = [speed_x, speed_y]
ballrect.move_ip(0, 0)

# Fondo estrellado
try:
    stars_bg = pygame.image.load(os.path.join(sprites_dir, "stars.png"))
    stars_bg = pygame.transform.scale(stars_bg, (640, 480))
except:
    stars_bg = None

# Bate (nave espacial)
try:
    bate_img = pygame.image.load(os.path.join(sprites_dir, "playerShip.png"))
    bate_img = pygame.transform.scale(bate_img, (100, 40))
except:
    bate_img = None

bate_ancho = 100
bate_alto = 15
bate_color = (70, 130, 180)
bate = pygame.Rect(
    (ventana.get_width() // 2 - bate_ancho // 2, ventana.get_height() - 40),
    (bate_ancho, bate_alto)
)
bate_speed = 8
bate_acceleration = 0.5
bate_max_speed = 20
bate_current_speed = bate_speed

# Ladrillos con colores más vibrantes
ladrillo_colores = [
    (255, 182, 193),  # Rosa claro
    (255, 105, 180),  # Rosa caliente
    (219, 112, 147),  # Rosa pálido
    (255, 20, 147),   # Rosa profundo
    (199, 21, 133),   # Rosa medio
    (255, 192, 203),  # Rosa suave
]
ladrillo_ancho = 60
ladrillo_alto = 20
ladrillos = []
ladrillos_colores = []  # Lista separada para los colores
ladrillos_filas = 4
ladrillos_columnas = 8
ladrillos_espacio = 10

for fila in range(ladrillos_filas):
    for col in range(ladrillos_columnas):
        x = col * (ladrillo_ancho + ladrillos_espacio) + 35
        y = fila * (ladrillo_alto + ladrillos_espacio) + 40
        ladrillo = pygame.Rect(x, y, ladrillo_ancho, ladrillo_alto)
        ladrillos.append(ladrillo)
        ladrillos_colores.append(ladrillo_colores[fila % len(ladrillo_colores)])

# Game Over
game_over = False
font = pygame.font.SysFont(None, 60)
ganaste = False

# Aceleración de la bola
aceleracion_intervalo = 4000  # ms
ultimo_aceleracion = pygame.time.get_ticks()
aceleracion_factor = 1.1

jugando = True

# Función para reiniciar juego
def reiniciar_juego():
    global ballrect, speed, bate, bate_current_speed, ladrillos, game_over, ganaste, ultimo_aceleracion
    # Reposicionar bate
    bate.x = ventana.get_width() // 2 - bate.width // 2
    bate.y = ventana.get_height() - 40
    bate_current_speed = bate_speed

    # Reposicionar pelota
    ballrect.x = bate.x + bate.width // 2 - ballrect.width // 2
    ballrect.y = bate.y - ballrect.height
    speed[0] = random.choice([-1, 1]) * random.randint(4, 8)
    speed[1] = -random.randint(4, 8)

    # Reiniciar ladrillos
    ladrillos.clear()
    ladrillos_colores.clear() # Limpiar colores
    for fila in range(ladrillos_filas):
        for col in range(ladrillos_columnas):
            x = col * (ladrillo_ancho + ladrillos_espacio) + 35
            y = fila * (ladrillo_alto + ladrillos_espacio) + 40
            ladrillo = pygame.Rect(x, y, ladrillo_ancho, ladrillo_alto)
            ladrillos.append(ladrillo)
            ladrillos_colores.append(ladrillo_colores[fila % len(ladrillo_colores)])

    # Reiniciar estado
    game_over = False
    ganaste = False
    ultimo_aceleracion = pygame.time.get_ticks()

# Bucle principal
clock = pygame.time.Clock()
while jugando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jugando = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reiniciar_juego()

    if not game_over and not ganaste:
        # Movimiento del bate
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and bate.left > 0:
            bate_current_speed = min(bate_current_speed + bate_acceleration, bate_max_speed)
            bate.x -= int(bate_current_speed)
        elif keys[pygame.K_RIGHT] and bate.right < ventana.get_width():
            bate_current_speed = min(bate_current_speed + bate_acceleration, bate_max_speed)
            bate.x += int(bate_current_speed)
        else:
            bate_current_speed = bate_speed

        # Aceleración de la bola
        ahora = pygame.time.get_ticks()
        if ahora - ultimo_aceleracion > aceleracion_intervalo:
            speed[0] = int(speed[0] * aceleracion_factor) or random.choice([-1, 1])
            speed[1] = int(speed[1] * aceleracion_factor) or random.choice([-1, 1])
            ultimo_aceleracion = ahora

        # Movimiento de pelota
        ballrect = ballrect.move(speed)

        # Rebote en bordes
        if ballrect.left < 0 or ballrect.right > ventana.get_width():
            speed[0] = -speed[0] + random.choice([-1, 0, 1])
        if ballrect.top < 0:
            speed[1] = -speed[1] + random.choice([-1, 0, 1])

        # Rebote con bate
        if ballrect.colliderect(bate) and speed[1] > 0:
            speed[1] = -speed[1] + random.choice([-1, 0, 1])
            offset = (ballrect.centerx - bate.centerx) / (bate.width // 2)
            speed[0] += int(offset * 3)

        # Colisión con ladrillos
        for i, ladrillo in enumerate(ladrillos[:]):
            if ballrect.colliderect(ladrillo):
                ladrillos.remove(ladrillo)
                ladrillos_colores.pop(i)  # Eliminar el color correspondiente
                speed[1] = -speed[1] + random.choice([-1, 0, 1])
                break

        # Verificar condiciones de fin
        if ballrect.bottom > ventana.get_height():
            game_over = True
        if not ladrillos:
            ganaste = True

    # Dibujar elementos
    # Fondo estrellado o color sólido
    if stars_bg:
        ventana.blit(stars_bg, (0, 0))
    else:
        ventana.fill((10, 10, 30))  # Azul oscuro como fondo espacial
    
    # Dibujar ladrillos con colores
    for i, ladrillo in enumerate(ladrillos):
        pygame.draw.rect(ventana, ladrillos_colores[i], ladrillo)
        # Borde brillante para los ladrillos
        pygame.draw.rect(ventana, (255, 255, 255), ladrillo, 2)
    
    # Dibujar pelota
    ventana.blit(ball, ballrect)
    
    # Dibujar bate (nave espacial o rectángulo)
    if bate_img:
        ventana.blit(bate_img, bate)
    else:
        pygame.draw.rect(ventana, bate_color, bate)

    if game_over:
        texto = font.render("Game Over", True, (200, 30, 30))
        ventana.blit(texto, (
            ventana.get_width() // 2 - texto.get_width() // 2,
            ventana.get_height() // 2 - texto.get_height() // 2
        ))

    if ganaste:
        texto = font.render("¡Ganaste!", True, (30, 200, 30))
        ventana.blit(texto, (
            ventana.get_width() // 2 - texto.get_width() // 2,
            ventana.get_height() // 2 - texto.get_height() // 2
        ))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()