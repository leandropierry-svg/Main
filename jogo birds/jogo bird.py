import random
import tkinter as tk


LARGURA, ALTURA = 480, 640
CHAO = 585
GRAVIDADE = 0.55
IMPULSO = -9.0
VELOCIDADE_OBSTACULOS = 3.2
INTERVALO_OBSTACULOS = 95
ABERTURA = 190


class JogoPassaro:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Pierre Voador")
        self.janela.resizable(False, False)
        self.canvas = tk.Canvas(janela, width=LARGURA, height=ALTURA,
                                highlightthickness=0, bg="#70c5ce")
        self.canvas.pack()
        self.janela.bind("<space>", self.bater_asas)
        self.canvas.bind("<Button-1>", self.bater_asas)
        self.reiniciar()
        self.atualizar()

    def reiniciar(self):
        self.passaro_y = ALTURA // 2
        self.velocidade_y = 0
        self.obstaculos = []
        self.quadros = 0
        self.pontos = 0
        self.terminou = False

    def bater_asas(self, _evento=None):
        if self.terminou:
            self.reiniciar()
        else:
            self.velocidade_y = IMPULSO

    def criar_obstaculo(self):
        abertura_y = random.randint(150, CHAO - 150)
        self.obstaculos.append({"x": LARGURA + 35, "abertura_y": abertura_y,
                                "marcou": False})

    def colidiu(self):
        # Limites vertical e chão.
        if self.passaro_y - 15 <= 0 or self.passaro_y + 15 >= CHAO:
            return True
        # Colisão do pássaro (aprox. 30x30) com cada tubo.
        px1, px2 = 98, 128
        py1, py2 = self.passaro_y - 15, self.passaro_y + 15
        for tubo in self.obstaculos:
            tx1, tx2 = tubo["x"], tubo["x"] + 65
            abertura_topo = tubo["abertura_y"] - ABERTURA // 2
            abertura_base = tubo["abertura_y"] + ABERTURA // 2
            sobrepoe_x = px2 > tx1 and px1 < tx2
            fora_da_abertura = py1 < abertura_topo or py2 > abertura_base
            if sobrepoe_x and fora_da_abertura:
                return True
        return False

    def desenhar(self):
        self.canvas.delete("all")
        # Nuvens decorativas.
        self.canvas.create_oval(35, 75, 130, 115, fill="#ffffff", outline="")
        self.canvas.create_oval(105, 55, 190, 115, fill="#ffffff", outline="")

        for tubo in self.obstaculos:
            x = tubo["x"]
            topo = tubo["abertura_y"] - ABERTURA // 2
            base = tubo["abertura_y"] + ABERTURA // 2
            self.canvas.create_rectangle(x, 0, x + 65, topo, fill="#58be3f", outline="#288c29", width=3)
            self.canvas.create_rectangle(x - 5, topo - 18, x + 70, topo, fill="#71d44f", outline="#288c29", width=3)
            self.canvas.create_rectangle(x, base, x + 65, CHAO, fill="#58be3f", outline="#288c29", width=3)
            self.canvas.create_rectangle(x - 5, base, x + 70, base + 18, fill="#71d44f", outline="#288c29", width=3)

        self.canvas.create_rectangle(0, CHAO, LARGURA, ALTURA, fill="#d9bb62", outline="#ac8736")
        # Pássaro: corpo, asa, olho e bico.
        x, y = 113, self.passaro_y
        self.canvas.create_oval(x - 18, y - 14, x + 18, y + 14, fill="#ffd83d", outline="#d59a18", width=2)
        self.canvas.create_oval(x - 18, y - 2, x + 1, y + 13, fill="#f3b527", outline="#d59a18")
        self.canvas.create_oval(x + 5, y - 9, x + 13, y - 1, fill="white", outline="")
        self.canvas.create_oval(x + 8, y - 7, x + 12, y - 3, fill="#1e1e1e", outline="")
        self.canvas.create_polygon(x + 18, y - 3, x + 31, y + 3, x + 18, y + 8, fill="#f08029", outline="#bd5718")
        self.canvas.create_text(LARGURA // 2, 35, text=f"Pontos: {self.pontos}",
                                fill="white", font=("Arial", 20, "bold"))
        if self.terminou:
            self.canvas.create_rectangle(55, 235, 425, 355, fill="#17344a", outline="white", width=2)
            self.canvas.create_text(LARGURA // 2, 275, text="Fim de jogo!", fill="white", font=("Arial", 26, "bold"))
            self.canvas.create_text(LARGURA // 2, 315, text="Clique ou pressione Espaço para recomeçar",
                                    fill="white", font=("Arial", 12))

    def atualizar(self):
        if not self.terminou:
            self.quadros += 1
            self.velocidade_y += GRAVIDADE
            self.passaro_y += self.velocidade_y
            if self.quadros % INTERVALO_OBSTACULOS == 0:
                self.criar_obstaculo()
            for tubo in self.obstaculos:
                tubo["x"] -= VELOCIDADE_OBSTACULOS
                if not tubo["marcou"] and tubo["x"] + 65 < 98:
                    tubo["marcou"] = True
                    self.pontos += 1
            self.obstaculos = [tubo for tubo in self.obstaculos if tubo["x"] > -75]
            if self.colidiu():
                self.terminou = True
        self.desenhar()
        self.janela.after(16, self.atualizar)


if __name__ == "__main__":
    raiz = tk.Tk()
    JogoPassaro(raiz)
    raiz.mainloop()