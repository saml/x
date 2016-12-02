import turtle

input_str = 'R2, L5, L4, L5, R4, R1, L4, R5, R3, R1, L1, L1, R4, L4, L1, R4, L4, R4, L3, R5, R4, R1, R3, L1, L1, R1, L2, R5, L4, L3, R1, L2, L2, R192, L3, R5, R48, R5, L2, R76, R4, R2, R1, L1, L5, L1, R185, L5, L1, R5, L4, R1, R3, L4, L3, R1, L5, R4, L4, R4, R5, L3, L1, L2, L4, L3, L4, R2, R2, L3, L5, R2, R5, L1, R1, L3, L5, L3, R4, L4, R3, L1, R5, L3, R2, R4, R2, L1, R3, L1, L3, L5, R4, R5, R2, R2, L5, L3, L1, L1, L5, L2, L3, R3, R3, L3, L4, L5, R2, L1, R1, R3, R4, L2, R1, L1, R3, R3, L4, L2, R5, R5, L1, R4, L5, L5, R1, L5, R4, R2, L1, L4, R1, L1, L1, L5, R3, R4, L2, R1, R2, R1, R1, R3, L5, R1, R4'

visited = {}
x = 0
y = 0

turtle.speed(0)

def taxi_distance(x, y):
    return abs(x) + abs(y)

for direction,amount in ((instr[0], int(instr[1:])) for instr in input_str.split(', ')):
    if direction == 'R':
        turtle.right(90)
    else:
        turtle.left(90)
    turtle.forward(amount)
    x, y = turtle.position()
    x, y = round(x), round(y)
    pos = (x, y)
    if pos in visited:
        print('intersection={} distance={}'.format(pos, taxi_distance(x, y)))
    visited[pos] = True

print('x = {}, y = {}, distance = {}'.format(x, y, taxi_distance(x, y)))
# $ python 1.py
# intersection=(106, 123) distance=229
# intersection=(99, 129) distance=228
# intersection=(99, 137) distance=236
# intersection=(102, 142) distance=244
# intersection=(98, 154) distance=252
# intersection=(94, 151) distance=245
# x = 90, y = 149, distance = 239

