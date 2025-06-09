import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import time
import math

from funkcyjka import rysuj, rysuj_walec, vertices, edges, faces, normals

sys.setrecursionlimit(10000)# Domyślnie 1000

#____ZMIENNE____
pozycja_neutralna = False
numer_etapu = 0
zadanie_do_druku_po_neutralnej = None
anim_usuwania = False
czas_ostatniego_usuwania = 0
czas_ostatniego_bloku = 0
drukowanie = False
generator = None
czas_ostatniego_kroku = 0
tryb_widoku = False  # do kontroli trybu widoku
wyswietlanie_budowy_drukarki = True  # do kontroli renderowania drukarki

# początkowa pozycja suwaka
z_pos_blatu = 0.225
y_pos_suwaka = -0.6
x_pos_glowica = 0

# KOLORY
kolor_nóżek = (0.1, 0.1, 0.1)
kolor_szyn = (0.05, 0.05, 0.05)
kolor_platformy = (0.6, 0.6, 0.65)
kolor_podstawy = (0.4, 0.5, 0.6)
kolor_walca = (0.3, 0.4, 0.45)
kolor_koncowek = (0.1, 0.1, 0.1)
kolor_lacznika_koncowek = (0.1, 0.1, 0.1)
kolor_suwaka = (0.05, 0.05, 0.05)
kolor_glowicy = (0, 0.8, 0)
kolor_dyszy = (0.8, 0, 0)

#STAŁE
opoznienie_kroku = 100  # szybkosc drukowania - zalecane ok 100
opoznienie_usuwania = 0.1  # ms (0.1 seconds)
szybkosc_recznego_drukowania = 120
stala_przesuniecia_wzgledem_srodka = 0.225  # to jest w osi z i dotyczy blatu
stala_przesuniecia_dyszy = 0.05 + 0.15 + 0.025  # 0.05 - przesuniecie glowicy wzgledem suwaka;  0.15 - polowa glowicy; 0.025 - polowa dyszy
stala_przesuniecia_atramentu = stala_przesuniecia_dyszy + 0.025 + 0.01  # 0.025 - kolejna polowa dyszy; 0.01 - polowa kosteczki

# neutralna pozycja
NEUTRAL_Y_SUWAKA = -0.6
NEUTRAL_X_GLOWICY = 0.0
NEUTRAL_Z_BLATU = 0.225

def Table(blat_z, suwak_y, glowica_x):
    if wyswietlanie_budowy_drukarki:
        rysuj((-0.5, -0.925, 0), (0.1, 0.025, 1.25), kolor_nóżek) # Nogi
        rysuj((0.5, -0.925, 0), (0.1, 0.025, 1.25), kolor_nóżek) # Nogi
        rysuj((0, -0.8825, blat_z), (1, 0.015, 1), kolor_platformy) # Platforma
        rysuj((0, -1.05, 0), (1.5, 0.1, 1.5), kolor_podstawy) # Platforma

        
        rysuj((-1.25, 0, 0), (0.2, 1, 0.2), kolor_walca) # Prostopadloscian zamiast Walec
        rysuj((1.25, 0, 0), (0.2, 1, 0.2), kolor_walca) # Prostopadloscian zamiast Walec      

        #rysuj_walec((-1.25, -1, 0), 2, 0.2, kolor_walca)
        #rysuj_walec((1.25, -1, 0), 2, 0.2, kolor_walca)
        rysuj_walec((-1.25, 1, 0), 0.25, 0.2, kolor_koncowek) # Końcówka
        rysuj_walec((1.25, 1, 0), 0.25, 0.2, kolor_koncowek) # Końcówka
        rysuj((-1.25, 0.1, 0.2), (0.05, 0.9, 0.01), kolor_szyn)  # Szyny
        rysuj((1.25, 0.1, 0.2), (0.05, 0.9, 0.01), kolor_szyn)  # Szyny
        rysuj((0, 1.1, 0), (1.2, 0.05, 0.03), kolor_lacznika_koncowek) # Łącznik
        rysuj((0, suwak_y, stala_przesuniecia_wzgledem_srodka), (1.4, 0.05, 0.03), kolor_suwaka) # Suwak
        rysuj((glowica_x, suwak_y-0.05, stala_przesuniecia_wzgledem_srodka), (0.15, 0.15, 0.15), kolor_glowicy) # Głowica
        rysuj((glowica_x, suwak_y-stala_przesuniecia_dyszy, stala_przesuniecia_wzgledem_srodka), (0.025, 0.025, 0.025), kolor_dyszy) # Dysza
        rysuj((glowica_x, suwak_y-stala_przesuniecia_atramentu, stala_przesuniecia_wzgledem_srodka), (0.01, 0.01, 0.01), (0, 0, 1)) # Atrament

