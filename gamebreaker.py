import tkinter as tk

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 6
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='pink', outline='green', width=2)
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 120
        self.height = 10
        self.ball = None
        self.move_speed = 0
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#47e7d1', outline='#ebf576', width=2)
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def start_move(self, direction):
        self.move_speed = direction

    def stop_move(self):
        self.move_speed = 0

    def update(self):
        if self.move_speed != 0:
            coords = self.get_position()
            width = self.canvas.winfo_width()
            if coords[0] + self.move_speed >= 0 and coords[2] + self.move_speed <= width:
                self.move(self.move_speed, 0)
                if self.ball is not None:
                    self.ball.move(self.move_speed, 0)

class Brick(GameObject):
    def __init__(self, canvas, x, y, hits, color):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.points = 10  # Tambahkan poin untuk setiap brick
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline='white', tags='brick')
        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            game.score += self.points  # Tambahkan skor
            if game.score > game.high_score:
                game.high_score = game.score
            game.update_hud()  # Perbarui tampilan HUD


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#e747c8',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()

        self.hud = None
        self.heart_icons = []
        self.end_text = None
        self.text = None
        self.setup_game()
        self.canvas.focus_set()
        self.bind_controls()

    def bind_controls(self):
        self.canvas.bind('<Left>', lambda _: self.paddle.start_move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.start_move(10))
        self.canvas.bind('<KeyRelease>', lambda _: self.paddle.stop_move())

    def setup_game(self):
        self.add_ball()
        self.update_hud()

        # Pastikan semua teks dihapus sebelum menampilkan teks baru
        if self.text:
            self.canvas.delete(self.text)
            self.text = None
        if self.end_text:
            self.canvas.delete(self.end_text)
            self.end_text = None

        self.text = self.draw_text(300, 200, 'Tekan Untuk Mulai', size=24)
        self.canvas.bind('<space>', lambda _: self.start_game())
        
    def create_bricks(self):
        row_colors = ['#e79047', '#7ced77', '#77d1ed', '#e6fa6a', '#fa6ac0']
        for row_index, y in enumerate(range(50, 110, 20)):
            color = row_colors[row_index % len(row_colors)]
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, y, 1, color)

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits, color):
        brick = Brick(self.canvas, x, y, hits, color)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Times New Roman', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='white')

    def update_hud(self):
        for heart in self.heart_icons:
            self.canvas.delete(heart)
        self.heart_icons = []
        for i in range(self.lives):
            x = 10 + i * 30
            y = 10
            heart = self.canvas.create_text(x, y, text="♥", font=("Helvetica", 20), fill="black")
            self.heart_icons.append(heart)

        hud_text = f'Skor: {self.score} | Skor Tertinggi: {self.high_score}'
        if self.hud is None:
            self.hud = self.draw_text(300, 20, hud_text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=hud_text)
            
            
    def start_game(self):
        if self.text:
            self.canvas.delete(self.text)
            self.text = None
        if self.end_text:
            self.canvas.delete(self.end_text)
            self.end_text = None

        self.canvas.unbind('<space>')
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))

        if num_bricks == 0:
            self.ball.speed = None
            if self.text:
                self.canvas.delete(self.text)
            self.end_text = self.draw_text(300, 200, 'Kamu Menang', size=24)
            self.after(2000, self.reset_game)
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            self.update_hud()
            if self.lives == 0:
                if self.text:
                    self.canvas.delete(self.text)
                self.end_text = self.draw_text(300, 200, 'Kamu Kalah!', size=24)
                self.after(2000, self.reset_game)
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.paddle.update()
            self.after(16, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

    def reset_game(self):
        self.lives = 3
        self.score = 0
        self.update_hud()
        self.canvas.delete('brick')
        self.create_bricks()
        self.setup_game()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker')
    game = Game(root)
    game.mainloop()
