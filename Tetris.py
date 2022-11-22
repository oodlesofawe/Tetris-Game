#!/usr/bin/python3

import random
import gi
import pygame
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk # noqa

pygame.init()
pygame.font.init()

# Variables
s_width = 800
s_height = 600
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# Formato de cada figura
S = [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]

Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']]

I = [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']]

O = [['.....', '.....', '.00..', '.00..', '.....']]

J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]

L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]

T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '..... ']]

figuras = [S, Z, I, O, J, L, T]
colores_figuras= [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 

class Pieza(object):
    filas = 20  # y
    columnas = 10  # x

    def __init__(self, columna, fila, figura):
        self.x = columna
        self.y = fila
        self.figura = figura
        self.color = colores_figuras[random.randint(0, 6)]
        self.rotacion = 0  # number from 0-3

def crear_cuadricula(posiciones_bloqueadas={}):
    cuadricula = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(cuadricula)):
        for j in range(len(cuadricula[i])):
            if (j, i) in posiciones_bloqueadas:
                c = posiciones_bloqueadas[(j, i)]
                cuadricula[i][j] = c
    return cuadricula

def convertir_formato_figura(figura):
    posiciones = []
    format = figura.figura[figura.rotacion % len(figura.figura)]

    for i, line in enumerate(format):
        fila = list(line)
        for j, columna in enumerate(fila):
            if columna == '0':
                posiciones.append((figura.x + j, figura.y + i))

    for i, posicion in enumerate(posiciones):
        posiciones[i] = (posicion[0] - 2, posicion[1] - 4)
    return posiciones


def espacio_permitido(figura, cuadricula):
    posiciones_permitidas = [[(j, i) for j in range(10) if cuadricula[i][j] == (0, 0, 0)] for i in range(20)]
    posiciones_permitidas = [j for sub in posiciones_permitidas for j in sub]
    formateado = convertir_formato_figura(figura)

    for posicion in formateado:
        if posicion not in posiciones_permitidas:
            if posicion[1] > -1:
                return False

    return True


def verificar_perdida(posiciones):
    for posicion in posiciones:
        x, y = posicion
        if y < 1:
            return True
    return False


def obtener_figura():
    global figuras, colores_figuras

    return Pieza(5, 0, random.choice(figuras))


def dibujar_texto(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))


def dibujar_cuadricula(surface, fila, columna):
    sx = top_left_x
    sy = top_left_y
    for i in range(fila):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i*30), (sx + play_width, sy + i * 30))  #Lineas horizontales
        for j in range(columna):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy), (sx + j * 30, sy + play_height)) #Lineas verticales


