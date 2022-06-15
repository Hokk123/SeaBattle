from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Эта клетка за границей доски!"


class BoardRepeatException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли!"


class BoardWrongShipException(BoardException):
    pass


def hello():
    print("                     Игра Морской бой!")
    print("Инструкция:")
    print("Дано поле 6х6 клеток, нужно расставить свои корабли так, что бы")
    print("между ними была как минимум одна пустая клетка. Далее стрелять")
    print("по координатам врежеского поля. (x, y). Выиграет сильнейший!!!")
    print('''
    -------------------------------------------
       |  1  |  2  |  3  |  4  |  5  |  6  |
    1  |     |     |     |     |     |     |
    2  |     |     |     |     |     |     |
    3  |     |     |     |     |     |     |
    4  |     |     |     |     |     |     |
    5  |     |     |     |     |     |     |
    6  |     |     |     |     |     |     |
    ''')

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, nos, length, vector):
        self.nos = nos
        self.lenght = length
        self.vector = vector
        self.hits = length

    @property
    def points(self):
        ship_points = []
        for i in range(self.lenght):
            cur_x = self.nos.x
            cur_y = self.nos.y

            if self.vector == 0: #горизонтальное расположение корабля
                cur_x += i

            elif self.vector == 1: #вертикальное расположение корабля
                cur_y += i

            ship_points.append(Dot(cur_x, cur_y))

        return ship_points

    def fire(self, fire):
        return fire in self.points


class Board:
    def __init__(self, view=False, size=6):
        self.size = size
        self.view = view

        self.count = 0

        self.field = [[" "] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.points:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.points:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contur(ship)

    def contur(self, ship, verb = False):
        centr = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.points:
            for dx, dy in centr:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  |  1  |  2  |  3  |  4  |  5  |  6  |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} |  " + "  |  ".join(row) + "  |"

        if self.view:
            res = res.replace("■", " ")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, a):
        if self.out(a):
            raise BoardOutException()

        if a in self.busy:
            raise BoardRepeatException()

        self.busy.append(a)

        for ship in self.ships:
            if a in ship.points:
                ship.hits -= 1
                self.field[a.x][a.y] = "X"
                if ship.hits == 0:
                    self.count += 1
                    self.contur(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[a.x][a.y] = "o"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 500:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board


    def loop(self):
        num = 0
        while True:
            print("-" * 39)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 39)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 39)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 39)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 39)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 39)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.loop()

hello()
g = Game()
g.start()