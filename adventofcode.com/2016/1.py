import turtle



def traces(prev, curr):
    if prev < curr:
        return range(prev + 1, curr)
    return range(prev - 1, curr, -1)

def taxi_distance(x, y):
    return abs(x) + abs(y)

class Tracer:
    def __init__(self):
        self.visited = {}
        self.found_intersection = False

    def visit(self, x, y):
        pos = (x, y)
        if pos in self.visited and not self.found_intersection:
            print('intersection={},{} distance={}'.format(x, y, taxi_distance(x, y)))
            self.found_intersection = True
        self.visited[pos] = True

    def trace(self, begin_pos, end_pos):
        x1, y1 = begin_pos
        x2, y2 = end_pos

        if x1 == x2:
            for y in traces(y1, y2):
                self.visit(x1, y)
        else:
            for x in traces(x1, x2):
                self.visit(x, y1)
        self.visit(x2, y2)

if __name__ == '__main__':
    turtle.speed(0)

    input_str = 'R2, L5, L4, L5, R4, R1, L4, R5, R3, R1, L1, L1, R4, L4, L1, R4, L4, R4, L3, R5, R4, R1, R3, L1, L1, R1, L2, R5, L4, L3, R1, L2, L2, R192, L3, R5, R48, R5, L2, R76, R4, R2, R1, L1, L5, L1, R185, L5, L1, R5, L4, R1, R3, L4, L3, R1, L5, R4, L4, R4, R5, L3, L1, L2, L4, L3, L4, R2, R2, L3, L5, R2, R5, L1, R1, L3, L5, L3, R4, L4, R3, L1, R5, L3, R2, R4, R2, L1, R3, L1, L3, L5, R4, R5, R2, R2, L5, L3, L1, L1, L5, L2, L3, R3, R3, L3, L4, L5, R2, L1, R1, R3, R4, L2, R1, L1, R3, R3, L4, L2, R5, R5, L1, R4, L5, L5, R1, L5, R4, R2, L1, L4, R1, L1, L1, L5, R3, R4, L2, R1, R2, R1, R1, R3, L5, R1, R4'
    x = 0
    y = 0
    prev_pos = (x, y)
    pos = (x, y)
    visited = {prev_pos: True}

    tracer = Tracer()

    for direction,amount in ((instr[0], int(instr[1:])) for instr in input_str.split(', ')):
        if direction == 'R':
            turtle.right(90)
        else:
            turtle.left(90)
        turtle.forward(amount)
        x, y = turtle.position()
        x, y = round(x), round(y)
        pos = (x, y)
        tracer.trace(prev_pos, pos)
        prev_pos = pos
    print('x = {}, y = {}, distance = {}'.format(x, y, taxi_distance(x, y)))

