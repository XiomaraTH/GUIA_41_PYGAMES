import pygame
import os
import random
import sys

pygame.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 600
VEL_BALAS = 20
VEL_ENEMIGO = 5
VEL_METEORITO = 3
MAX_ENEMIGOS = 6
MAX_METEORITOS = 4
PROB_ENEMIGO = 40
PROB_METEORITO = 30
ESPERA_ENEMIGOS = 20
ESPERA_METEORITOS = 30
SHIP_WIDTH = 60
SHIP_HEIGHT = 50

# niveles
NIVEL_MAXIMO = 10
PUNTOS_POR_NIVEL_FACIL = 10    
PUNTOS_POR_NIVEL_MEDIO = 20    
PUNTOS_POR_NIVEL_DIFICIL = 25  

# ventana
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# imágen
def cargarImagen(imagen): 
    ruta = os.path.join("sprites", imagen)
    return pygame.image.load(ruta)

# sonido
def cargarSonido(sonido): 
    ruta = os.path.join("sprites", sonido)
    return pygame.mixer.Sound(ruta)

# fuente
def crearFuente(size):
    ruta = os.path.join("sprites", "kenvector_future_thin.ttf")
    return pygame.font.Font(ruta, size)

# recursos
try:
    ICONO = cargarImagen("icon.png")
    pygame.display.set_icon(ICONO)
    
    FONDO = pygame.Surface((WIDTH, HEIGHT))
    FONDO.fill((0, 0, 0))      
    
    IMAGENES_ENEMIGOS = [
        pygame.transform.scale(cargarImagen("enemy1.png"), (SHIP_WIDTH, SHIP_HEIGHT)),
        pygame.transform.scale(cargarImagen("enemy2.png"), (SHIP_WIDTH, SHIP_HEIGHT)),
        pygame.transform.scale(cargarImagen("enemy3.png"), (SHIP_WIDTH, SHIP_HEIGHT))
    ]
    
    IMAGENES_METEORITOS = [
        cargarImagen("meteorBrown_small2.png"),
        cargarImagen("meteorBrown_med1.png")
    ]
    
    BALA_VERDE = pygame.transform.scale(cargarImagen("laserGreen.png"), (12, 25))
    BALA_AZUL = pygame.transform.scale(cargarImagen("laserBlue.png"), (12, 25))
    
    IMAGEN_EXPLOSION = cargarImagen("explosion.png")
    
    IMAGEN_JUGADOR = pygame.transform.scale(cargarImagen("playerShip.png"), (SHIP_WIDTH + 15, SHIP_HEIGHT + 15))
    
    IMAGEN_UFORED = pygame.transform.scale(cargarImagen("ufoRed.png"), (SHIP_WIDTH, SHIP_HEIGHT))
    
    sndExplosion = cargarSonido("explosion.ogg")
    sndLaser = cargarSonido("laser.ogg")
    
    FONT_MARCADOR = crearFuente(30)
    FONT_GAMEOVER = crearFuente(100)
    FONT_TITULO = crearFuente(80)
    
except Exception as e:
    print(f"Error al cargar recursos: {e}")
    print("Asegúrate de que todos los archivos estén en la carpeta 'sprites/'")
    sys.exit(1)

# sprites
enemigos = pygame.sprite.Group()
meteoritos = pygame.sprite.Group()
balasJugador = pygame.sprite.Group()
todo = pygame.sprite.Group()

# Colores
COLOR_MARCADOR = (255, 255, 255)  # Blanco
COLOR_GAMEOVER = (255, 0, 0)      # Rojo
COLOR_TITULO = (0, 255, 0)        # Verde

COLOR_BALA = "green"
VELOCIDAD_BALAS = VEL_BALAS  

nivel_actual = 1
puntos_nivel = 0

# Grupo para el ufoRed
ufos = pygame.sprite.Group()