def generator_szescianu(n):
    """Generator współrzędnych dla sześcianu (Y -> Z -> X)."""
    ROZMIAR_KOSTKI = 0.02
    y_bloku_wzgledna = -0.86 - ROZMIAR_KOSTKI
    for k in range(n):  # Oś Y
        y_bloku_wzgledna += ROZMIAR_KOSTKI
        cel_z_suwaka = y_bloku_wzgledna + stala_przesuniecia_atramentu
        yield ("USTAW_SUWAK_Y", cel_z_suwaka)
        for j in range(n):  # Oś Z
            if j > 0:
                yield ("USTAW_BLAT_Z",)
            z_c_for_block = j * ROZMIAR_KOSTKI
            for i in range(n):  # Oś X
                x_bloku_wzgledna = (i - (n - 1) / 2) * ROZMIAR_KOSTKI
                yield ("USTAW_GLOWICA_X", x_bloku_wzgledna)
                
                # Dodaj blok na aktualnej pozycji (x, y, z)
                yield ("PRINT_BLOCK", (x_bloku_wzgledna, y_bloku_wzgledna, z_c_for_block))
        # Po zakończeniu warstw Z przywróć blat na górę
        yield ("RESET_BLAT_Z", (n-1) * ROZMIAR_KOSTKI)
    yield ("FINISHED",)

def generator_kuli(r_promien):
    """
    Generator tworzący współrzędne kostek sfery 3D o promieniu r_promien
    w kolejności: Y (góra-dół) -> Z (przód-tył) -> X (prawo-lewo)
    """
    ROZMIAR_KOSTKI = 0.02
    
    # Ale z uwagi na koordynaty drukarki, y_bloku_wzgledna = -0.86 jest ok dla blatu.
    y_start_pos_for_kula = -0.86
    
    # Przechodzimy po osi Y (góra-dół)
    for k_y in range(-r_promien, r_promien + 1):

        y_bloku_wzgledna = y_start_pos_for_kula + (k_y + r_promien) * ROZMIAR_KOSTKI
        
        target_suwak_y = y_bloku_wzgledna + stala_przesuniecia_atramentu 
        
        # Zabezpieczenie przed zejściem suwaka za nisko
        target_suwak_y = max(target_suwak_y, NEUTRAL_Y_SUWAKA)
        yield ("USTAW_SUWAK_Y", target_suwak_y)

        # Przechodzimy po osi Z (przód-tył)
        # Zaczynamy od -r_promien do r_promien (od tylu do przodu)
        for k_z in range(-r_promien, r_promien + 1):
            # Jeśli nie jest to pierwsza warstwa Z w danej "plastrze" Y, ustaw blat
            # Po każdym Z warstwie, blat się ustawia (z_pos_blatu rośnie)
            if k_z > -r_promien: 
                yield ("USTAW_BLAT_Z",) 
            
            z_c_for_block = k_z * ROZMIAR_KOSTKI

            # Przechodzimy po osi X (prawo-lewo)
            for k_x in range(-r_promien, r_promien + 1):
                x_bloku_wzgledna = k_x * ROZMIAR_KOSTKI
                
                # Sprawdzamy, czy punkt (k_x, k_y, k_z) mieści się w kuli
                # Równanie sfery: x^2 + y^2 + z^2 <= r^2
                if (k_x**2 + k_y**2 + k_z**2) <= r_promien**2:
                    yield ("USTAW_GLOWICA_X", x_bloku_wzgledna)
                    # Dodaj blok na aktualnej pozycji (x, y, z)
                    # Ważne: z_c_for_block to relatywna pozycja Z kostki.
                    yield ("PRINT_BLOCK", (x_bloku_wzgledna, y_bloku_wzgledna, z_c_for_block + 0.02*r_promien))

        # Po zakończeniu wszystkich warstw Z dla danej Y, przywróć pozycje blatu,
        if k_y < r_promien:
            yield ("RESET_BLAT_Z", (2 * r_promien) * ROZMIAR_KOSTKI) 

    yield ("FINISHED",)

