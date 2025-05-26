from funkcja_rysujaca import rysuj 
from funkcja_rysujaca import rysuj_walec

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import time
import math

sys.setrecursionlimit(10000)  # Domyślnie 1000

z_pos_blatu = 0.225
z_pos_suwaka = -0.6  # początkowa pozycja suwaka
x_pos_glowica = 0


anim_clear = False
clear_stage = 0

anim_usuwania = False
czas_ostatniego_usuwania = 0
opoznienie_usuwania = 0.1  # ms (czyli 0.1 sekundy)

#deklaracje dlugosci

def Table(blat_z, suwak_z, glowica_x):
    rysuj((-0.5, -0.925, 0), (0.1, 0.025, 1.25), (0, 0, 0))  # nóżki
    rysuj((0.5, -0.925, 0), (0.1, 0.025, 1.25), (0, 0, 0))   # nóżki

    #rysuj((0, -0.8825, blat_z), (1, 0.015, 1), (0.6275, 0.6314, 0.6275))  # blat
    #rysuj((0, -1.05, 0), (1.5, 0.1, 1.5), (0.4314, 0.5412, 0.6235))     # podstawka

    rysuj_walec((-1.25, -1, 0), 2, 0.2, (0.3529, 0.4314, 0.4902))
    rysuj_walec((1.25, -1, 0), 2, 0.2, (0.3529, 0.4314, 0.4902))

    rysuj((-1.25, 0.1, 0.2), (0.05, 0.9, 0.01), (0, 0, 0))
    rysuj((1.25, 0.1, 0.2), (0.05, 0.9, 0.01), (0, 0, 0))

    rysuj_walec((-1.25, 1, 0), 0.25, 0.2, (0, 0, 0))
    rysuj_walec((1.25, 1, 0), 0.25, 0.2, (0, 0, 0))

    rysuj((0, 1.1, 0), (1.2, 0.05, 0.03), (0, 0, 0))  # łącznik

    rysuj((0, suwak_z, 0.225), (1.4, 0.05, 0.03), (0, 0, 0))  # suwak

    rysuj((glowica_x, z_pos_suwaka-0.05, 0.225), (0.15, 0.15, 0.15), (0, 1, 0)) #głowica (0.6275, 0.6314, 0.6275)

    rysuj((glowica_x, z_pos_suwaka-0.225, 0.225), (0.025, 0.025, 0.025), (1, 0, 0)) #czubek głowicy

def generator_szescianu(n):
    """
    Generator tworzący współrzędne kostek sześcianu o krawędzi n
    w kolejności: Y (przód–tył) → Z (dół–góra) → X (lewo–prawo)
    """
    SNAP_SIZE = 0.02
    y_block_relative = -0.86 - SNAP_SIZE
    for k in range(n):  # Oś Y (przód–tył)
        y_block_relative += SNAP_SIZE
        target_z_suwaka = y_block_relative + 0.26
        yield ("SET_SUWAK_Y", target_z_suwaka)

        for j in range(n):  # Oś Z (dół–góra)
            if j > 0:
                yield ("LAYER_DOWN",)
            z_c_for_block = j * SNAP_SIZE

            for i in range(n):  # Oś X (lewo–prawo)
                x_block_relative = (i - (n - 1) / 2) * SNAP_SIZE
                yield ("SET_HEAD_X", x_block_relative)

                # Dodaj blok na aktualnej pozycji (x, y, z)
                yield ("PRINT_BLOCK", (x_block_relative, y_block_relative, z_c_for_block))

        # Po zakończeniu warstw Z przywróć blat na górę
        yield ("RESET_BLAT_Z", (n-1) * SNAP_SIZE)

    yield ("FINISHED",)
    

