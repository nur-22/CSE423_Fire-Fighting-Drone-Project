from OpenGL.GL import *
from OpenGL.GLUT import *
from random import randint as rdn
import numpy as np
import math, random


inputTaken = False
inp = None
fireAt = None

# Human position
h_x0 = rdn(-980, -100)
h_y0 = -150
h_x1 = rdn(100, 980)
h_y1 = -150

# Windmill
rotate_deg_mill = 0

# Car
rotate_deg = 0

# Car Moving
c_x0 = 1300
c_y0 = -40

# Drone
d_x0 = -1300
d_y0 = 550

def draw_points(x, y, defult):
    glPointSize(defult)
    glBegin(GL_POINTS)
    glVertex2f(x ,y)
    glEnd()

def convert_and_draw_pixel(x, y, zone, default):
    if zone == 0:
        draw_points(x, y, default)
    if zone == 1:
        draw_points(y, x, default)
    if zone == 2:
        draw_points(-y, x, default)
    if zone == 3:
        draw_points(-x, y, default)
    if zone == 4:
        draw_points(-x, -y, default)
    if zone == 5:
        draw_points(-y, -x, default)
    if zone == 6:
        draw_points(y, -x, default)
    if zone == 7:
        draw_points(x, -y, default)

def draw_line_at_zone_0(x1, y1, x2, y2, zone, default):
    dx = x2 - x1
    dy = y2 - y1
    d = 2* dy - dx
    del_E = 2 * dy
    del_NE = 2 * (dy - dx)
    x = x1
    y = y1
    convert_and_draw_pixel(x, y, zone, default)
    while x < x2:
        if d < 0:
            d += del_E
            x += 1
        else:
            d += del_NE
            x += 1
            y += 1
        convert_and_draw_pixel(x, y, zone, default)

def draw_line(x1, y1, x2, y2, default=2):
    dx = x2 - x1
    dy = y2 - y1
    if (abs(dx) > abs(dy)):
        if dx >= 0:  # zone 0 or 7
            if dy >= 0:  # zone 0
                z = 0
                draw_line_at_zone_0(x1, y1, x2, y2, z, default)
            else:
                z = 7
                draw_line_at_zone_0(x1, -y1, x2, -y2, z, default)
        else:  # zone 3 or 4
            if dy >= 0:
                z = 3
                draw_line_at_zone_0(-x1, y1, -x2, y2, z, default)
            else:
                z = 4
                draw_line_at_zone_0(-x1, -y1, -x2, -y2, z, default)
    else:  # zone 1 or 2 or 5 or 6
        if dx >= 0:  # zone 1 or 6
            if dy >= 0:
                z = 1
                draw_line_at_zone_0(y1, x1, y2, x2, z, default)
            else:
                z = 6
                draw_line_at_zone_0(-y1, x1, -y2, x2, z, default)
        else:  # zone 2 or 5
            if dy >= 0:
                z = 2
                draw_line_at_zone_0(y1, -x1, y2, -x2, z, default)
            else:
                z = 5
                draw_line_at_zone_0(-y1, -x1, -y2, -x2, z, default)

def draw_8_way_points(x, y, x0, y0, full, default):
    draw_points(x + x0, y + y0, default)
    draw_points(y + x0, x + y0, default)
    draw_points(-y + x0, x + y0, default)
    draw_points(-x + x0, y + y0, default)
    if full:
        draw_points(y + x0, -x + y0, default)
        draw_points(x + x0, -y + y0, default)
        draw_points(-x + x0, -y + y0, default)
        draw_points(-y + x0, -x + y0, default)

def draw_one_circle(radius, x0, y0, full, default):
    d = 1 - radius
    x = 0
    y = radius

    draw_8_way_points(x, y, x0, y0, full, default)

    while x < y:
        if d < 0:
            d = d + 2 * x + 3
            x += 1
        else:
            d = d + 2 * x - 2 * y + 5
            x += 1
            y = y - 1

        draw_8_way_points(x, y, x0, y0, full, default)

def draw_circle(radius, x0, y0, full=True, default= 2):
    while radius > 0:
        draw_one_circle(radius, x0, y0, full, default)
        radius -= 1

def draw_building(center, width, height, view="Front"):
    left = center - width
    right = center + width

    draw_line(left, 0, right, 0)  # Bottom
    draw_line(left, 0, left, height)  # Left
    draw_line(right, 0, right, height)  # Right
    draw_line(left, height, right, height)  # Top
    lineHeight = height
    while lineHeight > 0:
        draw_line(left, lineHeight, right, lineHeight)
        lineHeight -= 1

    if view == "Front":
        designTop = height
        designRight = center + 50

        glColor3f(2 / 255, 161 / 255, 147 / 255)
        while designRight > left and designTop > 0:
            draw_line(left, designTop, designRight, designTop)
            designRight -= 3
            designTop -= 12

        glColor3f(2 / 255, 161 / 255, 147 / 255)
        draw_building(center + 125, 25, height, "Side")