def ustaw_pozycje_nautralna():
    global z_pos_blatu, y_pos_suwaka, x_pos_glowica, numer_etapu, pozycja_neutralna
    global drukowanie, generator, zadanie_do_druku_po_neutralnej

    # Etap 1: Suwak do -0.6
    if numer_etapu == 0:
        if y_pos_suwaka > NEUTRAL_Y_SUWAKA:
            y_pos_suwaka = max(y_pos_suwaka - 0.02, NEUTRAL_Y_SUWAKA)
        else:
            numer_etapu = 1

    # Etap 2: Głowica do 0
    elif numer_etapu == 1:
        if x_pos_glowica > NEUTRAL_X_GLOWICY:
            x_pos_glowica = max(x_pos_glowica - 0.01, NEUTRAL_X_GLOWICY)

        elif x_pos_glowica < NEUTRAL_X_GLOWICY:
            x_pos_glowica = min(x_pos_glowica + 0.01, NEUTRAL_X_GLOWICY)

        else:
            numer_etapu = 2

    # Etap 3: Blat do 0.225
    elif numer_etapu == 2:
        if z_pos_blatu > NEUTRAL_Z_BLATU:
            z_pos_blatu = max(z_pos_blatu - 0.01, NEUTRAL_Z_BLATU)
        elif z_pos_blatu < NEUTRAL_Z_BLATU:
            z_pos_blatu = min(z_pos_blatu + 0.01, NEUTRAL_Z_BLATU)
        else:
            pozycja_neutralna = False  # Zakończ animację
            numer_etapu = 0

            if zadanie_do_druku_po_neutralnej == "szescian":
                print("Pozycja neutralna osiągnięta. Rozpoczynanie drukowania sześcianu...")
                generator = generator_szescianu(4)
                drukowanie = True
                zadanie_do_druku_po_neutralnej = None
            elif zadanie_do_druku_po_neutralnej == "kula":
                print("Pozycja neutralna osiągnięta. Rozpoczynanie drukowania kuli...")
                generator = generator_kuli(4)
                drukowanie = True
                zadanie_do_druku_po_neutralnej = None   

                
