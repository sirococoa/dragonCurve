import pyxel

from copy import copy
import math
import random
from typing import TypeVar, Callable

N = TypeVar("N", int, float)

WINDOW_W = 256
WINDOW_H = 256

class Point:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.r = 10
        self.color = color

    def draw(self):
        pyxel.circb(self.x, self.y, self.r, self.color)

    def vector(self) -> list:
        return [self.x, self.y, 1]

    def __str__(self) -> str:
        return f"({self.x},{self.y})"
    
def create_point_from_vector(vector :list) -> Point:
    return Point(vector[0], vector[1])

class Line:
    def __init__(self, s :Point, t :Point, reverse :bool=False) -> None:
        self.s = s
        self.t = t
        self.reverse = reverse
    
    def draw(self):
        pyxel.line(self.s.x, self.s.y, self.t.x, self.t.y, self.t.color)

    def vector(self) -> list:
        return [self.t.x - self.s.x, self.t.y - self.s.y, 0]

    def over_area(self) -> bool:
        if not -WINDOW_W <= self.s.x <= WINDOW_W*2:
            return True
        if not -WINDOW_H <= self.s.y <= WINDOW_H*2:
            return True
        if not -WINDOW_W <= self.t.x <= WINDOW_W*2:
            return True
        if not -WINDOW_H <= self.t.y <= WINDOW_H*2:
            return True
        return False

    def __str__(self) -> str:
        return f"{self.s}->{self.t}"

class Transformer:
    def __init__(self, lines :list[Line]) -> None:
        self.lines = lines
        self.base = Line(lines[0].s, lines[-1].t)
    
    def transrate(self, target :Line) -> list[Line]:
        T1 = [[1, 0, -self.base.s.x], [0, 1, -self.base.s.y], [0, 0, 1]] # Translation matrix to move base.s -> (0, 0)
        targetVector = target.vector()
        baseVector = self.base.vector()
        theta = math.atan2(cross(baseVector, targetVector), inner(baseVector, targetVector))
        R = [[math.cos(theta), -math.sin(theta), 0], 
             [math.sin(theta), math.cos(theta), 0],
             [0, 0, 1]] # Rotation matrix to rotate base vector -> target vector
        scale = length(targetVector) / length(baseVector)
        S = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]] # Scale matrix to scale base -> target
        if target.reverse:
            tau = math.atan2(targetVector[1], targetVector[0])
            M = [[math.cos(2*tau), math.sin(2*tau), 0], 
                [math.sin(2*tau), -math.cos(2*tau), 0],
                [0, 0, 1]] # Reflection matrix to reflect symmetrically to the target vector
        else:
            M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        T2 = [[1, 0, target.s.x], [0, 1, target.s.y], [0, 0, 1]] # Translation matrix to move (0, 0) -> target
        T = product_matrix(T2, product_matrix(M, product_matrix(S, product_matrix(R, T1))))
        new_lines = []
        for line in self.lines:
            new_sv = product(T, line.s.vector())
            new_tv = product(T, line.t.vector())
            new_line = Line(Point(new_sv[0], new_sv[1], line.s.color), Point(new_tv[0], new_tv[1], line.t.color), line.reverse)
            new_lines.append(new_line)
        return new_lines

def finish_translate(line :Line) -> bool:
    return abs(int(line.s.x) - int(line.t.x)) + abs(int(line.s.y) - int(line.t.y)) <= 1

def product_matrix(A :list[list[N]], B :list[list[N]]) -> list[list[N]]:
    result = []
    BT = list(zip(*B))
    for row_A in A:
        row_result = []
        for column_B in BT:
            tmp = 0
            for a, b in zip(row_A, column_B):
                tmp += a*b
            row_result.append(tmp)
        result.append(row_result)
    return result

def product(A :list[list[N]], B: list[N]) -> list[N]:
    result = []
    for row_A in A:
        tmp = 0
        for a, b in zip(row_A, B):
            tmp += a*b
        result.append(tmp)
    return result

def inner(a :list[N], b :list[N]) -> N:
    return a[0]*b[0] + a[1]*b[1]

def cross(a :list[N], b :list[N]) -> N:
    return a[0]*b[1] - a[1]*b[0]

