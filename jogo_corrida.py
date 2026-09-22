import random
import tkinter as tk


LARGURA, ALTURA = 480, 640

# Pista
LARGURA_PISTA = 300
METADE_PISTA = LARGURA_PISTA // 2
FAIXA_ACOSTAMENTO = 22

# Velocidade do carro do jogador
VEL_MIN = 1.5
VEL_MIN_NATURAL = 3.0      # velocidade "de cruzeiro" para onde o carro tende a voltar
VEL_MAX_BASE = 8.5
VEL_MAX_TETO = 13.5        # limite absoluto que a dificuldade pode alcançar
ACELERACAO = 0.10
FREIO = 0.16
ATRITO_NATURAL = 0.05

# Direção
ESTERCO_BASE = 3.6

# Carro do jogador (dimensões)
CARRO_LARGURA = 34
CARRO_ALTURA = 54


class JogoCorrida:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Corrida Clássica")
        self.janela.resizable(False, False)
        self.canvas = tk.Canvas(janela, width=LARGURA, height=ALTURA,
                                highlightthickness=0, bg="#3a8f3a")
        self.canvas.pack()

        self.teclas = set()
        self.janela.bind("<KeyPress>", self._tecla_pressionada)
        self.janela.bind("<KeyRelease>", self._tecla_solta)
        self.canvas.bind("<Button-1>", self._clique)
        self.canvas.focus_set()

        self.reiniciar()
        self.atualizar()

    # ---------- controle de teclado ----------

    def _tecla_pressionada(self, evento):
        self.teclas.add(evento.keysym)
        if self.terminou and evento.keysym == "space":
            self.reiniciar()

    def _tecla_solta(self, evento):
        self.teclas.discard(evento.keysym)

    def _clique(self, _evento=None):
        if self.terminou:
            self.reiniciar()

    # ---------- estado ----------

    def reiniciar(self):
        self.recorde = getattr(self, "recorde", 0)

        self.jogador_offset = 0.0
        self.velocidade = VEL_MIN_NATURAL
        self.velocidade_max = VEL_MAX_BASE

        self.desvio_atual = 0.0
        self.desvio_alvo = 0.0
        self.proxima_curva_em = 500

        self.distancia = 0.0
        self.pontos = 0
        self.combustivel = 100.0

        self.obstaculos = []
        self.itens = []
        self.proximo_obstaculo_em = 300.0
        self.proximo_item_em = 900.0

        self.quadros = 0
        self.quadros_na_grama = 0
        self.terminou = False
        self.motivo_fim = ""

    # ---------- geração de conteúdo ----------

    def _posicoes_livres(self, ocupadas, largura_min=70):
        """Sorteia um deslocamento dentro da pista que não colida com posições já usadas."""
        for _ in range(12):
            desloc = random.uniform(-METADE_PISTA + 45, METADE_PISTA - 45)
            if all(abs(desloc - o) > largura_min for o in ocupadas):
                return desloc
        return random.uniform(-METADE_PISTA + 45, METADE_PISTA - 45)

    def gerar_obstaculo(self):
        ocupadas = [o["desloc"] for o in self.obstaculos if o["y"] < 140]
        desloc = self._posicoes_livres(ocupadas)
        tipo = random.choices(["carro", "caminhao"], weights=[3, 1])[0]
        cores = ["#3a6fd8", "#d83a3a", "#d8b23a", "#8a3ad8", "#3ad8c4", "#e07a2b"]
        self.obstaculos.append({
            "desloc": desloc,
            "y": -80.0,
            "tipo": tipo,
            "cor": random.choice(cores),
            "vel_propria": random.uniform(1.0, 3.2),  # tráfego mais lento que você
        })

    def gerar_item(self):
        ocupadas = [o["desloc"] for o in self.obstaculos if o["y"] < 140]
        desloc = self._posicoes_livres(ocupadas)
        self.itens.append({"desloc": desloc, "y": -60.0})

    # ---------- física / regras ----------

    def atualizar_direcao_e_velocidade(self):
        esterco = ESTERCO_BASE + (self.velocidade - VEL_MIN_NATURAL) * 0.12
        if "Left" in self.teclas:
            self.jogador_offset -= esterco
        if "Right" in self.teclas:
            self.jogador_offset += esterco

        limite_grama = METADE_PISTA + FAIXA_ACOSTAMENTO + 55
        self.jogador_offset = max(-limite_grama, min(limite_grama, self.jogador_offset))

        fora_da_pista = abs(self.jogador_offset) > METADE_PISTA - 6

        if "Up" in self.teclas:
            self.velocidade += ACELERACAO
        elif "Down" in self.teclas:
            self.velocidade -= FREIO
        else:
            # tende naturalmente à velocidade de cruzeiro
            if self.velocidade > VEL_MIN_NATURAL:
                self.velocidade -= ATRITO_NATURAL
            elif self.velocidade < VEL_MIN_NATURAL:
                self.velocidade += ATRITO_NATURAL

        if fora_da_pista:
            self.velocidade -= 0.10  # atrito extra da grama
            self.quadros_na_grama += 1
        else:
            self.quadros_na_grama = 0

        self.velocidade = max(VEL_MIN, min(self.velocidade_max, self.velocidade))

        if self.quadros_na_grama > 55:
            self.terminou = True
            self.motivo_fim = "Você saiu da pista!"

    def atualizar_curva(self):
        if self.distancia >= self.proxima_curva_em:
            margem = METADE_PISTA + FAIXA_ACOSTAMENTO + 10
            self.desvio_alvo = random.uniform(-(LARGURA / 2 - margem), LARGURA / 2 - margem)
            self.proxima_curva_em = self.distancia + random.uniform(450, 950)
        self.desvio_atual += (self.desvio_alvo - self.desvio_atual) * 0.02

    def atualizar_dificuldade(self):
        self.velocidade_max = min(VEL_MAX_TETO, VEL_MAX_BASE + self.distancia / 2800)

    def atualizar_obstaculos_e_itens(self):
        self.proximo_obstaculo_em -= self.velocidade
        if self.proximo_obstaculo_em <= 0:
            self.gerar_obstaculo()
            intervalo_base = max(140, 340 - self.distancia / 20)
            self.proximo_obstaculo_em = random.uniform(intervalo_base * 0.7, intervalo_base * 1.3)

        self.proximo_item_em -= self.velocidade
        if self.proximo_item_em <= 0:
            self.gerar_item()
            self.proximo_item_em = random.uniform(700, 1300)

        centro_pista = LARGURA / 2 + self.desvio_atual

        for obs in self.obstaculos:
            obs["y"] += max(0.4, self.velocidade - obs["vel_propria"])
        self.obstaculos = [o for o in self.obstaculos if o["y"] < ALTURA + 100]

        for item in self.itens:
            item["y"] += self.velocidade
        self.itens = [i for i in self.itens if i["y"] < ALTURA + 60]

        # colisão com obstáculos
        py = ALTURA - 110
        px = centro_pista + self.jogador_offset
        for obs in self.obstaculos:
            largura_o = 40 if obs["tipo"] == "carro" else 50
            altura_o = 58 if obs["tipo"] == "carro" else 78
            ox = centro_pista + obs["desloc"]
            if (abs(px - ox) < (CARRO_LARGURA + largura_o) / 2 - 6 and
                    abs(py - obs["y"]) < (CARRO_ALTURA + altura_o) / 2 - 6):
                self.terminou = True
                self.motivo_fim = "Colisão!"

        # coleta de itens de combustível
        restantes = []
        for item in self.itens:
            ix = centro_pista + item["desloc"]
            if abs(px - ix) < 30 and abs(py - item["y"]) < 34:
                self.combustivel = min(100.0, self.combustivel + 28)
                self.pontos += 50
            else:
                restantes.append(item)
        self.itens = restantes

    def atualizar_pontuacao_e_combustivel(self):
        self.distancia += self.velocidade
        self.pontos += int(self.velocidade * 0.15)
        self.combustivel -= self.velocidade * 0.018
        if self.combustivel <= 0:
            self.combustivel = 0
            self.terminou = True
            self.motivo_fim = "Sem combustível!"

    # ---------- desenho ----------

    def cor_ceu(self):
        ciclo = (self.distancia % 7000) / 7000
        paletas = [
            ((120, 190, 235), (200, 230, 245)),  # dia
            ((235, 150, 110), (255, 210, 150)),  # entardecer
            ((35, 40, 80), (70, 75, 120)),       # noite
            ((235, 150, 110), (255, 210, 150)),  # amanhecer
        ]
        posicao = ciclo * len(paletas)
        indice = int(posicao) % len(paletas)
        prox = (indice + 1) % len(paletas)
        t = posicao - int(posicao)
        topo = tuple(int(paletas[indice][0][k] + (paletas[prox][0][k] - paletas[indice][0][k]) * t) for k in range(3))
        base = tuple(int(paletas[indice][1][k] + (paletas[prox][1][k] - paletas[indice][1][k]) * t) for k in range(3))
        return topo, base

    def desenhar_ceu_e_grama(self):
        topo, base = self.cor_ceu()
        faixas = 24
        for i in range(faixas):
            t = i / faixas
            r = int(topo[0] + (base[0] - topo[0]) * t)
            g = int(topo[1] + (base[1] - topo[1]) * t)
            b = int(topo[2] + (base[2] - topo[2]) * t)
            y0 = i * (ALTURA / faixas)
            self.canvas.create_rectangle(0, y0, LARGURA, y0 + ALTURA / faixas + 1,
                                         fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

        cor_grama_clara = "#3f9d3f"
        cor_grama_escura = "#357f35"
        fase = self.distancia % 40
        for base_y in range(-40, ALTURA + 40, 40):
            y = base_y - fase
            self.canvas.create_rectangle(0, y, LARGURA, y + 20, fill=cor_grama_escura, outline="")

    def desenhar_pista(self):
        centro = LARGURA / 2 + self.desvio_atual
        esq = centro - METADE_PISTA
        dir_ = centro + METADE_PISTA

        # acostamento (vermelho/branco tipo zebra)
        fase = self.distancia % 40
        for base_y in range(-40, ALTURA + 40, 40):
            y = base_y - fase
            cor = "#c94040" if (base_y // 40) % 2 == 0 else "#e8e8e8"
            self.canvas.create_rectangle(esq - FAIXA_ACOSTAMENTO, y, esq, y + 40, fill=cor, outline="")
            self.canvas.create_rectangle(dir_, y, dir_ + FAIXA_ACOSTAMENTO, y + 40, fill=cor, outline="")

        # asfalto
        self.canvas.create_rectangle(esq, 0, dir_, ALTURA, fill="#454545", outline="")

        # linhas de borda
        self.canvas.create_line(esq, 0, esq, ALTURA, fill="#f2f2f2", width=3)
        self.canvas.create_line(dir_, 0, dir_, ALTURA, fill="#f2f2f2", width=3)

        # linha central tracejada
        fase2 = self.distancia % 56
        for base_y in range(-56, ALTURA + 56, 56):
            y = base_y - fase2
            self.canvas.create_rectangle(centro - 4, y, centro + 4, y + 30,
                                         fill="#f2d94e", outline="")

    def _carro(self, x, y, largura, altura, cor_corpo, cor_vidro, virado_para_cima=True):
        self.canvas.create_rectangle(x - largura / 2, y - altura / 2, x + largura / 2, y + altura / 2,
                                     fill=cor_corpo, outline="#1c1c1c", width=2)
        vy = -altura * 0.12 if virado_para_cima else altura * 0.12
        self.canvas.create_rectangle(x - largura / 2 + 5, y - altura / 4 + vy,
                                     x + largura / 2 - 5, y + altura / 6 + vy,
                                     fill=cor_vidro, outline="")
        # rodas
        rw, rh = largura * 0.16, altura * 0.22
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx = x + sx * (largura / 2 - 2)
                cy = y + sy * (altura / 2 - rh / 2 - 3)
                self.canvas.create_rectangle(cx - rw / 2, cy - rh / 2, cx + rw / 2, cy + rh / 2,
                                             fill="#111111", outline="")
        # faróis / lanternas
        cor_luz = "#fff3b0" if virado_para_cima else "#e04040"
        ly = y - altura / 2 + 4 if virado_para_cima else y + altura / 2 - 4
        for sx in (-1, 1):
            lx = x + sx * (largura / 2 - 7)
            self.canvas.create_oval(lx - 3, ly - 3, lx + 3, ly + 3, fill=cor_luz, outline="")

    def desenhar_obstaculos(self):
        centro = LARGURA / 2 + self.desvio_atual
        for obs in self.obstaculos:
            x = centro + obs["desloc"]
            if obs["tipo"] == "carro":
                self._carro(x, obs["y"], 40, 58, obs["cor"], "#bfe4ff", virado_para_cima=False)
            else:
                self._carro(x, obs["y"], 50, 78, obs["cor"], "#d8d8d8", virado_para_cima=False)

    def desenhar_itens(self):
        centro = LARGURA / 2 + self.desvio_atual
        for item in self.itens:
            x = centro + item["desloc"]
            y = item["y"]
            self.canvas.create_rectangle(x - 12, y - 15, x + 12, y + 15,
                                         fill="#e8c93a", outline="#8a6d0e", width=2)
            self.canvas.create_text(x, y, text="C", fill="#5a4400", font=("Arial", 12, "bold"))

    def desenhar_jogador(self):
        centro = LARGURA / 2 + self.desvio_atual
        x = centro + self.jogador_offset
        y = ALTURA - 110
        self._carro(x, y, CARRO_LARGURA, CARRO_ALTURA, "#e02f2f", "#bfe4ff", virado_para_cima=True)

    def desenhar_hud(self):
        def texto_com_sombra(x, y, s, tam=14, cor="white", negrito=True):
            fonte = ("Arial", tam, "bold" if negrito else "normal")
            self.canvas.create_text(x + 1, y + 1, text=s, fill="#000000", font=fonte)
            self.canvas.create_text(x, y, text=s, fill=cor, font=fonte)

        texto_com_sombra(LARGURA / 2, 22, f"Pontos: {self.pontos}", 18)
        texto_com_sombra(LARGURA / 2, 44, f"Recorde: {self.recorde}", 12)

        vel_kmh = int(self.velocidade * 22)
        texto_com_sombra(70, ALTURA - 22, f"{vel_kmh} km/h", 13)

        # medidor de combustível
        bx0, by0, bx1, by1 = LARGURA - 130, ALTURA - 34, LARGURA - 20, ALTURA - 14
        self.canvas.create_rectangle(bx0, by0, bx1, by1, fill="#222222", outline="white", width=2)
        largura_fuel = (bx1 - bx0 - 4) * (self.combustivel / 100)
        cor_fuel = "#3ad83a" if self.combustivel > 30 else "#d83a3a"
        if largura_fuel > 0:
            self.canvas.create_rectangle(bx0 + 2, by0 + 2, bx0 + 2 + largura_fuel, by1 - 2,
                                         fill=cor_fuel, outline="")
        texto_com_sombra((bx0 + bx1) / 2, by0 - 10, "Combustível", 10)

        if self.terminou:
            self.canvas.create_rectangle(45, 235, 435, 400, fill="#17233a", outline="#f2d94e", width=3)
            texto_com_sombra(LARGURA / 2, 270, "Fim de jogo!", 24, "#f2d94e")
            texto_com_sombra(LARGURA / 2, 305, self.motivo_fim, 13)
            texto_com_sombra(LARGURA / 2, 335, f"Pontuação: {self.pontos}", 14)
            texto_com_sombra(LARGURA / 2, 370, "Espaço ou clique para recomeçar", 12, negrito=False)

    def desenhar(self):
        self.canvas.delete("all")
        self.desenhar_ceu_e_grama()
        self.desenhar_pista()
        self.desenhar_itens()
        self.desenhar_obstaculos()
        self.desenhar_jogador()
        self.desenhar_hud()

    # ---------- loop principal ----------

    def atualizar(self):
        if not self.terminou:
            self.quadros += 1
            self.atualizar_curva()
            self.atualizar_dificuldade()
            self.atualizar_direcao_e_velocidade()
            self.atualizar_obstaculos_e_itens()
            self.atualizar_pontuacao_e_combustivel()
            if self.terminou:
                self.recorde = max(self.recorde, self.pontos)
        self.desenhar()
        self.janela.after(16, self.atualizar)


if __name__ == "__main__":
    raiz = tk.Tk()
    JogoCorrida(raiz)
    raiz.mainloop()