def Main():
    global z_pos_blatu, y_pos_suwaka, x_pos_glowica, pozycja_neutralna, anim_usuwania, czas_ostatniego_usuwania
    global czas_ostatniego_kroku, drukowanie, czas_ostatniego_bloku, generator, zadanie_do_druku_po_neutralnej
    global stala_przesuniecia_atramentu, stala_przesuniecia_wzgledem_srodka, tryb_widoku, wyswietlanie_budowy_drukarki
    button_down = False
    cubes = set()
    clock = pygame.time.Clock()
    pygame.init()
    pygame.font.init()
    screen_width, screen_height = 1840, 1000
    display = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Drukarka 3D")
    glClearColor(0.8, 0.8, 1.0, 1.0) # Jaśniejszy kolor tła (np. błękitny)
    gluPerspective(45, (screen_width / screen_height), 0.1, 500) # kamera widzi 45 stopni, proporcje ekranu, minimalna odleglosc od kamery,max odleglosc do ktorej rysujemy
    
    # Włączenie oświetlenia i ustawienia
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Pozycja i jasność światła
    light_position = [0.0, 4.0, 0.0, 1.0]  # Nowa pozycja światła
    light_ambient = [0.2, 0.2, 0.2, 0.2]   # Ambient - delikatne oświetlenie tła
    light_diffuse = [0.2, 0.2, 0.2, 0.2]   # Diffuse (zmniejszona jasność)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    
    glTranslatef(0, 0, -5)
    cube_display = glGenLists(1)
    glNewList(cube_display, GL_COMPILE)
    rysuj((0, 0, 0), (0.01, 0.01, 0.01), (0, 0, 1))
    glEndList()

    while True:
        button_down = pygame.mouse.get_pressed()[0] == 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    tryb_widoku = not tryb_widoku
                    wyswietlanie_budowy_drukarki = not tryb_widoku
                    print(f"Tryb widoku: {tryb_widoku}")
                if not tryb_widoku:
                    if event.key == pygame.K_c:
                        if not drukowanie and not pozycja_neutralna and zadanie_do_druku_po_neutralnej is None:
                            print("Żądanie drukowania sześcianu. Ustawianie pozycji neutralnej...")
                            zadanie_do_druku_po_neutralnej = "szescian"
                            pozycja_neutralna = True
                        elif drukowanie:
                            print("Drukowanie w toku. Nie można rozpocząć nowego zadania.")
                        elif pozycja_neutralna or zadanie_do_druku_po_neutralnej is not None:
                            print("Maszyna jest w trakcie ustawiania pozycji neutralnej lub ma już zaplanowane zadanie.")
                    if event.key == pygame.K_v:
                        if not drukowanie and not pozycja_neutralna and zadanie_do_druku_po_neutralnej is None:
                            print("Żądanie drukowania kuli. Ustawianie pozycji neutralnej...")
                            zadanie_do_druku_po_neutralnej = "kula"
                            pozycja_neutralna = True
                        elif drukowanie:
                            print("Drukowanie w toku. Nie można rozpocząć nowego zadania.")
                        elif pozycja_neutralna or zadanie_do_druku_po_neutralnej is not None:
                            print("Maszyna jest w trakcie ustawiania pozycji neutralnej lub ma już zaplanowane zadanie.")
                    if event.key == pygame.K_r:
                        pozycja_neutralna = True
                    if event.key == pygame.K_DELETE:
                        if cubes:
                            anim_usuwania = True
                            czas_ostatniego_usuwania = pygame.time.get_ticks()
                            print("Rozpoczęto animację usuwania kostek.")
            if event.type == pygame.MOUSEWHEEL:
                if tryb_widoku:
                    zoom_speed = 0.1
                    glTranslatef(0, 0, event.y * zoom_speed)
                elif not pozycja_neutralna and not drukowanie:
                    if event.y > 0:
                        y_pos_suwaka = min(y_pos_suwaka + 0.02, 0.9)
            if event.type == pygame.MOUSEMOTION:
                if button_down and (event.rel[0] != 0 or event.rel[1] != 0):
                    sensitivity = 0.1
                    glRotatef(event.rel[1] * sensitivity, 1, 0, 0)
                    glRotatef(event.rel[0] * sensitivity, 0, 1, 0)

        if not tryb_widoku:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                now = time.time()
                if now - czas_ostatniego_bloku > (1/szybkosc_recznego_drukowania):
                    snap = 0.02
                    x = round(x_pos_glowica / snap) * snap
                    y = round((y_pos_suwaka - stala_przesuniecia_atramentu) / snap) * snap
                    z = round(-(z_pos_blatu - stala_przesuniecia_wzgledem_srodka) / snap) * snap
                    rounded_pos = (x, y, z)
                    if rounded_pos not in cubes:
                        cubes.add(rounded_pos)
                        print(f'Dodano kostkę w przybliżeniu: {rounded_pos}, przy z_blatu: {z_pos_blatu}')
                    czas_ostatniego_bloku = now

            if not pozycja_neutralna and not drukowanie:
                if keys[pygame.K_s] and z_pos_blatu > -0.595:
                    z_pos_blatu -= 0.02
                if keys[pygame.K_w] and z_pos_blatu < 1.045:
                    z_pos_blatu += 0.02
                if keys[pygame.K_a] and x_pos_glowica > -0.825:
                    x_pos_glowica -= 0.02
                if keys[pygame.K_d] and x_pos_glowica < 0.825:
                    x_pos_glowica += 0.02

            if drukowanie:
                teraz = pygame.time.get_ticks()
                if teraz - czas_ostatniego_kroku >= opoznienie_kroku:
                    try:
                        command = next(generator)
                        if command[0] == "USTAW_GLOWICA_X":
                            x_pos_glowica = command[1]
                        elif command[0] == "USTAW_SUWAK_Y":
                            y_pos_suwaka = command[1]
                        elif command[0] == "USTAW_BLAT_Z":
                            z_pos_blatu -= 0.02
                        elif command[0] == "PRINT_BLOCK":
                            cubes.add(command[1])
                        elif command[0] == "FINISHED":
                            drukowanie = False
                            generator = None
                            pozycja_neutralna = True
                            print("Drukowanie zakończone!")
                        elif command[0] == "RESET_BLAT_Z":
                            z_pos_blatu += command[1]
                        czas_ostatniego_kroku = teraz
                    except StopIteration:
                        drukowanie = False
                        generator = None
                        print("Drukowanie zakończone z wyjątkiem StopIteration.")

            if pozycja_neutralna:
                ustaw_pozycje_nautralna()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        Table(z_pos_blatu, y_pos_suwaka, x_pos_glowica)
        for x_c, y_c, z_c in cubes:
            glPushMatrix()
            glTranslatef(x_c, y_c, z_c + z_pos_blatu)
            glCallList(cube_display)
            glPopMatrix()

        if anim_usuwania:
            teraz = pygame.time.get_ticks()
            if teraz - czas_ostatniego_usuwania >= opoznienie_usuwania:
                if cubes:
                    removed = cubes.pop()
                    print(f"Usunięto kostkę: {removed}")
                    czas_ostatniego_usuwania = teraz
                else:
                    anim_usuwania = False
                    print("Wszystkie kostki usunięte.")

        # Renderowanie FPS i pozycji atramentu w dyszy
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, screen_width, 0, screen_height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


        # --- WYSWIETLANIE FPS ---
        fps_font = pygame.font.Font(None, 36)
        fps_text_surface = fps_font.render(f"FPS: {clock.get_fps():.2f}", True, (0, 0, 0), (255, 255, 255, 180))
        text_data = pygame.image.tostring(fps_text_surface, "RGBA", True)
        text_x = 10
        text_y = screen_height - fps_text_surface.get_height() - 10
        glRasterPos2i(text_x, text_y)
        glDrawPixels(fps_text_surface.get_width(), fps_text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        # --- WYŚWIETLANIE ATARMENTU ---
        ink_pos_font = pygame.font.Font(None, 28)
        ink_pos_text = f"Atrament XYZ: ({x_pos_glowica:.3f}, {y_pos_suwaka-stala_przesuniecia_atramentu:.3f}, {stala_przesuniecia_wzgledem_srodka:.3f})"
        ink_surface = ink_pos_font.render(ink_pos_text, True, (0, 0, 0), (255, 255, 255, 180))
        ink_text_data = pygame.image.tostring(ink_surface, "RGBA", True)
        ink_text_x = 10
        ink_text_y = text_y - ink_surface.get_height() - 5
        glRasterPos2i(ink_text_x, ink_text_y)
        glDrawPixels(ink_surface.get_width(), ink_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, ink_text_data)

        glEnable(GL_DEPTH_TEST) # Włącz ponownie test głębi
        glDisable(GL_BLEND) # Włącz ponownie oświetlenie
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60) # Ogranicza do maksymalnie 60 FPS

Main()