def generator_kuli(n_radius):

    SNAP_SIZE = 0.02
    Y_CENTER_PRINTER = -0.86

    if n_radius < 0:
        n_radius = 0

    current_z_print_level_for_y_slice = 0

    for y_idx in range(-n_radius, n_radius + 1):
        y_offset_from_sphere_center = y_idx * SNAP_SIZE
        y_block_absolute_printer = Y_CENTER_PRINTER + y_offset_from_sphere_center
        target_z_suwaka = y_block_absolute_printer + 0.26
        yield ("SET_SUWAK_Y", target_z_suwaka)

        layer_downs_for_this_y_slice = 0
        current_z_print_level_for_y_slice += 4

        for z_idx in range(-n_radius, n_radius + 1):
            min_x_idx_for_slice = n_radius + 1
            max_x_idx_for_slice = -n_radius - 1
            found_block_in_xz_plane = False

            # Zmieniony warunek - sprawdzanie najdalszego narożnika bloku
            # Używamy abs(y_idx) i abs(z_idx) bo y_idx i z_idx mogą być ujemne.
            # (abs(x_idx_check) + 0.5)**2 odnosi się do odległości kwadratowej
            # najdalszej krawędzi x bloku od środka płaszczyzny yz.
            # n_radius_squared = float(n_radius)**2 # Użyj float dla n_radius**2 jeśli chcesz większej precyzji w progu
            n_radius_squared = n_radius**2 # Dla spójności z int n_radius

            # Próg dla sumy kwadratów y i z (dla narożnika)
            yz_corner_sq_sum = (abs(y_idx) + 0.5)**2 + (abs(z_idx) + 0.5)**2

            for x_idx_check in range(-n_radius, n_radius + 1):
                # Warunek przynależności najdalszego narożnika bloku do sfery
                if (abs(x_idx_check) + 0.5)**2 + yz_corner_sq_sum <= n_radius_squared:
                    found_block_in_xz_plane = True
                    min_x_idx_for_slice = min(min_x_idx_for_slice, x_idx_check)
                    max_x_idx_for_slice = max(max_x_idx_for_slice, x_idx_check)

            if not found_block_in_xz_plane:
                continue

            if current_z_print_level_for_y_slice > 0:
                yield ("LAYER_DOWN",)
                layer_downs_for_this_y_slice += 1

            z_coordinate_for_block_in_y_slice = current_z_print_level_for_y_slice * SNAP_SIZE

            for x_idx in range(min_x_idx_for_slice, max_x_idx_for_slice + 1):
                # Ponowne sprawdzenie warunku dla konkretnego x_idx
                if (abs(x_idx) + 0.5)**2 + yz_corner_sq_sum <= n_radius_squared:
                    x_block_absolute_printer = x_idx * SNAP_SIZE
                    yield ("SET_HEAD_X", x_block_absolute_printer)
                    yield ("PRINT_BLOCK", (x_block_absolute_printer, y_block_absolute_printer, z_coordinate_for_block_in_y_slice))

            current_z_print_level_for_y_slice += 1

        

        if layer_downs_for_this_y_slice > 0:
            yield ("RESET_BLAT_Z", layer_downs_for_this_y_slice * SNAP_SIZE)

    yield ("FINISHED",)

def animacja_clear():
    global z_pos_blatu, z_pos_suwaka, x_pos_glowica, clear_stage, anim_clear

    # Etap 1: Suwak do 0.9
    if clear_stage == 0:
        if z_pos_suwaka < 0.9:
            z_pos_suwaka = min(z_pos_suwaka + 0.02, 0.9)
        else:
            clear_stage = 1

    # Etap 2: Głowica do 0
    elif clear_stage == 1:
        if x_pos_glowica > 0:
            x_pos_glowica = max(x_pos_glowica - 0.01, 0)
        elif x_pos_glowica < 0:
            x_pos_glowica = min(x_pos_glowica + 0.01, 0)
        else:
            clear_stage = 2

    # Etap 3: Blat do 0.225
    elif clear_stage == 2:
        if z_pos_blatu > 0:
            z_pos_blatu = max(z_pos_blatu - 0.01, 0.)
        elif z_pos_blatu < 0:
            z_pos_blatu = min(z_pos_blatu + 0.01, 0.)
        else:
            anim_clear = False  # Zakończ animację
            clear_stage = 0