def length(a :list[N]) -> N:
    return math.sqrt(a[0]**2 + a[1]**2)

class Canvas:
    def __init__(self) -> None:
        self.dots = dict()

    def register_line(self, line :Line) -> None:
        sx, sy = int(line.s.x), int(line.s.y)
        tx, ty = int(line.t.x), int(line.t.y)
        dx, dy = sx - tx, sy - ty
        if abs(dx) >= abs(dy):
            if sx < tx:
                for x in range(sx, tx):
                    if dy / dx > 0:
                        y = int(dy / dx * (x - sx) + sy + 0.5)
                    else:
                        y = int(dy / dx * (x - sx) + sy - 0.5)
                    self.register_dots(x, y, line.t.color)
            else:
                for x in range(tx, sx):
                    if dy / dx > 0:
                        y = int(dy / dx * (x - sx) + sy + 0.5)
                    else:
                        y = int(dy / dx * (x - sx) + sy - 0.5)
                    self.register_dots(x, y, line.t.color)
        else:
            if sy < ty:
                for y in range(sy, ty):
                    if dx / dy > 0:
                        x = int(dx / dy * (y - sy) + sx + 0.5)
                    else:
                        x = int(dx / dy * (y - sy) + sx - 0.5)
                    self.register_dots(x, y, line.t.color)
            else:
                for y in range(ty, sy):
                    if dx / dy > 0:
                        x = int(dx / dy * (y - sy) + sx + 0.5)
                    else:
                        x = int(dx / dy * (y - sy) + sx - 0.5)
                    self.register_dots(x, y, line.t.color)

    def register_dots(self, x :int, y :int, color :int) -> None:
        self.dots[(x, y)] = color
    
    def draw(self) -> None:
        for pos, color in self.dots.items():
            pyxel.pset(pos[0], pos[1], color)

class Editor:
    def __init__(self) -> None:
        self.points = []
        self.block_area = lambda x, y: False
        self.color = 7

    def regist_block_area(self, block_area :Callable[[int, int], bool]) -> None:
        self.block_area = block_area
    
    def delete(self):
        if self.points:
            self.points.pop()

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, repeat=10) and not self.block_area(pyxel.mouse_x, pyxel.mouse_y):
            self.points.append(Point(pyxel.mouse_x, pyxel.mouse_y, self.color))
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT, repeat=10):
            self.delete()

    def generate(self) -> tuple[list[Point], list[Line]]:
        lines = []
        for i, pair in enumerate(zip(self.points, self.points[1:])):
            lines.append(Line(pair[0], pair[1], bool(i%2)))
        return self.points, lines

    def generatable(self) -> bool:
        return len(self.points) >= 3

    def next_color(self) -> None:
        self.color = (self.color + 1) % 16

    def draw(self):
        for point in self.points:
            point.draw()