# dificultad
def calcular_dificultad(nivel):
    """Calcula la dificultad del juego según el nivel actual"""
    if nivel <= 3:  
        factor_nivel = nivel - 1  
        return {
            'vel_enemigo': max(VEL_ENEMIGO - 2, 1),  
            'vel_meteorito': max(VEL_METEORITO - 1, 1),  
            'max_enemigos': 3 + factor_nivel,  
            'max_meteoritos': 2 + factor_nivel, 
            'prob_enemigo': 20 + (factor_nivel * 10), 
            'prob_meteorito': 15 + (factor_nivel * 5), 
            'espera_enemigos': ESPERA_ENEMIGOS + (factor_nivel * 5), 
            'espera_meteoritos': ESPERA_METEORITOS + (factor_nivel * 5),
            'puntos_por_nivel': PUNTOS_POR_NIVEL_FACIL  
        }
    elif nivel <= 5:  # Niveles medios (4-5) - Un poco más rápido que el nivel fácil
        factor_nivel = nivel - 3  # 1, 2 para niveles 4, 5
        return {
            'vel_enemigo': VEL_ENEMIGO - 1,  # Un poco más rápido que el nivel fácil
            'vel_meteorito': VEL_METEORITO,  # Velocidad base
            'max_enemigos': 6 + factor_nivel,  # 7, 8 enemigos
            'max_meteoritos': 5 + factor_nivel,  # 6, 7 meteoritos
            'prob_enemigo': 50 + (factor_nivel * 10),  # 60%, 70%
            'prob_meteorito': 30 + (factor_nivel * 5),  # 35%, 40%
            'espera_enemigos': max(ESPERA_ENEMIGOS - 5 - factor_nivel, 10),
            'espera_meteoritos': max(ESPERA_METEORITOS - 5 - factor_nivel, 15),
            'puntos_por_nivel': PUNTOS_POR_NIVEL_MEDIO  # 20 enemigos para subir
        }
    else:  # Niveles difíciles (6-10) - Rápido
        factor_dificultad = min(nivel - 5, 5)  # Máximo factor 5
        return {
            'vel_enemigo': VEL_ENEMIGO + 2 + factor_dificultad,  # Más rápido
            'vel_meteorito': VEL_METEORITO + 1 + factor_dificultad,  # Más rápido
            'max_enemigos': 9 + factor_dificultad,  # 10-14 enemigos
            'max_meteoritos': 8 + factor_dificultad,  # 9-13 meteoritos
            'prob_enemigo': 80 + (factor_dificultad * 5),  # 85-105%
            'prob_meteorito': 45 + (factor_dificultad * 5),  # 50-70%
            'espera_enemigos': max(ESPERA_ENEMIGOS - 10 - factor_dificultad, 5),
            'espera_meteoritos': max(ESPERA_METEORITOS - 10 - factor_dificultad, 10),
            'puntos_por_nivel': PUNTOS_POR_NIVEL_DIFICIL  # 25 enemigos para subir
        }

# Clase Jugador
class Jugador(pygame.sprite.Sprite): 
    def __init__(self, *groups):
        super().__init__(*groups)
        # Usar imagen pre-cargada para mejor rendimiento
        self.image = IMAGEN_JUGADOR
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.add(todo)

# Clase Enemigo
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, dificultad):
        super().__init__()
        # Usar imagen pre-escalada para mejor rendimiento
        self.image = random.choice(IMAGENES_ENEMIGOS)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width) 
        self.rect.y = -self.rect.height 
        self.velx = random.choice([-dificultad['vel_enemigo'], 0, dificultad['vel_enemigo']]) 
        self.velocidad_y = dificultad['vel_enemigo']
        self.add(enemigos, todo)
    
    def update(self):
        self.rect.x += self.velx
        self.rect.y += self.velocidad_y
        if self.rect.left < 0:
            self.rect.left = 0
            self.velx = -self.velx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velx = -self.velx
        if self.rect.y > HEIGHT:
            self.kill()

# Clase Meteorito
class Meteorito(pygame.sprite.Sprite):
    def __init__(self, dificultad):
        super().__init__()
        meteor = random.choice(IMAGENES_METEORITOS)
        self.original_image = meteor
        size = random.randint(30, 45)  # Meteoritos un poco más grandes
        self.original_image = pygame.transform.scale(self.original_image, (size, size))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.vely = random.randint(dificultad['vel_meteorito'], dificultad['vel_meteorito'] + 2)
        self.velx = random.choice([-2, -1, 0, 1, 2])
        self.angle = 0
        self.add(meteoritos, todo)
    
    def update(self):
        self.rect.x += self.velx
        self.rect.y += self.vely
        # Optimizar rotación: rotar la imagen original y mantener el rectángulo
        self.angle = (self.angle + 2) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Mantener la posición del rectángulo sin recalcular el centro
        if self.rect.left < 0:
            self.rect.left = 0
            self.velx = abs(self.velx)
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velx = -abs(self.velx)
        if self.rect.y > HEIGHT:
            self.kill()