def Main():
    clock = pygame.time.Clock()
    global z_pos_blatu, z_pos_suwaka, x_pos_glowica, anim_clear, anim_usuwania, czas_ostatniego_usuwania

    last_block_time = 0
    drukowanie = False
    generator = None
    czas_ostatniego_kroku = 0
    opoznienie_kroku = 0.1 #szybkosc drukowania - zalecane ok 100

    pygame.init()
    pygame.font.init() # Inicjalizacja modułu czcionek
    screen_width, screen_height = 1840, 1000
    screen_size = (screen_width, screen_height)
    display = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("SEMEN BEZ NAPLETA") # Rozważ zmianę tytułu na bardziej neutralny dla projektu akademickiego

    glClearColor(1, 1, 1, 1)
    gluPerspective(45, (screen_width / screen_height), 0.1, 500)
    glEnable(GL_DEPTH_TEST)
    # glDisable(GL_BLEND) # Wykomentowane, bo blending będzie potrzebny dla tekstu FPS
    glTranslatef(0, 0, -5)

    button_down = False
    cubes = set()

    # === Stworzenie display listy dla kostki ===
    cube_display = glGenLists(1)
    glNewList(cube_display, GL_COMPILE)
    rysuj((0, 0, 0), (0.01, 0.01, 0.01), (0, 0, 1)) # Użycie funkcji rysuj
    glEndList()

    # Zmienne do śledzenia i wyświetlania FPS
    fps_font = pygame.font.Font(None, 36) # Rozmiar czcionki dla FPS
    frame_times = []
    fps_update_interval = 1.0 # sekundy
    last_fps_update_time = time.time()
    displayed_fps = 0

    while True:
        current_time_for_fps = time.time()
        frame_times.append(current_time_for_fps)
        # Usuń czasy klatek starsze niż 1 sekunda (lub trochę więcej dla stabilności)
        while frame_times and frame_times[0] < current_time_for_fps - (fps_update_interval + 0.5):
            frame_times.pop(0)

        if current_time_for_fps - last_fps_update_time > fps_update_interval:
            if len(frame_times) > 1:
                # Oblicz FPS na podstawie różnicy czasów ostatnich klatek w okresie
                time_span = frame_times[-1] - frame_times[0]
                if time_span > 0:
                    displayed_fps = (len(frame_times) -1) / time_span
            else:
                displayed_fps = 0 # lub clock.get_fps() jako fallback
            last_fps_update_time = current_time_for_fps
            # Można też użyć: displayed_fps = clock.get_fps() dla prostszego, ale czasem mniej dokładnego odczytu

        button_down = pygame.mouse.get_pressed()[0] == 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_c: # Użyjmy 'c' dla sześcianu
                    if not drukowanie:
                        generator = generator_szescianu(4) 
                        drukowanie = True
                        print("Rozpoczęto drukowanie sześcianu...")

                if event.key == pygame.K_v: # Dodajmy nowy klawisz, np. 'v' dla kuli (sphere/ball)
                    if not drukowanie:
                        # Inicjalizacja drukowania kuli o promieniu np. 10 jednostek
                        generator = generator_kuli(5) 
                        drukowanie = True
                        print("Rozpoczęto drukowanie kuli...")

                if event.key == pygame.K_r:
                    anim_clear = True

                if event.key == pygame.K_DELETE:
                    if cubes:
                        anim_usuwania = True
                        czas_ostatniego_usuwania = pygame.time.get_ticks()
                        print("Rozpoczęto animację usuwania kostek.")

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    z_pos_suwaka = min(z_pos_suwaka + 0.02, 0.9)
                elif event.y < 0:
                    z_pos_suwaka = max(z_pos_suwaka - 0.02, -0.6)
            if event.type == pygame.MOUSEMOTION:
                if button_down and (event.rel[0] != 0 or event.rel[1] != 0):
                    sensitivity = 0.1
                    glRotatef(event.rel[1] * sensitivity, 1, 0, 0)
                    glRotatef(event.rel[0] * sensitivity, 0, 1, 0)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            now = time.time()
            if now - last_block_time > (1/120.0): # Użyj float dla dzielenia
                snap = 0.02
                x = round(x_pos_glowica / snap) * snap
                y = round((z_pos_suwaka - 0.26) / snap) * snap
                z_na_powierzchni_blatu = z_pos_blatu + (0.015/2) + (0.01/2)
                z_offset_value = round(-(z_pos_blatu - 0.225) / snap) * snap
                rounded_pos = (x, y, z_offset_value)


                if rounded_pos not in cubes:
                    cubes.add(rounded_pos)
                    print(f'Dodano kostkę w przybliżeniu: {rounded_pos}, przy z_blatu: {z_pos_blatu}')
                last_block_time = now
        # else: # Usunięcie tego else pozwala na płynniejsze dodawanie kostek przy przytrzymaniu spacji
        #     last_block_time = 0


        if not anim_clear and not drukowanie:
            if keys[pygame.K_s] and z_pos_blatu > -0.595:
                z_pos_blatu -= 0.02
            if keys[pygame.K_w] and z_pos_blatu < 1.045:
                z_pos_blatu += 0.02
            if keys[pygame.K_a] and x_pos_glowica > -0.825:
                x_pos_glowica -= 0.02
            if keys[pygame.K_d] and x_pos_glowica < 0.825:
                x_pos_glowica += 0.02

                # Logika drukowania z generatora
        if drukowanie:
            teraz = pygame.time.get_ticks()
            if teraz - czas_ostatniego_kroku >= opoznienie_kroku:
                try:
                    command = next(generator) # Pobierz kolejną komendę z generatora
                    
                    if command[0] == "SET_HEAD_X":
                        x_pos_glowica = command[1]
                        
                    elif command[0] == "SET_SUWAK_Y":
                        z_pos_suwaka = command[1]
                        
                    elif command[0] == "LAYER_DOWN":
                        z_pos_blatu -= 0.02 # Opuść blat o jeden krok
                    elif command[0] == "PRINT_BLOCK":
                        cubes.add(command[1]) # Dodaj kostkę
                    elif command[0] == "FINISHED":
                        drukowanie = False
                        generator = None
                        anim_clear = True
                        print("Drukowanie zakończone!")
                    elif command[0] == "RESET_BLAT_Z":
                        z_pos_blatu += command[1]  # Przywróć blat na górę   
                    
                    czas_ostatniego_kroku = teraz
                except StopIteration:
                    drukowanie = False
                    generator = None
                    print("Drukowanie zakończone z wyjątkiem StopIteration.")

        if anim_clear:
            animacja_clear()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Table(z_pos_blatu, z_pos_suwaka, x_pos_glowica)

        for x_c, y_c, z_c in cubes: # Użycie innych nazw zmiennych, aby uniknąć konfliktu
            glPushMatrix()
            # Rysowanie kostki: z_c to offset, z_pos_blatu to aktualne przesunięcie blatu.
            # To zakłada, że ruch blatu (W/S) ma przesuwać także wszystkie "wydrukowane" kostki.
            glTranslatef(x_c, y_c, z_c + z_pos_blatu)
            glCallList(cube_display)
            glPopMatrix()

        if anim_usuwania:
            teraz = pygame.time.get_ticks()
            if teraz - czas_ostatniego_usuwania >= opoznienie_usuwania: # opoznienie_usuwania jest w ms
                if cubes:
                    removed = cubes.pop()
                    print(f"Usunięto kostkę: {removed}")
                    czas_ostatniego_usuwania = teraz
                else:
                    anim_usuwania = False
                    print("Wszystkie kostki usunięte.")

        # --- Rysowanie FPS ---
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, screen_width, 0, screen_height) # Ustawia (0,0) w lewym dolnym rogu
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        fps_text_surface = fps_font.render(f"FPS: {displayed_fps:.2f}", True, (0, 0, 0), (255,255,255,180)) # Czarny tekst, lekko przezroczyste tło
        text_data = pygame.image.tostring(fps_text_surface, "RGBA", True)

        text_x = 10
        text_y = screen_height - fps_text_surface.get_height() - 10 # Pozycja od góry

        glRasterPos2i(text_x, text_y)
        glDrawPixels(fps_text_surface.get_width(), fps_text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        glEnable(GL_DEPTH_TEST) # Przywróć test głębi
        glDisable(GL_BLEND) # Wyłącz blending, jeśli nie jest potrzebny dla reszty sceny

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        # --- Koniec rysowania FPS ---

        pygame.display.flip()
        clock.tick(60) # Ogranicza do maksymalnie 60 FPS


Main()