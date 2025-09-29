import random
import pygame
import supabase
import os
from supabase import create_client, Client

# Configurações do Supabase
SUPABASE_URL = "https://uxagbrbcgzyqahqkdpbs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV4YWdicmJjZ3p5cWFocWtkcGJzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzI5MDc1OSwiZXhwIjoyMDcyODY2NzU5fQ.TFGARD7msT8whJ4c8Y9Q_FiNo8kTEILSp-y36LeNKbQ"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

pygame.init()

largura, altura = 400, 600
tela = pygame.display.set_mode((largura, altura))
clock = pygame.time.Clock()
# === Sistema de pontuação e tempo ===
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 24)
pontuacao = 0
tempo_inicio = pygame.time.get_ticks()
tempo_atual = 0

# === Carregar imagens ===
img_jogador = pygame.image.load("jogador.png")
img_jogador = pygame.transform.scale(img_jogador, (30, 40))  # Redimensiona

carros = [
    pygame.transform.scale(pygame.image.load("carro1.png"), (30, 40)),
    pygame.transform.scale(pygame.image.load("carro2.png"), (30, 40)),
    pygame.transform.scale(pygame.image.load("carro3.png"), (30, 40))
]

jogador = pygame.Rect(180, 500, 40, 40)
velocidade = 5
obstaculos = []

# Variável para armazenar o nome do jogador
nome_jogador = ""