# Clase UfoRed
class UfoRed(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Usar imagen pre-cargada para mejor rendimiento
        self.image = IMAGEN_UFORED
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width  # Aparece desde la izquierda
        self.rect.y = random.randint(30, HEIGHT // 2)
        self.velx = random.randint(3, 6)
        self.add(ufos, todo)
    
    def update(self):
        self.rect.x += self.velx
        if self.rect.left > WIDTH:
            self.kill()

# Función optimizada para obtener imagen de bala
def get_bala_image():
    if COLOR_BALA == "blue":
        return BALA_AZUL
    else:
        return BALA_VERDE

class BalaJugador(pygame.sprite.Sprite):
    def __init__(self, nave):
        super().__init__()
        # Usar imagen pre-cargada para mejor rendimiento
        self.image = get_bala_image()
        self.rect = self.image.get_rect()
        self.rect.midbottom = nave.rect.midtop
        self.add(balasJugador, todo)
        sndLaser.play()
    
    def update(self):
        self.rect.y -= int(VELOCIDAD_BALAS)
        if self.rect.bottom < 0:
            self.kill()

# Clase Explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()
        # Usar imagen pre-cargada para mejor rendimiento
        self.image = IMAGEN_EXPLOSION
        self.rect = self.image.get_rect()
        self.rect.center = sprite.rect.center
        self.paso = 10
        self.add(todo)
        sndExplosion.play()
    
    def update(self):
        self.paso -= 1
        if self.paso == 0:
            self.kill()

# Clase Marcador
class Marcador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.puntos = 0
        self.nivel = 1
        self.puntos_nivel = 0
        self.actualizarTexto()
        self.add(todo)
    
    def update(self):
        pass
    
    def aumenta(self):
        global nivel_actual, puntos_nivel
        self.puntos += 1
        self.puntos_nivel += 1
        puntos_nivel = self.puntos_nivel
        
        # Obtener puntos necesarios para el nivel actual
        dificultad = calcular_dificultad(self.nivel)
        puntos_necesarios = dificultad['puntos_por_nivel']
        
        # Verificar si sube de nivel
        if self.puntos_nivel >= puntos_necesarios and self.nivel < NIVEL_MAXIMO:
            self.nivel += 1
            self.puntos_nivel = 0
            nivel_actual = self.nivel
            self.actualizarTexto()
            return True  # Indica que subió de nivel
        else:
            self.actualizarTexto()
            return False
    
    def actualizarTexto(self):
        # Obtener puntos necesarios para el nivel actual
        dificultad = calcular_dificultad(self.nivel)
        puntos_necesarios = dificultad['puntos_por_nivel']
        
        # Mostrar puntos totales y nivel actual
        texto_puntos = f"Puntos: {self.puntos}"
        texto_nivel = f"Nivel: {self.nivel}"
        texto_progreso = f"Progreso: {self.puntos_nivel}/{puntos_necesarios}"
        
        # Crear superficie combinada
        superficie = pygame.Surface((200, 80))
        superficie.fill((0, 0, 0))  # Fondo negro
        
        # Renderizar textos
        texto_puntos_surf = FONT_MARCADOR.render(texto_puntos, False, COLOR_MARCADOR)
        texto_nivel_surf = FONT_MARCADOR.render(texto_nivel, False, (0, 255, 0))  # Verde para nivel
        texto_progreso_surf = FONT_MARCADOR.render(texto_progreso, False, (255, 255, 0))  # Amarillo para progreso
        
        # Posicionar textos
        superficie.blit(texto_puntos_surf, (0, 0))
        superficie.blit(texto_nivel_surf, (0, 25))
        superficie.blit(texto_progreso_surf, (0, 50))
        
        self.image = superficie
        self.rect = self.image.get_rect()
        self.rect.topright = (WIDTH-10, 10)

# Función para detectar colisiones
def detectarColisiones(nave):
    subio_nivel = False
    
    # Colisiones entre balas y enemigos - usar detección más precisa
    enemigos_tocados = pygame.sprite.groupcollide(enemigos, balasJugador, True, True, pygame.sprite.collide_mask)
    for enemigo, balas in enemigos_tocados.items():
        Explosion(enemigo)
        if marcador.aumenta():  # Verificar si subió de nivel
            subio_nivel = True
    
    # Colisiones entre balas y meteoritos - usar detección más precisa
    meteoritos_tocados = pygame.sprite.groupcollide(meteoritos, balasJugador, True, True, pygame.sprite.collide_mask)
    for meteorito, balas in meteoritos_tocados.items():
        Explosion(meteorito)
        if marcador.aumenta():  # Verificar si subió de nivel
            subio_nivel = True
    
    return subio_nivel
    
    muerte = False
    if nave in todo:
        # Colisión con enemigos - usar detección más precisa
        enemigos_chocan = pygame.sprite.spritecollide(nave, enemigos, True, pygame.sprite.collide_mask)
        for enemigo in enemigos_chocan:
            Explosion(enemigo)
            Explosion(nave)
            nave.kill()
            muerte = True
        
        # Colisión con meteoritos
        meteoritos_chocan = pygame.sprite.spritecollide(nave, meteoritos, True, pygame.sprite.collide_mask)
        for meteorito in meteoritos_chocan:
            Explosion(meteorito)
            Explosion(nave)
            nave.kill()
            muerte = True
    
    return muerte

# Función para mostrar game over
def gameover():
    gameover_text = FONT_GAMEOVER.render("GAME OVER", False, COLOR_GAMEOVER)
    rect = gameover_text.get_rect()
    rect.center = (WIDTH // 2, HEIGHT // 2)
    WIN.blit(gameover_text, rect)
    pygame.display.update()

# Función para mostrar subida de nivel y reiniciar el juego
def mostrar_subida_nivel(nivel):
    WIN.blit(FONDO, (0, 0))
    todo.draw(WIN)
    
    # Texto de subida de nivel
    nivel_text = FONT_TITULO.render(f"NIVEL {nivel}", False, (0, 255, 255))  # Cyan
    rect_nivel = nivel_text.get_rect()
    rect_nivel.center = (WIDTH // 2, HEIGHT // 2 - 50)
    
    # Texto de dificultad
    if nivel <= 3:
        dificultad_text = FONT_MARCADOR.render("DIFICULTAD: FÁCIL", False, (0, 255, 0))  # Verde
    elif nivel <= 5:
        dificultad_text = FONT_MARCADOR.render("DIFICULTAD: MEDIA", False, (255, 255, 0))  # Amarillo
    else:
        dificultad_text = FONT_MARCADOR.render("DIFICULTAD: DIFÍCIL", False, (255, 0, 0))  # Rojo
    
    rect_dificultad = dificultad_text.get_rect()
    rect_dificultad.center = (WIDTH // 2, HEIGHT // 2 + 50)
    
    WIN.blit(nivel_text, rect_nivel)
    WIN.blit(dificultad_text, rect_dificultad)
    pygame.display.update()
    pygame.time.delay(2000)  # Mostrar por 2 segundos
    
    # Reiniciar el juego como al inicio (manteniendo nivel y puntos)
    reiniciar_para_nuevo_nivel()
    
    # Mostrar mensaje de "¡PREPÁRATE!"
    WIN.blit(FONDO, (0, 0))
    preparate_text = FONT_TITULO.render("¡PREPÁRATE!", False, (255, 255, 0))  # Amarillo
    rect_preparate = preparate_text.get_rect()
    rect_preparate.center = (WIDTH // 2, HEIGHT // 2)
    WIN.blit(preparate_text, rect_preparate)
    pygame.display.update()
    pygame.time.delay(1500)  # Mostrar por 1.5 segundos

# Función para mostrar título
def mostrarTitulo(nave):
    WIN.blit(FONDO, (0, 0))
    if nave and nave.image:
        WIN.blit(nave.image, nave.rect)
    titulo = FONT_TITULO.render("SPACE SHOOTER", False, COLOR_TITULO)
    rect = titulo.get_rect()
    rect.center = (WIDTH // 2, HEIGHT // 2)
    WIN.blit(titulo, rect)
    pygame.display.update()
    pygame.time.delay(3000)

# Función para dibujar optimizada
def dibuja():
    WIN.blit(FONDO, (0, 0))
    todo.draw(WIN)
    pygame.display.flip()  # Más eficiente que update() para pantalla completa

# Función para reiniciar para nuevo nivel (mantiene nivel y puntos)
def reiniciar_para_nuevo_nivel():
    global nave
    # Limpiar todos los sprites excepto el marcador
    enemigos.empty()
    meteoritos.empty()
    balasJugador.empty()
    ufos.empty()
    
    # Remover nave del grupo todo si existe
    if nave in todo:
        nave.remove(todo)
    
    # Crear nueva nave en posición inicial
    nave = Jugador()
    
    # Resetear color y velocidad de balas
    global COLOR_BALA, VELOCIDAD_BALAS
    COLOR_BALA = "green"
    VELOCIDAD_BALAS = VEL_BALAS
    
    # Mostrar pantalla limpia por un momento
    WIN.blit(FONDO, (0, 0))
    todo.draw(WIN)
    pygame.display.flip()
    pygame.time.delay(1000)  # Pausa de 1 segundo para mostrar pantalla limpia

# Función para reiniciar (game over completo)
def reinicio():
    global nave, marcador, nivel_actual, puntos_nivel
    gameover()
    pygame.time.delay(2000)
    todo.empty()
    enemigos.empty()
    meteoritos.empty()
    balasJugador.empty()
    ufos.empty()
    nave = Jugador()
    marcador = Marcador()
    nivel_actual = 1
    puntos_nivel = 0

# Función principal optimizada
def main():
    global nave, marcador, esperaMeteorito, COLOR_BALA, VELOCIDAD_BALAS, nivel_actual
    
    nave = Jugador()
    marcador = Marcador()
    
    jugando = True
    esperaEnemigo = 0
    esperaMeteorito = 0
    esperaUfo = random.randint(200, 400)  # frames para el próximo ufo (más frecuente)
    reloj = pygame.time.Clock()
    
    mostrarTitulo(nave)
    
    # Optimización: cachear valores frecuentemente usados
    VELOCIDAD_MOVIMIENTO = 5
    
    while jugando:
        # Obtener dificultad actual
        dificultad = calcular_dificultad(nivel_actual)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jugando = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    BalaJugador(nave)
                elif event.key == pygame.K_ESCAPE:
                    jugando = False
        
        teclas = pygame.key.get_pressed()
        # Optimización: usar variables locales para reducir acceso a atributos
        nave_rect = nave.rect
        if teclas[pygame.K_LEFT] and nave_rect.left > 0:
            nave_rect.x -= VELOCIDAD_MOVIMIENTO
        if teclas[pygame.K_RIGHT] and nave_rect.right < WIDTH:
            nave_rect.x += VELOCIDAD_MOVIMIENTO
        if teclas[pygame.K_UP] and nave_rect.top > 0:
            nave_rect.y -= VELOCIDAD_MOVIMIENTO
        if teclas[pygame.K_DOWN] and nave_rect.bottom < HEIGHT:
            nave_rect.y += VELOCIDAD_MOVIMIENTO
        
        # Generar enemigos con dificultad dinámica
        if esperaEnemigo == 0 and len(enemigos) < dificultad['max_enemigos']:
            if random.uniform(0, 100) < dificultad['prob_enemigo']:
                Enemigo(dificultad)
                esperaEnemigo = dificultad['espera_enemigos']
        elif esperaEnemigo > 0:
            esperaEnemigo -= 1
        
        # Generar meteoritos con dificultad dinámica
        if esperaMeteorito == 0 and len(meteoritos) < dificultad['max_meteoritos']:
            if random.uniform(0, 100) < dificultad['prob_meteorito']:
                Meteorito(dificultad)
                esperaMeteorito = dificultad['espera_meteoritos']
        elif esperaMeteorito > 0:
            esperaMeteorito -= 1
        
        # Generar ufoRed
        if esperaUfo == 0 and len(ufos) == 0:
            UfoRed()
            esperaUfo = random.randint(300, 600)  # Próxima aparición más frecuente
        elif esperaUfo > 0:
            esperaUfo -= 1
        
        # Actualizar sprites
        todo.update()
        
        # Colisión nave-ufoRed
        if nave in todo:
            ufos_chocados = pygame.sprite.spritecollide(nave, ufos, True, pygame.sprite.collide_mask)
            if ufos_chocados:
                COLOR_BALA = "blue"
                VELOCIDAD_BALAS = VEL_BALAS * 1.5  # Aumentar velocidad en 50%
        
        # Detectar colisiones
        subio_nivel = detectarColisiones(nave)
        if subio_nivel:
            mostrar_subida_nivel(nivel_actual)
            # Después de reiniciar, esperar un poco antes de que aparezcan nuevos enemigos
            esperaEnemigo = 60  # 1 segundo de espera
            esperaMeteorito = 90  # 1.5 segundos de espera
        
        muerte = False
        if nave in todo:
            # Colisión con enemigos - usar detección más precisa
            enemigos_chocan = pygame.sprite.spritecollide(nave, enemigos, True, pygame.sprite.collide_mask)
            for enemigo in enemigos_chocan:
                Explosion(enemigo)
                Explosion(nave)
                nave.kill()
                muerte = True
            
            # Colisión con meteoritos
            meteoritos_chocan = pygame.sprite.spritecollide(nave, meteoritos, True, pygame.sprite.collide_mask)
            for meteorito in meteoritos_chocan:
                Explosion(meteorito)
                Explosion(nave)
                nave.kill()
                muerte = True
        

        
        if muerte:
            COLOR_BALA = "green"  # Resetear color de balas al reiniciar
            VELOCIDAD_BALAS = VEL_BALAS  # Resetear velocidad al reiniciar
            reinicio()
        
        dibuja()
        reloj.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 