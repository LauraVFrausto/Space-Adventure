import pygame
from random import randint
from time import time, sleep

ventana_pixeles = 600
fps = 60
fondo_negro = (0, 0, 0)
color_blanco = (255, 255, 255)
cantidad_asteroides = 30
cantidad_balas = 3


class Entidad:
    def __init__(self, x, y, radio, velocidad):
        self.x = x
        self.y = y
        self.radio = radio
        self.velocidad = velocidad

    def actualizar(self):
        self.y += self.velocidad

    def es_colision(self, entidad):
        return (self.radio + entidad.radio
                ) ** 2 >= (self.x - entidad.x) ** 2 + (self.y - entidad.y) ** 2


class Asteroide(Entidad):
    def __init__(self):
        Entidad.__init__(self, -20, 580, 16, 2)
        self.imagen = pygame.image.load("asteroid.png")

    def spawn(self, otros_asteroides=[]):
        self.y = randint(0, ventana_pixeles) * -1
        self.x = randint(self.radio, ventana_pixeles - self.radio)
        while sum(self.es_colision(asteroide) for asteroide in otros_asteroides) > 1:
            self.spawn(otros_asteroides)
    
    def asteroide_caido(self, otros_asteroides):
        if self.y >= ventana_pixeles:
            self.spawn(otros_asteroides)

    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x - self.radio, self.y - self.radio, self.radio, self.radio))


class Bala(Entidad):
    def __init__(self):
        Entidad.__init__(self, -20, 0, 12, -2)
        self.fue_disparada = False
        self.imagen = pygame.image.load("bullet.png")

    def disparar(self, nave):
        self.x = nave.x
        self.y = nave.y - nave.radio

    def actualizar(self):
        if self.fue_disparada:
            Entidad.actualizar(self)
            if self.y < 0:
                self.fue_disparada = False
                self.x = -20

    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x - self.radio, self.y - self.radio, self.radio, self.radio))


class Nave(Entidad):
    def __init__(self):
        Entidad.__init__(self, ventana_pixeles // 2, ventana_pixeles * (3 / 4),
                         16, 2)
        self.vidas = 3
        self.imagen = pygame.image.load("nave.png")

    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x - self.radio, self.y - self.radio, self.radio, self.radio))


def main():
    asteroides = [Asteroide() for _ in range(cantidad_asteroides)]
    nave = Nave()
    balas = [Bala() for _ in range(cantidad_balas)]
    pygame.init()

    reloj = pygame.time.Clock()
    pygame.key.set_repeat(10, 10)
    ventana = pygame.display.set_mode((ventana_pixeles, ventana_pixeles))

    tiempo = time()
    corriendo = True
    pause_balas = 0
    pause_vidas = 0
    gameOver = pygame.image.load("game_over.png").convert()
    gameOver = pygame.transform.scale(gameOver, (600, 600))
    
    vida = pygame.image.load("corazon.png")
    vida = pygame.transform.scale(vida, (30, 30))

    puntaje = 0

    while corriendo:
        ventana.fill(fondo_negro)

        x_inicial_vidas = 570
        for _ in range(nave.vidas):
            ventana.blit(vida, (x_inicial_vidas, 0, 30, 30))    
            x_inicial_vidas -= 40
        for asteroide in asteroides:
            if asteroide.es_colision(nave):
                asteroide.spawn(asteroides)
                if pause_vidas == 0:
                    nave.vidas -= 1
                    pause_vidas = 30
                    if nave.vidas == 0:
                        corriendo = False
            for bala in balas:
                if asteroide.es_colision(bala):
                    bala.fue_disparada = False
                    bala.x = -20
                    asteroide.spawn(asteroides)

            asteroide.asteroide_caido(asteroides)
            asteroide.actualizar()

            # dibujar
            asteroide.dibujar(ventana)

        nave.dibujar(ventana)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if (nave.y - nave.radio) > 0:
                nave.y -= nave.velocidad
        if keys[pygame.K_a]:
            if (nave.x - nave.radio) > 0:
                nave.x -= nave.velocidad
        if keys[pygame.K_s]:
            if (nave.y + nave.radio) < 600:
                nave.y += nave.velocidad
        if keys[pygame.K_d]:
            if (nave.x + nave.radio) < 600:
                nave.x += nave.velocidad

        if keys[pygame.K_SPACE]:
            if pause_balas == 0:
                for bala in balas:
                    if not bala.fue_disparada:
                        bala.fue_disparada = True
                        bala.disparar(nave)
                        pause_balas = 30
                        break

        for bala in balas:
            bala.actualizar()
            bala.dibujar(ventana)

        if int(time() - tiempo) % 10 == 0:
            for asteroide in asteroides:
                asteroide.velocidad += 0.01

        puntaje += 0.01

        font = pygame.font.Font(pygame.font.get_default_font(), 28)
        text_surface = font.render(f'Puntaje: {round(puntaje)}', True, color_blanco)
        ventana.blit(text_surface, dest=(0, 0))

        pygame.display.update()
        if pause_balas > 0:
            pause_balas -= 1
        if pause_vidas > 0:
            pause_vidas -= 1
        reloj.tick(fps)

    ventana.blit(gameOver, (0, 0))
    pygame.display.update()
    sleep(5)


if __name__ == "__main__":
    main()