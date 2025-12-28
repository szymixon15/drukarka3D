import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# tworzymy bryłę podstawową - SZEŚCIAN o środku (0, 0, 0) i krawędzi długości 2 jednostek

vertices = ((-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), # lista 8 wierzchołków sześcianu
            (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)) 
edges = ((0, 6), (0, 3), (0, 4), (1, 2), (1, 5), (2, 3), #lista par indeksów wierzchołków, które tworzą krawędzie
         (2, 6), (3, 7), (4, 5), (4, 7), (5, 6), (6, 7))
faces = ((0, 1, 2 , 3), (4, 5, 6, 7), (0, 4, 7, 3), #lista czwórek indeksów wierzchołków tworzących ściany sześcianu
         (1, 5, 6, 2), (2, 6, 7, 3), (1, 5, 4, 0))

# Wektory normalne dla każdej ściany sześcianu (w kolejności odpowiadającej 'faces')
# Upewnij się, że kolejność wierzchołków w 'faces' i te normalne są spójne (reguła prawej dłoni)
# Zakładając standardową kolejność wierzchołków (przeciwnie do ruchu wskazówek zegara patrząc z zewnątrz):
# Face (0,1,2,3): v0(-1,-1,-1), v1(-1,1,-1), v2(-1,1,1), v3(-1,-1,1) -> Normal pointing in -X: (-1, 0, 0)
# Face (4,5,6,7): v4(1,-1,-1), v5(1,1,-1), v6(1,1,1), v7(1,-1,1)   -> Normal pointing in +X: (1, 0, 0)
# Face (0,4,7,3): v0(-1,-1,-1), v4(1,-1,-1), v7(1,-1,1), v3(-1,-1,1) -> Normal pointing in -Y: (0, -1, 0)
# Face (1,5,6,2): v1(-1,1,-1), v5(1,1,-1), v6(1,1,1), v2(-1,1,1)   -> Normal pointing in +Y: (0, 1, 0)
# Face (2,6,7,3): v2(-1,1,1), v6(1,1,1), v7(1,-1,1), v3(-1,-1,1)   -> Normal pointing in +Z: (0, 0, 1)
# Face (1,5,4,0): v1(-1,1,-1), v5(1,1,-1), v4(1,-1,-1), v0(-1,-1,-1) -> Normal pointing in -Z: (0, 0, -1)
# Lub jeśli ostatnia ściana to (0,4,5,1) -> normal (0,0,-1)
normals = [
    (-1, 0, 0),  # dla face (0,1,2,3)
    (1, 0, 0),   # dla face (4,5,6,7)
    (0, -1, 0),  # dla face (0,4,7,3)
    (0, 1, 0),   # dla face (1,5,6,2)
    (0, 0, 1),   # dla face (2,6,7,3)
    (0, 0, -1)   # dla face (1,5,4,0) - lub ostatniej zdefiniowanej
]


def rysuj(pos, size, color): #pozycja(x, y ,z) , rozmiar(długość, szerokość, wysokość), kolor(RGB)
    x, y, z = pos
    sx, sy, sz = size
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    
    glColor3fv(color) # Ustawienie koloru materiału (dzięki GL_COLOR_MATERIAL)

    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i]) # Ustawienie wektora normalnego dla ściany
        for vertex_index in face:
            glVertex3fv(vertices[vertex_index])
    glEnd()

    # Krawędzie rysowane bez wpływu oświetlenia, aby były zawsze widoczne jako czarne
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3fv((0, 0, 0))  # krawędzie czarne
    for edge in edges:
        for vertex_index in edge:
            glVertex3fv(vertices[vertex_index])
    glEnd()
    glEnable(GL_LIGHTING) # Ponowne włączenie oświetlenia
    
    glPopMatrix()


#tworzymy walec pionowy


def rysuj_walec(pos, wysokosc, promien, kolor):
    x, y, z = pos
    glPushMatrix()
    glColor3fv(kolor) #Przesunięcie i ustawienie koloru.
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)  #Przesuwa walec do pozycji. Rotacja -90 stopni wokół osi X sprawia, że walec "stoi" wzdłuż osi Y (domyślnie jest wzdłuż Z).

    quad = gluNewQuadric() 
    gluQuadricNormals(quad, GLU_SMOOTH) #nowa bryła - gładsza i ładniejsze światło

    # Dolne denko
    gluDisk(quad, 0, promien, 64, 1) #Rysuje dolną podstawę (dysk o promieniu promien). 64 segmenty – dość gładka.

    # Ściany boczne
    gluCylinder(quad, promien, promien, wysokosc, 64, 64) #Rysuje ścianki boczne

    # Górne denko (po przesunięciu)
    glTranslatef(0, 0, wysokosc)
    gluDisk(quad, 0, promien, 64, 1) #Przesuwa w górę (na wysokość walca) i rysuje drugą podstawę.

    gluDeleteQuadric(quad)
    glPopMatrix() #Usuwa tymczasową bryłę i przywraca poprzednią macierz.