def draw_human(x0, y0):
    headRadius = 15
    bodyLength = 40
    handLength = 20
    legLength = 20
    bodyStart = y0-headRadius
    bodyEnd = bodyStart-bodyLength

    draw_circle(headRadius, x0, y0, True) #Head
    draw_line(x0, bodyStart, x0, bodyEnd) #Body
    draw_line(x0, bodyStart, x0-handLength, bodyStart-handLength) #Left hand
    draw_line(x0, bodyStart, x0+handLength, bodyStart-handLength) #Right hand
    draw_line(x0, bodyEnd, x0-legLength, bodyEnd-legLength) #Left leg
    draw_line(x0, bodyEnd, x0+legLength, bodyEnd-legLength) #Right leg

def human_movement(x, y):
    global fireAt
    if abs(fireAt - x) <= 50:
        return x
    elif x < fireAt:
        tx = 100
        t = np.array([[1, 0, tx],
                      [0, 1, 0],
                      [0, 0, 1]])

        v1 = np.array([[x],
                       [y],
                       [1]])

        v11 = np.matmul(t, v1)
        return v11[0][0]
    else:
        tx = -50
        t = np.array([[1, 0, tx],
                      [0, 1, 0],
                      [0, 0, 1]])

        v1 = np.array([[x],
                       [y],
                       [1]])

        v11 = np.matmul(t, v1)
        return v11[0][0]

def rotation2(x, y, a, b, deg=45):
    c = math.cos(math.radians(deg))
    s = math.sin(math.radians(deg))
    e1 = a*(1-c) + b*s
    e2 = b*(1-c) - a*s
    r = np.array([[c, -s, e1],
                  [s, c, e2],
                  [0, 0, 1]])

    v1 = np.array([[x],
                   [y],
                   [1]])

    v11 = np.matmul(r, v1)
    return (v11[0][0], v11[1][0])

def draw_windmill(c, h):
    global rotate_deg_mill
    draw_line(c-10, 0, c-10, h)
    draw_line(c+10, 0, c+10, h)

    i = h
    while i > 0:
        draw_line(c-10, i, c+10, i)
        i -= 2

    draw_circle(20, c, h)

    glColor3f(27 / 255, 209 / 255, 209 / 255)
    x1, y1 = rotation2(c-75, h, c, h, rotate_deg_mill)
    x2, y2 = rotation2(c+75, h, c, h, rotate_deg_mill)
    draw_line(x1, y1, x2, y2, 4)

    rotate_deg_mill += 10
    if rotate_deg_mill == 360:
        rotate_deg_mill = 0

def draw_car(x0, y0):
    global rotate_deg
    top = y0 + 50
    right = x0 + 100
    bottom = y0 - 50
    left = x0 - 100

    glColor3f(237 / 255, 82 / 255, 71 / 255)
    draw_line(right, top, right, bottom) # Right side
    draw_line(left, top, left, bottom) # Left side
    draw_line(left, top, right, top) # Top side
    draw_line(left, bottom, right, bottom) # Bottom side

    while top > bottom:
        draw_line(left, top, right, top)
        top -= 1

    a1 = x0-50
    a2 = x0+50
    b = bottom

    glColor3f(166 / 255, 150 / 255, 149 / 255)
    draw_circle(25, a1, b)
    draw_circle(25, a2, b)

    glColor3f(255 / 237, 255 / 255, 0 / 255)
    # draw_line(a1, b+25, a1, b-25)

    x1, y1 = rotation2(a1, b+25, a1, b, rotate_deg)
    x2, y2 = rotation2(a1, b-25, a1, b, rotate_deg)
    draw_line(x1, y1, x2, y2)

    x1, y1 = rotation2(a2, b+25, a2, b, rotate_deg)
    x2, y2 = rotation2(a2, b-25, a2, b, rotate_deg)
    draw_line(x1, y1, x2, y2)

    rotate_deg += 45
    if rotate_deg == 360:
        rotate_deg = 0

def car_movement(x, y):
    tx = -50
    t = np.array([[1, 0, tx],
                [0, 1, 0],
                [0, 0, 1]])

    v1 = np.array([[x],
                  [y],
                  [1]])

    v11 = np.matmul(t, v1)
    return v11[0][0]

def road_striping(center, width):
    left = center - width
    right = center + width
    glColor3f(255 / 255, 255 / 255, 255 / 255)
    for i in range(-123, -127, -1):
        draw_line(left, i, right, i)

