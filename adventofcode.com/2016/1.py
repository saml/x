import turtle

turtle.speed(0)

input_str = 'R2, L5, L4, L5, R4, R1, L4, R5, R3, R1, L1, L1, R4, L4, L1, R4, L4, R4, L3, R5, R4, R1, R3, L1, L1, R1, L2, R5, L4, L3, R1, L2, L2, R192, L3, R5, R48, R5, L2, R76, R4, R2, R1, L1, L5, L1, R185, L5, L1, R5, L4, R1, R3, L4, L3, R1, L5, R4, L4, R4, R5, L3, L1, L2, L4, L3, L4, R2, R2, L3, L5, R2, R5, L1, R1, L3, L5, L3, R4, L4, R3, L1, R5, L3, R2, R4, R2, L1, R3, L1, L3, L5, R4, R5, R2, R2, L5, L3, L1, L1, L5, L2, L3, R3, R3, L3, L4, L5, R2, L1, R1, R3, R4, L2, R1, L1, R3, R3, L4, L2, R5, R5, L1, R4, L5, L5, R1, L5, R4, R2, L1, L4, R1, L1, L1, L5, R3, R4, L2, R1, R2, R1, R1, R3, L5, R1, R4'

x = 0
y = 0
prev_pos = (x, y)
pos = (x, y)
visited = {prev_pos: True}

def traces(prev, curr):
    if prev < curr:
        return range(prev + 1, curr)
    return range(prev - 1, curr, -1)

def visit(x, y, visited):
    #print('{},{}'.format(x, y))
    if (x, y) in visited:
        print('intersection={},{} distance={}'.format(x, y, taxi_distance(x, y)))
    visited[(x, y)] = True

def trace(begin_pos, end_pos, visited):
    x1, y1 = begin_pos
    x2, y2 = end_pos

    if x1 == x2:
        for y in traces(y1, y2):
            visit(x1, y, visited)
    else:
        for x in traces(x1, x2):
            visit(x, y1, visited)
    #print('>', end='')
    visit(x2, y2, visited)

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
    trace(prev_pos, pos, visited)
    prev_pos = pos

print('x = {}, y = {}, distance = {}'.format(x, y, taxi_distance(x, y)))
'''
$ python 1.py
intersection=138,3 distance=141
intersection=113,140 distance=253
intersection=105,125 distance=230
intersection=106,125 distance=231
intersection=107,125 distance=232
intersection=108,125 distance=233
intersection=109,125 distance=234
intersection=109,123 distance=232
intersection=106,123 distance=229
intersection=106,124 distance=230
intersection=106,125 distance=231
intersection=105,128 distance=233
intersection=104,128 distance=232
intersection=104,127 distance=231
intersection=104,128 distance=232
intersection=99,128 distance=227
intersection=99,129 distance=228
intersection=96,130 distance=226
intersection=96,131 distance=227
intersection=96,132 distance=228
intersection=99,137 distance=236
intersection=99,142 distance=241
intersection=100,142 distance=242
intersection=101,142 distance=243
intersection=102,142 distance=244
intersection=94,154 distance=248
intersection=95,154 distance=249
intersection=96,154 distance=250
intersection=97,154 distance=251
intersection=98,154 distance=252
intersection=98,153 distance=251
intersection=96,151 distance=247
intersection=94,151 distance=245
intersection=94,150 distance=244
intersection=93,150 distance=243
x = 90, y = 149, distance = 239
'''
