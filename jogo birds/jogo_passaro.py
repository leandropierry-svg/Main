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
        self.angulo_asa = 0
        self.obstaculos = []
        self.quadros = 0
        self.pontos = 0
        self.recorde = getattr(self, "recorde", 0)
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
        if self.passaro_y - 15 <= 0 or self.passaro_y + 15 >= CHAO:
            return True
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

    # ---------- desenho ----------

    def desenhar_ceu(self):
        # Gradiente simples de céu, feito com faixas horizontais.
        topo = (110, 190, 210)
        base = (200, 235, 235)
        passos = 40
        altura_faixa = CHAO / passos
        for i in range(passos):
            t = i / passos
            r = int(topo[0] + (base[0] - topo[0]) * t)
            g = int(topo[1] + (base[1] - topo[1]) * t)
            b = int(topo[2] + (base[2] - topo[2]) * t)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            y0 = i * altura_faixa
            self.canvas.create_rectangle(0, y0, LARGURA, y0 + altura_faixa + 1,
                                         fill=cor, outline="")

        # Sol
        self.canvas.create_oval(370, 45, 430, 105, fill="#fff2b0", outline="#ffe27a", width=3)

        # Nuvens (deslocam levemente com o tempo para dar sensação de profundidade)
        deslocamento = -(self.quadros * 0.4) % (LARGURA + 200) - 100
        for dx, dy, escala in [(0, 0, 1.0), (160, -25, 0.7), (300, 20, 0.85)]:
            cx = 90 + dx + deslocamento
            cy = 90 + dy
            self._nuvem(cx, cy, escala)

    def _nuvem(self, cx, cy, escala=1.0):
        for dx, dy, r in [(-35, 8, 26), (0, -5, 32), (35, 8, 24), (0, 15, 20)]:
            x = cx + dx * escala
            y = cy + dy * escala
            raio = r * escala
            self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio,
                                    fill="#ffffff", outline="")

    def _prancha_madeira(self, x0, y0, x1, y1, tom_claro, tom_medio, tom_escuro):
        """Desenha um bloco com textura de tábua de madeira (veios horizontais)."""
        if y1 <= y0:
            return
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=tom_medio, outline=tom_escuro, width=3)
        # Veios da madeira: linhas onduladas horizontais.
        largura = x1 - x0
        altura = y1 - y0
        n_veios = max(1, int(altura // 22))
        for i in range(1, n_veios + 1):
            fy = y0 + (altura * i) / (n_veios + 1)
            pontos = []
            passo = 8
            xx = x0 + 4
            while xx < x1 - 4:
                ondulacao = 2 if (int(xx) // passo) % 2 == 0 else -2
                pontos.extend([xx, fy + ondulacao])
                xx += passo
            if len(pontos) >= 4:
                self.canvas.create_line(*pontos, fill=tom_escuro, width=1, smooth=True)
        # Nós na madeira.
        random.seed(int(x0) * 7 + int(y0))
        for _ in range(max(1, int(altura // 90))):
            nx = random.uniform(x0 + 10, x1 - 10)
            ny = random.uniform(y0 + 10, y1 - 10)
            self.canvas.create_oval(nx - 4, ny - 4, nx + 4, ny + 4, outline=tom_escuro, width=2)
            self.canvas.create_oval(nx - 1.5, ny - 1.5, nx + 1.5, ny + 1.5, fill=tom_escuro, outline="")
        # Brilho sutil na borda esquerda para dar volume.
        self.canvas.create_line(x0 + 3, y0, x0 + 3, y1, fill=tom_claro, width=2)

    def desenhar_obstaculo(self, tubo):
        x = tubo["x"]
        topo = tubo["abertura_y"] - ABERTURA // 2
        base = tubo["abertura_y"] + ABERTURA // 2

        tom_claro = "#c99a5b"
        tom_medio = "#a9713a"
        tom_escuro = "#7a4c22"

        # Tronco superior e inferior com textura de madeira.
        self._prancha_madeira(x, 0, x + 65, topo, tom_claro, tom_medio, tom_escuro)
        self._prancha_madeira(x, base, x + 65, CHAO, tom_claro, tom_medio, tom_escuro)

        # "Boca" do tubo (parte mais larga, tipo tampo de madeira mais grosso).
        self._prancha_madeira(x - 6, topo - 20, x + 71, topo, "#d7ab6c", "#b47f42", "#7a4c22")
        self._prancha_madeira(x - 6, base, x + 71, base + 20, "#d7ab6c", "#b47f42", "#7a4c22")

    def desenhar_passaro(self):
        x, y = 113, self.passaro_y
        # Inclina o pássaro conforme a velocidade (sobe = nariz pra cima, cai = nariz pra baixo).
        inclinacao = max(-10, min(35, self.velocidade_y * 3.5))

        self.canvas.create_oval(x - 18, y - 14, x + 18, y + 14,
                                fill="#ffd83d", outline="#d59a18", width=2)
        # Asa (posição varia com o tempo para simular batimento).
        bate = abs((self.quadros // 4) % 6 - 3)
        self.canvas.create_oval(x - 18, y - 2 + bate, x + 1, y + 13 + bate,
                                fill="#f3b527", outline="#d59a18")
        self.canvas.create_oval(x + 5, y - 9, x + 13, y - 1, fill="white", outline="")
        self.canvas.create_oval(x + 8, y - 7, x + 12, y - 3, fill="#1e1e1e", outline="")
        self.canvas.create_polygon(x + 18, y - 3, x + 31, y + 3, x + 18, y + 8,
                                   fill="#f08029", outline="#bd5718")
        # sobrancelha, dá expressão de acordo com a inclinação
        self.canvas.create_line(x + 2, y - 10 + inclinacao * 0.05, x + 12, y - 12,
                                fill="#7a4c22", width=2)

    def desenhar_chao(self):
        self.canvas.create_rectangle(0, CHAO, LARGURA, ALTURA, fill="#d9bb62", outline="")
        self.canvas.create_rectangle(0, CHAO, LARGURA, CHAO + 8, fill="#71d44f", outline="")
        # Textura de grama/terra listrada, deslocando com o cenário.
        deslocamento = -(self.quadros * VELOCIDADE_OBSTACULOS) % 30
        xx = deslocamento - 30
        while xx < LARGURA:
            self.canvas.create_line(xx, CHAO + 10, xx + 15, ALTURA, fill="#c7a655", width=6)
            xx += 30

    def desenhar_hud(self):
        # Sombra atrás do texto para melhor leitura sobre o céu.
        texto = f"Pontos: {self.pontos}"
        self.canvas.create_text(LARGURA // 2 + 2, 37, text=texto,
                                fill="#00000055", font=("Arial", 22, "bold"))
        self.canvas.create_text(LARGURA // 2, 35, text=texto,
                                fill="white", font=("Arial", 22, "bold"))
        if self.recorde:
            self.canvas.create_text(LARGURA // 2, 62, text=f"Recorde: {self.recorde}",
                                    fill="white", font=("Arial", 12, "bold"))

        if self.terminou:
            self.canvas.create_rectangle(50, 230, 430, 365, fill="#17344a", outline="#ffd83d", width=3)
            self.canvas.create_text(LARGURA // 2, 270, text="Fim de jogo!",
                                    fill="#ffd83d", font=("Arial", 26, "bold"))
            self.canvas.create_text(LARGURA // 2, 305, text=f"Pontuação: {self.pontos}",
                                    fill="white", font=("Arial", 14))
            self.canvas.create_text(LARGURA // 2, 335, text="Clique ou pressione Espaço para recomeçar",
                                    fill="white", font=("Arial", 12))

    def desenhar(self):
        self.canvas.delete("all")
        self.desenhar_ceu()
        for tubo in self.obstaculos:
            self.desenhar_obstaculo(tubo)
        self.desenhar_chao()
        self.desenhar_passaro()
        self.desenhar_hud()

    # ---------- loop ----------

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
                self.recorde = max(self.recorde, self.pontos)
        self.desenhar()
        self.janela.after(16, self.atualizar)


if __name__ == "__main__":
    raiz = tk.Tk()
    JogoPassaro(raiz)
    raiz.mainloop()
