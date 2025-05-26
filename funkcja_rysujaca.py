import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

vertices = ((-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1),#szescian - 8 wierzchołków
            (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)) 
edges = ((0, 6), (0, 3), (0, 4), (1, 2), (1, 5), (2, 3), #połączenie poszczegolnych wierzchołków
         (2, 6), (3, 7), (4, 5), (4, 7), (5, 6), (6, 7))
faces = ((0, 1, 2 , 3), (4, 5, 6, 7), (0, 4, 7, 3), #sciany
         (1, 5, 6, 2), (2, 6, 7, 3), (1, 5, 4, 0))


def rysuj(pos, size, color): #pozycja(x, y ,z) , rozmiar(szerokość, grubość, głębokość), kolor(RGB)
    x, y, z = pos
    sx, sy, sz = size
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glBegin(GL_QUADS)
    glColor3fv(color)
    for face in faces:
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
    glColor3fv(kolor)
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)  # Walec pionowy

    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)

    # Dolne denko
    gluDisk(quad, 0, promien, 64, 1)

    # Ściany boczne
    gluCylinder(quad, promien, promien, wysokosc, 64, 64)

    # Górne denko (po przesunięciu)
    glTranslatef(0, 0, wysokosc)
    gluDisk(quad, 0, promien, 64, 1)

    gluDeleteQuadric(quad)
    glPopMatrix()