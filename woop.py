import os
import sys


class WumpusWorld:
    def __init__(self):
        self.grid_size = 4
        self.agent_pos = [0, 0]
        self.agent_dir = 0
        self.wumpus_pos = [2, 0]
        self.pits = [[2, 2], [3, 1]]
        self.gold_pos = [1, 2]
        self.has_gold = False
        self.has_arrow = True
        self.wumpus_alive = True
        self.game_over = False
        self.won = False
        self.score = 0
        self.visited = [[False] * 4 for _ in range(4)]
        self.visited[0][0] = True
        self.safe_cells = set()
        self.safe_cells.add((0, 0))
        self.possible_wumpus = set()
        self.possible_pits = set()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_direction_name(self):
        dirs = ['Yukarı ↑', 'Sağ →', 'Aşağı ↓', 'Sol ←']
        return dirs[self.agent_dir]

    def perceive(self):
        percepts = []
        x, y = self.agent_pos

        if self.wumpus_alive:
            wx, wy = self.wumpus_pos
            if (abs(x - wx) == 1 and y == wy) or (abs(y - wy) == 1 and x == wx):
                percepts.append('Koku')

        for pit in self.pits:
            px, py = pit
            if (abs(x - px) == 1 and y == py) or (abs(y - py) == 1 and x == px):
                percepts.append('Esinti')
                break

        if not self.has_gold and x == self.gold_pos[0] and y == self.gold_pos[1]:
            percepts.append('Parıltı')

        return percepts

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        if y + 1 < 4: neighbors.append([x, y + 1])
        if x + 1 < 4: neighbors.append([x + 1, y])
        if y - 1 >= 0: neighbors.append([x, y - 1])
        if x - 1 >= 0: neighbors.append([x - 1, y])
        return neighbors

    def make_inferences(self, percepts):
        print("\n" + "=" * 60)
        print("AJAN ÇIKARIMLAR")
        print("=" * 60)

        x, y = self.agent_pos
        print(f" Mevcut Konum: ({x}, {y})")
        print(f" Yön: {self.get_direction_name()}")

        if not percepts:
            print("Algılanan: Hiçbir şey")
            print("Çıkarım: Bu kare tamamen güvenli!")
            print("Çıkarım: Komşu karelerde ne Wumpus ne de çukur var")

            for neighbor in self.get_neighbors(self.agent_pos):
                nx, ny = neighbor
                self.safe_cells.add((nx, ny))

        else:
            print(f"Algılanan: {', '.join(percepts)}")

            if 'Koku' in percepts:
                print("Çıkarım: WUMPUS komşu karelerin birinde!")
                print("Dikkat: Komşu karelere gitmeden önce ok atmayı düşün")
                neighbors = self.get_neighbors(self.agent_pos)
                for neighbor in neighbors:
                    nx, ny = neighbor
                    if (nx, ny) not in self.safe_cells:
                        self.possible_wumpus.add((nx, ny))
                if self.possible_wumpus:
                    print(f"Wumpus olabilecek kareler: {list(self.possible_wumpus)}")

            if 'Esinti' in percepts:
                print("Çıkarım: ÇUKUR komşu karelerin birinde!")
                print("Dikkat: Komşu karelere giderken dikkatli ol")
                neighbors = self.get_neighbors(self.agent_pos)
                for neighbor in neighbors:
                    nx, ny = neighbor
                    if (nx, ny) not in self.safe_cells:
                        self.possible_pits.add((nx, ny))
                if self.possible_pits:
                    print(f"Çukur olabilecek kareler: {list(self.possible_pits)}")

            if 'Parıltı' in percepts:
                print("Çıkarım: ALTIN bu karede!")
                print("Öneri: 'g' (Grab) komutu ile altını al")

        safe_list = [cell for cell in self.safe_cells if cell != tuple(self.agent_pos)]
        if safe_list:
            print(f"Bilinen güvenli kareler: {safe_list}")

        print("=" * 60)

    def display_world(self):
        print("\n" + "=" * 60)
        print("WUMPUS WORLD - OYUN DURUMU")
        print("=" * 60)

        for y in range(3, -1, -1):
            row = f"y={y} | "
            for x in range(4):
                cell = "    "

                if [x, y] == self.agent_pos:
                    symbols = ['↑', '→', '↓', '←']
                    cell = f" A{symbols[self.agent_dir]} "
                elif self.wumpus_alive and [x, y] == self.wumpus_pos:
                    cell = " W  "
                elif [x, y] in self.pits:
                    cell = " P  "
                elif not self.has_gold and [x, y] == self.gold_pos:
                    cell = " G  "

                elif self.visited[y][x]:
                    cell = " .  "

                row += f"[{cell}]"
            print(row)

        print("      " + "-" * 28)
        print("       x=0   x=1   x=2   x=3")

        print("\nDurum:")
        print(f"  Skor: {self.score}")
        print(f"  Konum: ({self.agent_pos[0]}, {self.agent_pos[1]})")
        print(f"  Yön: {self.get_direction_name()}")
        print(f"  Altın: {' Var' if self.has_gold else ' Yok'}")
        print(f"  Ok: {' Var' if self.has_arrow else ' Yok'}")
        print(f"  Wumpus: {' Canlı' if self.wumpus_alive else ' Ölü'}")

        print("\n Semboller:")
        print("  A↑→↓← : Ajan (yön ile)  |  W : Wumpus  |  P : Çukur  |  G : Altın  |  . : Ziyaret edilmiş")

    def move_forward(self):
        if self.game_over:
            print("\n  Oyun bitti, hareket edemezsin!")
            return False

        x, y = self.agent_pos
        new_x, new_y = x, y

        if self.agent_dir == 0:
            new_y += 1
        elif self.agent_dir == 1:
            new_x += 1
        elif self.agent_dir == 2:
            new_y -= 1
        else:
            new_x -= 1

        if new_x < 0 or new_x >= 4 or new_y < 0 or new_y >= 4:
            print("\n Duvardan çıkamazsın!")
            return False

        print(f"\n ({x}, {y}) -> ({new_x}, {new_y}) hareket edildi")

        self.agent_pos = [new_x, new_y]
        self.score -= 1
        self.visited[new_y][new_x] = True

        if [new_x, new_y] in self.pits:
            self.game_over = True
            self.score -= 1000
            print("\n ÇUKURA DÜŞTÜN! ÖLDÜN! ")
            return True

        if self.wumpus_alive and [new_x, new_y] == self.wumpus_pos:
            self.game_over = True
            self.score -= 1000
            print("\nWUMPUS SENI YEDİ! ÖLDÜN! ")
            return True

        return True

    def turn_left(self):
        if self.game_over:
            print("\n Oyun bitti!")
            return False
        self.agent_dir = (self.agent_dir - 1) % 4
        self.score -= 1
        print(f"\n Sola döndü. Yeni yön: {self.get_direction_name()}")
        return True

    def turn_right(self):
        if self.game_over:
            print("\n️  Oyun bitti!")
            return False
        self.agent_dir = (self.agent_dir + 1) % 4
        self.score -= 1
        print(f"\n Sağa döndü. Yeni yön: {self.get_direction_name()}")
        return True

    def grab(self):
        if self.game_over:
            print("\n️  Oyun bitti!")
            return False

        if self.has_gold:
            print("\n️  Zaten altını aldın!")
            return False

        if self.agent_pos == self.gold_pos:
            self.has_gold = True
            self.score -= 1
            print("\n ALTINI ALDIN! ")
            print(" Şimdi başlangıç noktasına (0,0) dön ve çık!")
            return True
        else:
            print("\n Burada altın yok!")
            return False

    def shoot(self):
        if self.game_over:
            print("\n️  Oyun bitti!")
            return False

        if not self.has_arrow:
            print("\n Okun kalmadı!")
            return False

        self.has_arrow = False
        self.score -= 10

        x, y = self.agent_pos
        wx, wy = self.wumpus_pos
        hit = False

        if self.wumpus_alive:
            if self.agent_dir == 0 and wx == x and wy > y:
                hit = True
            elif self.agent_dir == 1 and wy == y and wx > x:
                hit = True
            elif self.agent_dir == 2 and wx == x and wy < y:
                hit = True
            elif self.agent_dir == 3 and wy == y and wx < x:
                hit = True

        if hit:
            self.wumpus_alive = False
            self.safe_cells.add(tuple(self.wumpus_pos))
            print("\n WUMPUS'U ÖLDÜRDÜN! ")
            print(" Artık Wumpus'un bulunduğu kare güvenli!")
        else:
            print("\n ISKALADIN! Okun bitti.")
        return True

    def climb(self):
        if self.game_over:
            print("\n️  Oyun bitti!")
            return False

        if self.agent_pos == [0, 0]:
            self.game_over = True
            if self.has_gold:
                self.score += 1000
                self.won = True
                print("\n TEBRİKLER! KAZANDIN! ")
                print(f" Altınla birlikte çıktın! Final Skor: {self.score}")
            else:
                print("\n Mağaradan çıktın ama altın olmadan...")
                print(f" Final Skor: {self.score}")
            return True
        else:
            print("\n Sadece başlangıç noktasından (0,0) çıkabilirsin!")
            return False

    def play(self):
        print("\n" + "=" * 60)
        print(" WUMPUS WORLD OYUNUNA HOŞ GELDİNİZ ")
        print("=" * 60)
        print("\n OYUN KURALLARI:")
        print("   Hedef: Altını bul, al ve başlangıç noktasına dön")
        print("   Altını almak: +1000 puan")
        print("   Ölmek (Wumpus/Çukur): -1000 puan")
        print("  ️ Her hareket: -1 puan")
        print("   Ok atmak: -10 puan")
        print("\n KOMUTLAR:")
        print("  f - İleri git")
        print("  l - Sola dön")
        print("  r - Sağa dön")
        print("  g - Altını al (Grab)")
        print("  s - Ok at (Shoot)")
        print("  c - Çık (Climb - sadece 0,0'da)")
        print("  q - Oyundan çık")
        print("\n" + "=" * 60)
        input("\nBaşlamak için Enter'a bas...")

        while not self.game_over:
            self.clear_screen()
            self.display_world()

            percepts = self.perceive()
            self.make_inferences(percepts)

            command = input("\n Komut gir (f/l/r/g/s/c/q) Enter'a bastıktan sonra tekrar Enter'a basmalısın:  ").lower().strip()

            action_taken = False

            if command == 'f':
                action_taken = self.move_forward()
            elif command == 'l':
                action_taken = self.turn_left()
            elif command == 'r':
                action_taken = self.turn_right()
            elif command == 'g':
                action_taken = self.grab()
            elif command == 's':
                action_taken = self.shoot()
            elif command == 'c':
                action_taken = self.climb()
            elif command == 'q':
                print("\n Oyundan çıkılıyor...")
                break
            else:
                print("\n Geçersiz komut!")

            if not self.game_over and command != 'q':
                input("\nDevam etmek için Enter'a bas...")

        if self.game_over:
            input("\nDevam etmek için Enter'a bas...")
            self.clear_screen()
            self.display_world()
            print("\n" + "=" * 60)
            print(" OYUN BİTTİ!")
            print("=" * 60)
            print(f"\n Final Skor: {self.score}")
            if self.won:
                print(" KAZANDIN! Harika bir performans!")
            else:
                print(" Kaybettin. Tekrar dene!")

if __name__ == "__main__":
    game = WumpusWorld()
    game.play()