class Panel:
    WIDTH = WINDOW_W
    HEIGHT = 50
    X = 0
    Y = WINDOW_H - HEIGHT
    MARGIN = 10
    COLOR = 14

    OPEN_BUTTON_SIZE = 30
    OPEN_BUTTON_X = WINDOW_W - OPEN_BUTTON_SIZE - MARGIN
    OPEN_BUTTON_Y = WINDOW_H - OPEN_BUTTON_SIZE - MARGIN
    OPEN_BUTTON_CLOLOR = 14
    CLOSE_BUTTON_SIZE = 30
    CLOSE_BUTTON_X = WINDOW_W - CLOSE_BUTTON_SIZE - MARGIN
    CLOSE_BUTTON_Y = WINDOW_H - CLOSE_BUTTON_SIZE - MARGIN
    CLOSE_BUTTON_CLOLOR = 8
    START_BUTTON_SIZE = 30
    START_BUTTON_X = CLOSE_BUTTON_X - START_BUTTON_SIZE - MARGIN
    START_BUTTON_Y = WINDOW_H - START_BUTTON_SIZE - MARGIN
    START_BUTTON_CLOLOR = 3
    COLOR_BUTTON_SIZE = 30
    COLOR_BUTTON_SIZE_OFFSET = 2
    COLOR_BUTTON_X = START_BUTTON_X - COLOR_BUTTON_SIZE - MARGIN
    COLOR_BUTTON_Y = WINDOW_H - COLOR_BUTTON_SIZE - MARGIN
    DELETE_BUTTON_SIZE = 30
    DELETE_BUTTON_X = COLOR_BUTTON_X - DELETE_BUTTON_SIZE - MARGIN
    DELETE_BUTTON_Y = WINDOW_H - DELETE_BUTTON_SIZE - MARGIN
    DELETE_BUTTON_CLOLOR = 1

    def __init__(self, app :'App', editor :Editor) -> None:
        self.app = app
        self.editor = editor
        self.hide = True
        self.open_button = Button(self.OPEN_BUTTON_X, self.OPEN_BUTTON_Y, self.OPEN_BUTTON_SIZE, self.click_open_button, self.draw_open_button)
        self.close_button = Button(self.CLOSE_BUTTON_X, self.CLOSE_BUTTON_Y, self.CLOSE_BUTTON_SIZE, self.click_close_button, self.draw_close_button, active=False)
        self.editor.regist_block_area(self.block_editor_open_button_area)
        self.panel_buttons = []
        self.panel_buttons.append(Button(self.START_BUTTON_X, self.START_BUTTON_Y, self.START_BUTTON_SIZE, self.click_start_button, self.draw_start_button, active=False))
        self.panel_buttons.append(Button(self.DELETE_BUTTON_X, self.DELETE_BUTTON_Y, self.DELETE_BUTTON_SIZE, self.click_delete_button, self.draw_delete_button, active=False))
        self.panel_buttons.append(Button(self.COLOR_BUTTON_X, self.COLOR_BUTTON_Y, self.COLOR_BUTTON_SIZE, self.click_color_button, self.draw_color_button, active=False))

    def reset(self) -> None:
        self.hide = True
        self.open_button.active()
        self.close_button.disactive()
        for button in self.panel_buttons:
            button.disactive()
        self.editor.regist_block_area(self.block_editor_open_button_area)

    def update(self) -> None:
        self.open_button.update()
        self.close_button.update()
        for button in self.panel_buttons:
            button.update()

    def draw(self):
        if not self.hide:
            pyxel.rect(self.X, self.Y, self.WIDTH, self.HEIGHT, self.COLOR)
        self.open_button.draw()
        self.close_button.draw()
        for button in self.panel_buttons:
            button.draw()

    def click_open_button(self):
        self.hide = False
        self.open_button.disactive()
        self.close_button.active()
        for button in self.panel_buttons:
            button.active()
        self.editor.regist_block_area(self.block_editor_panel_area)

    def click_close_button(self):
        self.reset()

    def click_start_button(self):
        self.app.start()

    def click_delete_button(self):
        self.editor.delete()
    
    def click_color_button(self):
        self.editor.next_color()

    def draw_open_button(self):
        pyxel.rect(self.OPEN_BUTTON_X, self.OPEN_BUTTON_Y, self.OPEN_BUTTON_SIZE, self.OPEN_BUTTON_SIZE, self.OPEN_BUTTON_CLOLOR)

    def draw_close_button(self):
        pyxel.rect(self.CLOSE_BUTTON_X, self.CLOSE_BUTTON_Y, self.CLOSE_BUTTON_SIZE, self.CLOSE_BUTTON_SIZE, self.CLOSE_BUTTON_CLOLOR)

    def draw_start_button(self):
        pyxel.rect(self.START_BUTTON_X, self.START_BUTTON_Y, self.START_BUTTON_SIZE, self.START_BUTTON_SIZE, self.START_BUTTON_CLOLOR)

    def draw_delete_button(self):
        pyxel.rect(self.DELETE_BUTTON_X, self.DELETE_BUTTON_Y, self.DELETE_BUTTON_SIZE, self.DELETE_BUTTON_SIZE, self.DELETE_BUTTON_CLOLOR)

    def draw_color_button(self):
        x = self.COLOR_BUTTON_X + self.COLOR_BUTTON_SIZE // 2
        y = self.COLOR_BUTTON_Y + self.COLOR_BUTTON_SIZE // 2
        r = self.COLOR_BUTTON_SIZE // 2 + self.COLOR_BUTTON_SIZE_OFFSET
        c = self.editor.color
        pyxel.circ(x, y, r, c)

    def block_editor_panel_area(self, x :int, y :int) -> bool:
        return 0 <= x - self.X <= self.WIDTH and 0 <= y - self.Y <= self.HEIGHT

    def block_editor_open_button_area(self, x :int, y :int) -> bool:
        return 0 <= x - self.OPEN_BUTTON_X <= self.OPEN_BUTTON_SIZE and 0 <= y - self.OPEN_BUTTON_Y <= self.OPEN_BUTTON_SIZE