def desaparecer_filas(cuadricula, bloqueadas):
    # Se necesita ver si la fila está despejada

    aumento = 0
    for i in range(len(cuadricula)-1, -1, -1):
        fila = cuadricula[i]
        if (0, 0, 0) not in fila:
            aumento += 1
            # Agregar posiciones para eliminar bloqueadas
            indice = i
            for j in range(len(fila)):
                try:
                    del bloqueadas[(j, i)]
                except: # noqa
                    continue
    if aumento > 0:
        for key in sorted(list(bloqueadas), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < indice:
                nueva_tecla = (x, y + aumento)
                bloqueadas[nueva_tecla] = bloqueadas.pop(key)
    return aumento


def dibujar_siguiente_figura(figura, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Siguiente Figura', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = figura.figura[figura.rotacion % len(figura.figura)]

    for i, line in enumerate(format):
        fila = list(line)
        for j, columna in enumerate(fila):
            if columna == '0':
                pygame.draw.rect(surface, figura.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy-30))


def actualizar_puntaje(nuevo_puntaje):
    puntaje = max_puntaje()

    with open('puntajes.txt', 'w') as f:
        if int(puntaje) > nuevo_puntaje:
            f.write(str(puntaje))
        else:
            f.write(str(nuevo_puntaje))


def max_puntaje():
    with open('puntajes.txt', 'r') as f:
        lines = f.readlines()
        puntaje = lines[0].strip()

    return puntaje


def dibujar_ventana(surface, cuadricula, puntaje=0, ultimo_puntaje = 0):
    surface.fill((0, 0, 0))
    #Titulo de Tetris
    font = pygame.font.SysFont("comicsans", 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # Puntaje actual
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(puntaje), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    #Ultimo puntaje
    label = font.render('High Score: ' + ultimo_puntaje, 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(cuadricula)):
        for j in range(len(cuadricula[i])):
            pygame.draw.rect(surface, cuadricula[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)

    #Dibujar borde y cuadricula
    dibujar_cuadricula(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    # pygame.display.update()


def musica():
    # reproduccion de la musica
    pygame.mixer.init()
    cancion = (
        "/home/jeremysg/Desktop/tetris_practica/musiquita_tetris.wav"
    )

    sonido_fondo = pygame.mixer.Sound(cancion)
    pygame.mixer.Sound.play(sonido_fondo, -1)


def Ventana_ajustes(button):
    builder = Gtk.Builder()
    archivo = (
        "/home/jeremysg/Desktop/tetris_practica/prac_glade.glade"
    )

    builder.add_from_file(archivo)

    window = builder.get_object('Main_window')

    # Main_window.realize(main_menu())
    Bsonido_off = builder.get_object('Music_off')
    Bsonido_on = builder.get_object('Music_on')
    Bsalir = builder.get_object('Bsalir')
    Bpausa = builder.get_object('Bpausa')

    def continuarM(button):
        pygame.mixer.unpause()

    def pausarM(button):
        pygame.mixer.pause()

    def salirJ(button):
        window.hide()
        pygame.quit()
        Gtk.main_quit()

    def pausarJ(button):
        window.hide()
        Gtk.main_quit()

    Bsalir.connect('clicked', salirJ)
    Bpausa.connect('clicked', pausarJ)
    Bsonido_off.connect('clicked', pausarM)
    Bsonido_on.connect('clicked', continuarM)
    window.show_all()
    Gtk.main()


def main(win):
    musica()
    global cuadricula

    ultimo_puntaje = max_puntaje()
    posiciones_bloqueadas = {}  # (x,y):(255,0,0)
    cuadricula = crear_cuadricula(posiciones_bloqueadas)

    cambiar_pieza = False
    correr = True
    pieza_actual = obtener_figura()
    pieza_siguiente = obtener_figura()
    reloj = pygame.time.Clock()
    tiempo_caida = 0
    tiempo_nivel = 0
    puntaje = 0

    while correr:
        rapidez_caida = 0.27

        cuadricula = crear_cuadricula(posiciones_bloqueadas)
        tiempo_caida += reloj.get_rawtime()
        tiempo_nivel += reloj.get_rawtime()
        reloj.tick()

        if tiempo_nivel/1000 > 5:
            tiempo_nivel = 0
            if tiempo_nivel > 0.12:
                tiempo_nivel -= 0.005

        # Caida de la pieza
        if tiempo_caida/1000 >= rapidez_caida:
            tiempo_caida = 0
            pieza_actual.y += 1
            if not (espacio_permitido(pieza_actual, cuadricula)) and pieza_actual.y > 0:
                pieza_actual.y -= 1
                cambiar_pieza = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                correr = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pieza_actual.x -= 1
                    if not espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.x += 1

                elif event.key == pygame.K_RIGHT:
                    pieza_actual.x += 1
                    if not espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.x -= 1
                elif event.key == pygame.K_UP:
                    # Rotar la figura
                    pieza_actual.rotacion = pieza_actual.rotacion + 1 % len(pieza_actual.figura)
                    if not espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.rotacion = pieza_actual.rotacion - 1 % len(pieza_actual.figura)

                if event.key == pygame.K_DOWN:
                    # Mover la figura hacia abajo
                    pieza_actual.y += 1
                    if not espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.y -= 1

                if event.key == ord("p"):
                    Ventana_ajustes(None)

                if event.key == pygame.K_SPACE:
                    while espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.y += 1
                    pieza_actual.y -= 1
                    print(convertir_formato_figura(pieza_actual))  # todo arreglado
                if event.key == pygame.K_SPACE:
                    while espacio_permitido(pieza_actual, cuadricula):
                        pieza_actual.y += 1
                    pieza_actual.y -= 1
                    print(convertir_formato_figura(pieza_actual))  # todo arreglado

        posicion_figura = convertir_formato_figura(pieza_actual)

        # Agregar pieza a la cuadricula para dibujar
        for i in range(len(posicion_figura)):
            x, y = posicion_figura[i]
            if y > -1:
                cuadricula[y][x] = pieza_actual.color

        #Si la pieza toca el suelo
        if cambiar_pieza:
            for posicion in posicion_figura:
                p = (posicion[0], posicion[1])
                posiciones_bloqueadas[p] = pieza_actual.color
            pieza_actual = pieza_siguiente
            pieza_siguiente = obtener_figura()
            cambiar_pieza = False
            puntaje += desaparecer_filas(cuadricula, posiciones_bloqueadas) * 10

            # Llamar cuatro veces para comprobar multiples desapariciones de filas
            desaparecer_filas(cuadricula, posiciones_bloqueadas)

        dibujar_ventana(win, cuadricula, puntaje, ultimo_puntaje)
        dibujar_siguiente_figura(pieza_siguiente, win)
        pygame.display.update()

        # Comprobar si el usuario perdio
        if verificar_perdida(posiciones_bloqueadas):
            correr = False

    dibujar_texto("Has perdido", 40, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)
    actualizar_puntaje(puntaje)
    Ventana_ajustes(None)
    pygame.mixer.quit()


def main_menu():
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    correr = True
    while correr:
        win.fill((0, 0, 0))
        dibujar_texto('Toca cualquier tecla para comenzar', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                correr = False

            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


def menu_principal():
    def iniciar_juego(button):
        menu_inicial.hide()
        Gtk.main_quit()
        main_menu()

    def salir(button):
        menu_inicial.hide()
        pygame.quit
        Gtk.main_quit()

    builder = Gtk.Builder()

    archivo = (
        "/home/jeremysg/Desktop/tetris_practica/prac_glade.glade"
    )

    builder.add_from_file(archivo)
    menu_inicial = builder.get_object('Menu_inicial')
    Empezar = builder.get_object('Bempezar')
    Opciones = builder.get_object('Bopciones')
    Salir = builder.get_object('Bsalir')

    Empezar.connect('clicked', iniciar_juego)
    Opciones.connect('clicked', Ventana_ajustes)
    Salir.connect('clicked', Gtk.main_quit)
    menu_inicial.show_all()
    Gtk.main()


menu_principal()