def draw_road():
    # Footpath GREEN COLOR
    glColor3f(50 / 255, 205 / 255, 50 / 255)
    for Y in range(0, -40, -1):
        draw_line(-1000, Y, 1000, Y)

    glColor3f(50 / 255, 205 / 255, 50 / 255)
    for Y in range(-206, -246, -1):
        draw_line(-1000, Y, 1000, Y)
    # road Striping
    for j in range(-1000, 1001, 200):
        road_striping(j, 25)

def draw_drone(x0, y0):
    global d_x0
    if d_x0==None:
        x0=fireAt
    g = 50

    draw_line(x0+g, y0+g, x0-g, y0+g)
    draw_line(x0-g, y0+g, x0 - g, y0-g)
    draw_line(x0 - g, y0-g, x0 + g, y0-g)
    draw_line(x0 + g, y0-g, x0+g, y0+g)

    draw_line(x0 + g, y0 + g, x0 + g+ g, y0 + g + g)
    draw_line(x0 - g, y0 + g, x0 - g- g, y0 + g + g)
    draw_line(x0 - g, y0 - g, x0 -g - g, y0 - g - g)
    draw_line(x0 + g, y0 - g, x0 + g + g, y0 - g - g)

    draw_circle(8, x0 + g+ g, y0 + g + g, True)
    draw_circle(8, x0 - g- g, y0 + g + g, True)
    draw_circle(8, x0 -g - g, y0 - g - g, True)
    draw_circle(8, x0 + g + g, y0 - g - g, True)

    draw_circle(10, x0 -25, y0 +25, True)
    draw_circle(10, x0 + 25, y0 + 25, True)

def drone_movement(x, y):
    global fireAt
    if d_x0 == None:
        x == fireAt

    if x < fireAt:   # left to right
        tx = 100
        t = np.array([[1, 0, tx],
                      [0, 1, 0],
                      [0, 0, 1]])

        v1 = np.array([[x],
                       [y],
                       [1]])

        v11 = np.matmul(t, v1)

        return v11[0][0]

def rain_movement():
    global d_x0, fireAt
    if d_x0 == None:
        d_x0 = fireAt
        glColor3f(0, 0, 1)

        for i in range(50):
            draw_points(fireAt, (random.randint(75, 500)), 3)
            draw_points(fireAt - 10, (random.randint(75, 500)), 3)
            draw_points(fireAt + 10, (random.randint(75, 500)), 3)
        for i in range(50):
            x = random.randint(10, 40)
            y = random.randint(70, 500)

            draw_line(fireAt - x, y, fireAt - x, y + 10)

            draw_line(fireAt + x, y, fireAt + x + 5, y - 5)
            draw_line(fireAt - x, y, fireAt - x + 5, y - 5)

def iterate():
    glViewport(0, 0, 1000, 1000)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1000, 1000, -1000, 1000, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    global inputTaken, inp, fireAt, h_x0, h_y0, h_x1, h_y1, c_x0, c_y0, d_x0, d_y0

    # Drawing buildings
    glColor3f(7 / 255, 245 / 255, 225 / 255)
    draw_building(-800, 100, 400)

    glColor3f(7 / 255, 245 / 255, 225 / 255)
    draw_building(0, 100, 600)

    glColor3f(7 / 255, 245 / 255, 225 / 255)
    draw_building(750, 100, 400)

    draw_road()

    # Taking input and set fire to the specific building
    glColor3f(250 / 237, 152 / 255, 5 / 255)
    if not inputTaken:
        inp = int(input("Fire broke out in building 1/2/3: "))
        inputTaken = True

    if inp == 1:
        draw_circle(100, -800, 0, False)  # r, x, y
        fireAt = -800
    elif inp == 2:
        draw_circle(100, 0, 0, False)  # r, x, y
        fireAt = 0
    elif inp == 3:
        fireAt = 750
        draw_circle(100, 750, 0, False)  # r, x, y

    # Drawing windmills
    glColor3f(150 / 237, 171 / 255, 171 / 255)
    draw_windmill(400, 200)
    glColor3f(150 / 237, 171 / 255, 171 / 255)
    draw_windmill(-400, 200)

    # Drawing car
    draw_car(c_x0, c_y0)

    # Drawing human
    glColor3f(255 / 237, 255 / 255, 255 / 255)
    draw_human(h_x0, h_y0)
    draw_human(h_x1, h_y1)

    draw_drone(d_x0, d_y0)
    rain_movement()

    glutSwapBuffers()

    # Human movement
    h_x0 = human_movement(h_x0, h_y0)
    h_x1 = human_movement(h_x1, h_y1)

    # Car movement
    c_x0 = car_movement(c_x0, c_y0)

    # Drone movement
    d_x0 = drone_movement(d_x0, d_y0)

    glutPostRedisplay()

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1000, 1000)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"OpenGL Coding Practice")
glutDisplayFunc(showScreen)

# glutIdleFunc(showScreen)
glutMainLoop()