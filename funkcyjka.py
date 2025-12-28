import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Tworzymy bryłę podstawową - SZEŚCIAN o środku (0, 0, 0) i krawędzi długości 2 jednostek

vertices = ((-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), # lista 8 wierzchołków sześcianu
            (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)) 
edges = ((0, 6), (0, 3), (0, 4), (1, 2), (1, 5), (2, 3), #lista par indeksów wierzchołków, które tworzą krawędzie
         (2, 6), (3, 7), (4, 5), (4, 7), (5, 6), (6, 7))
faces = ((0, 1, 2 , 3), (4, 5, 6, 7), (0, 4, 7, 3), #lista czwórek indeksów wierzchołków tworzących ściany sześcianu
         (1, 5, 6, 2), (2, 6, 7, 3), (1, 5, 4, 0))

# Wektory normalne dla każdej ściany sześcianu
normals = [
    (-1, 0, 0),  # dla face (0,1,2,3)
    (1, 0, 0),   # dla face (4,5,6,7)
    (0, -1, 0),  # dla face (0,4,7,3)
    (0, 1, 0),   # dla face (1,5,6,2)
    (0, 0, 1),   # dla face (2,6,7,3)
    (0, 0, -1)   # dla face (1,5,4,0)
]

def rysuj(pos, size, color): # pozycja(x, y ,z) , rozmiar(długość, szerokość, wysokość), kolor(RGB)
    x, y, z = pos
    sx, sy, sz = size
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    
    glColor3fv(color) # Ustawienie koloru materiału (dzięki GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color + (1.0,))
    
    
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i]) # Ustawienie wektora normalnego dla ściany
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

    glBegin(GL_LINES)
    glColor3fv((0, 0, 0))  # krawędzie czarne
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

def rysuj_walec(pos, wysokosc, promien, kolor):
    x, y, z = pos
    glPushMatrix()
    glColor3fv(kolor) # Przesunięcie i ustawienie koloru.
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, kolor + (1.0,))
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0) # Przesuwa walec do pozycji. Rotacja -90 stopni wokół osi X sprawia, że walec "stoi" wzdłuż osi Y (domyślnie jest wzdłuż Z).

    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH) # nowa bryła - gładsza i ładniejsze światło

    # Dolne denko
    gluDisk(quad, 0, promien, 64, 1)
    # Ściany boczne
    gluCylinder(quad, promien, promien, wysokosc, 64, 64)
    # Górne denko (po przesunięciu)
    glTranslatef(0, 0, wysokosc)
    gluDisk(quad, 0, promien, 64, 1) # Przesuwa w górę (na wysokość walca) i rysuje drugą podstawę.

    gluDeleteQuadric(quad)
    glPopMatrix() # Usuwa tymczasową bryłę i przywraca poprzednią macierz.