class Button:
    DELAY = 10

    def __init__(self, x :int, y :int, size :int, click :Callable[[], None], drawf :Callable[[], None], active :bool=True) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.click = click
        self.drawf = drawf
        self._active = active
        self.delay_clount = 0

    def update(self) -> None:
        if self.delay_clount > 0:
            self.delay_clount -= 1
        if not self._active:
            return
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.delay_clount == 0:
            if 0 <= pyxel.mouse_x - self.x <= self.size and 0 <= pyxel.mouse_y - self.y <= self.size:
                self.click()
                self.delay_clount = self.DELAY

    def draw(self) -> None:
        if not self._active:
            return
        self.drawf()

    def active(self) -> None:
        self._active = True
        self.delay_clount = self.DELAY
    
    def disactive(self) -> None:
        self._active = False

class ResetButton(Button):
    MARGIN = 10
    SIZE = 30
    X = WINDOW_W - SIZE - MARGIN
    Y = WINDOW_H - SIZE - MARGIN
    CLOLOR = 13

    def __init__(self, app :'App') -> None:
        super().__init__(self.X, self.Y, self.SIZE, self.click, self.drawf)
        self.app = app

    def click(self):
        self.app.reset()

    def drawf(self):
        pyxel.rect(self.X, self.Y, self.SIZE, self.SIZE, self.CLOLOR)

class App:
    MAX_LINE_NUM = 5000
    MAX_PROCESS_NUM_PER_FRAME = 100

    def __init__(self):
        pyxel.init(WINDOW_W, WINDOW_H)
        pyxel.mouse(True)

        self.editor = Editor()
        self.panel = Panel(self, self.editor)
        self.reset_button = ResetButton(self)
        self.reset()

        pyxel.run(self.update, self.draw)

    def reset(self):
        self.state = "Edit"
        self.points = []
        self.lines = []
        self.line_queue = []
        self.transformer = None
        self.panel.reset()
        self.canvas = Canvas()
    
    def start(self):
        if self.editor.generatable():
            self.points, self.lines = self.editor.generate()
            self.state = "Translate"
            self.transformer = Transformer(self.lines)
            self.reset_button.active()

    def update(self):
        if self.state == "Edit":
            self.editor.update()
            self.panel.update()
            if pyxel.btnp(pyxel.KEY_SPACE, repeat=60):
                self.start()
        elif self.state == "Translate":
            self.reset_button.update()
            if pyxel.btnp(pyxel.KEY_R, repeat=60):
                self.reset()
            if not self.line_queue:
                if len(self.lines) > self.MAX_LINE_NUM:
                    sampled_lines = random.sample(self.lines, self.MAX_LINE_NUM)
                    for line in self.lines:
                        if line not in sampled_lines:
                            self.canvas.register_line(line)
                    self.lines = sampled_lines
                self.line_queue = copy(self.lines)
                self.lines = []
            for _ in range(self.MAX_PROCESS_NUM_PER_FRAME):
                if not self.line_queue:
                    break
                line = self.line_queue.pop()
                new_lines = self.transformer.transrate(line)
                for new_line in new_lines:
                    if new_line.over_area:
                        self.canvas.register_line(new_line)
                        continue
                    if finish_translate(new_line):
                        self.canvas.register_line(new_line)
                    else:
                        self.lines.append(new_line)
            print(len(self.lines), len(self.line_queue))
        else:
            pass

    def draw(self):
        pyxel.cls(0)
        if self.state == "Edit":
            self.editor.draw()
            self.panel.draw()
        elif self.state == "Translate":
            for line in self.lines:
                    line.draw()
            for line in self.line_queue:
                    line.draw()
            for point in self.points:
                point.draw()
            self.canvas.draw()
            self.reset_button.draw()
        else:
            pass

App()
