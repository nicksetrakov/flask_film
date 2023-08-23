class Elevator:
    def __init__(self, high=5, now=3):
        self.high = high
        self.now = now

    def up(self):
        if int(self.high) - int(self.now) <= 0:
            print('Лифт не может подняться выше')
        else:
            print(f'Лифт поднимается на {self.now + 1} этаж')
            self.now += 1

    def down(self):
        if self.now == 1:
            print('Лифт не может опуститься ниже')
        else:
            print(f'Лифт опускается на {self.now - 1} этаж')
            self.now -= 1


s = Elevator()
s.up()
s.up()
s.up()
s.down()
s.down()
s.down()
s.down()
s.down()
s.down()