def salvar_pontuacao(nome, pontuacao, tempo):
    try:
        data = supabase.table("ranking").insert({
            "nome": nome,
            "pontuacao": pontuacao,
            "tempo": tempo
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar pontuação: {e}")
        return False


def obter_top_pontuacoes():
    try:
        response = supabase.table("ranking") \
            .select("*") \
            .order("pontuacao", desc=True) \
            .limit(3) \
            .execute()
        return response.data
    except Exception as e:
        print(f"Erro ao obter pontuações: {e}")
        return []


def criar_obstaculo():
    x = random.randint(0, largura - 40)  # valor minimo e maximo menos o tamanho do bloco
    carro_img = random.choice(carros)  # Escolhe aleatoriamente uma das 3 imagens
    rect = pygame.Rect(x, -40, 40, 40)
    return {"rect": rect, "img": carro_img}  # Retorna dicionário com rect + imagem


def atualizar_pontuacao():
    global pontuacao, tempo_atual
    tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000  # Tempo em segundos
    pontuacao = tempo_atual * 10  # 10 pontos por segundo


def desenhar_interface():
    # Desenhar pontuação
    texto_pontuacao = fonte.render(f"Pontos: {pontuacao}", True, (255, 255, 255))
    tela.blit(texto_pontuacao, (10, 10))

    # Desenhar tempo
    minutos = tempo_atual // 60
    segundos = tempo_atual % 60
    texto_tempo = fonte.render(f"Tempo: {minutos:02d}:{segundos:02d}", True, (255, 255, 255))
    tela.blit(texto_tempo, (10, 50))


def reiniciar_jogo():
    global jogador, obstaculos, pontuacao, tempo_inicio, tempo_atual, nome_jogador
    jogador = pygame.Rect(180, 500, 40, 40)
    obstaculos = []
    pontuacao = 0
    tempo_inicio = pygame.time.get_ticks()
    tempo_atual = 0
    nome_jogador = ""


def desenhar_botao(texto, x, y, largura, altura, cor_normal, cor_hover, mouse_pos):
    cor = cor_hover if (x <= mouse_pos[0] <= x + largura and y <= mouse_pos[1] <= y + altura) else cor_normal
    pygame.draw.rect(tela, cor, (x, y, largura, altura))
    pygame.draw.rect(tela, (255, 255, 255), (x, y, largura, altura), 2)

    texto_botao = fonte.render(texto, True, (255, 255, 255))
    texto_x = x + (largura - texto_botao.get_width()) // 2
    texto_y = y + (altura - texto_botao.get_height()) // 2
    tela.blit(texto_botao, (texto_x, texto_y))


def desenhar_campo_texto(texto, x, y, largura, altura, ativo):
    cor = (100, 100, 100) if ativo else (70, 70, 70)
    pygame.draw.rect(tela, cor, (x, y, largura, altura))
    pygame.draw.rect(tela, (255, 255, 255), (x, y, largura, altura), 2)

    texto_surface = fonte.render(texto, True, (255, 255, 255))
    tela.blit(texto_surface, (x + 5, y + (altura - texto_surface.get_height()) // 2))

    if ativo:
        # Desenhar cursor piscante
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = x + 5 + texto_surface.get_width()
            pygame.draw.line(tela, (255, 255, 255),
                             (cursor_x, y + 5),
                             (cursor_x, y + altura - 5), 2)


def tela_digitar_nome():
    global nome_jogador
    nome_jogador = ""
    digitando = True
    campo_ativo = True

    while digitando:
        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if campo_ativo:
                    if evento.key == pygame.K_RETURN and nome_jogador.strip():
                        digitando = False
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    elif evento.key == pygame.K_ESCAPE:
                        return False
                    elif len(nome_jogador) < 15:
                        nome_jogador += evento.unicode
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                campo_rect = pygame.Rect(largura // 2 - 150, altura // 2, 300, 40)
                campo_ativo = campo_rect.collidepoint(mouse_pos)

        # Desenhar tela de digitar nome
        tela.fill((40, 40, 40))

        texto_titulo = fonte.render("DIGITE SEU NOME", True, (255, 255, 255))
        texto_instrucao = fonte_pequena.render("Pressione ENTER para continuar", True, (200, 200, 200))

        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, altura // 2 - 60))
        tela.blit(texto_instrucao, (largura // 2 - texto_instrucao.get_width() // 2, altura // 2 + 50))

        # Desenhar campo de texto
        desenhar_campo_texto(nome_jogador, largura // 2 - 150, altura // 2, 300, 40, campo_ativo)

        pygame.display.flip()
        clock.tick(60)

    return True


def tela_game_over():
    global rodando, nome_jogador

    # Salvar pontuação
    if nome_jogador:
        salvar_pontuacao(nome_jogador, pontuacao, tempo_atual)

    # Obter top 3 pontuações
    top_pontuacoes = obter_top_pontuacoes()

    botao_reiniciar_rect = (largura // 2 - 100, altura // 2 + 160, 200, 50)
    botao_sair_rect = (largura // 2 - 100, altura // 2 + 220, 200, 50)

    aguardando = True
    while aguardando:
        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                aguardando = False
                rodando = False
                return False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Botão esquerdo do mouse
                    if (botao_reiniciar_rect[0] <= mouse_pos[0] <= botao_reiniciar_rect[0] + botao_reiniciar_rect[2] and
                            botao_reiniciar_rect[1] <= mouse_pos[1] <= botao_reiniciar_rect[1] + botao_reiniciar_rect[
                                3]):
                        reiniciar_jogo()
                        aguardando = False
                        return True  # Reiniciar jogo
                    elif (botao_sair_rect[0] <= mouse_pos[0] <= botao_sair_rect[0] + botao_sair_rect[2] and
                          botao_sair_rect[1] <= mouse_pos[1] <= botao_sair_rect[1] + botao_sair_rect[3]):
                        aguardando = False
                        rodando = False
                        return False  # Sair do jogo

        # Desenhar tela de game over
        tela.fill((40, 40, 40))

        texto_game_over = fonte.render("GAME OVER!", True, (255, 0, 0))
        texto_pontuacao_final = fonte.render(f"Pontuação Final: {pontuacao}", True, (255, 255, 255))
        texto_tempo_final = fonte.render(f"Tempo: {tempo_atual // 60:02d}:{tempo_atual % 60:02d}", True,
                                         (255, 255, 255))

        tela.blit(texto_game_over, (largura // 2 - texto_game_over.get_width() // 2, altura // 2 - 150))
        tela.blit(texto_pontuacao_final, (largura // 2 - texto_pontuacao_final.get_width() // 2, altura // 2 - 110))
        tela.blit(texto_tempo_final, (largura // 2 - texto_tempo_final.get_width() // 2, altura // 2 - 70))

        # Desenhar ranking
        texto_ranking = fonte.render("TOP 3 PONTUAÇÕES", True, (255, 215, 0))
        tela.blit(texto_ranking, (largura // 2 - texto_ranking.get_width() // 2, altura // 2 - 30))

        for i, record in enumerate(top_pontuacoes):
            texto_record = fonte_pequena.render(
                f"{i + 1}. {record['nome']}: {record['pontuacao']} pts - {record['tempo'] // 60:02d}:{record['tempo'] % 60:02d}",
                True, (255, 255, 255)
            )
            tela.blit(texto_record, (largura // 2 - texto_record.get_width() // 2, altura // 2 + i * 25))

        # Desenhar botões
        desenhar_botao("REINICIAR", botao_reiniciar_rect[0], botao_reiniciar_rect[1],
                       botao_reiniciar_rect[2], botao_reiniciar_rect[3],
                       (0, 150, 0), (0, 200, 0), mouse_pos)

        desenhar_botao("SAIR", botao_sair_rect[0], botao_sair_rect[1],
                       botao_sair_rect[2], botao_sair_rect[3],
                       (150, 0, 0), (200, 0, 0), mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    return False


rodando = True
while rodando:
    tela.fill((40, 40, 40))  # cor da tela

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jogador.left > 0:
        jogador.x -= velocidade

    if teclas[pygame.K_RIGHT] and jogador.right < largura:
        jogador.x += velocidade

    if teclas[pygame.K_UP] and jogador.top > 0:
        jogador.y -= velocidade

    if teclas[pygame.K_DOWN] and jogador.bottom < altura:
        jogador.y += velocidade

    if random.randint(1, 30) == 1:
        obstaculos.append(criar_obstaculo())  # sorteia a criação de obstáculo

    for obstaculo in obstaculos:
        obstaculo["rect"].y += 5
        if obstaculo["rect"].colliderect(jogador):
            # Primeiro pede o nome do jogador
            if tela_digitar_nome():
                # Depois mostra a tela de game over
                if not tela_game_over():
                    rodando = False
                    break
            else:
                rodando = False
                break
        # Desenhar obstáculo
        tela.blit(obstaculo["img"], obstaculo["rect"])

    obstaculos = [obstaculo for obstaculo in obstaculos if
                  obstaculo["rect"].y < altura]  # remove o obstaculo que ultrapassar o altura da pag.

    # Atualizar pontuação e tempo
    atualizar_pontuacao()

    # Desenhar interface (pontuação e tempo)
    desenhar_interface()

    # Desenhar jogador
    tela.blit(img_jogador, jogador)
    # atualiza a tela
    pygame.display.flip()  # loop para ficar sempre aparecendo
    clock.tick(60)  # Frames por segundo

pygame.quit()