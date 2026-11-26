import heapq
from collections import deque
import time

# ==========================================
# 1. ESTRUTURA BASE (O NÓ DE BUSCA)
# ==========================================
class No:
    def __init__(self, estado, pai=None, acao=None, custo_g=0, heuristica_h=0, apenas_heuristica=False):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.custo_g = custo_g
        self.heuristica_h = heuristica_h
        self.apenas_heuristica = apenas_heuristica

    @property
    def f(self):
        # Busca Gulosa avalia f(n) = h(n); A* avalia f(n) = g(n) + h(n)
        return self.heuristica_h if self.apenas_heuristica else (self.custo_g + self.heuristica_h)

    def __lt__(self, outro):
        return self.f < outro.f


def reconstruir_caminho(no):
    caminho = []
    while no:
        caminho.append((no.acao, no.estado))
        no = no.pai
    return caminho[::-1]


# ==========================================
# 2. ALGORITMOS DE BUSCA (ARQUITETURA UNIFICADA)
# ==========================================
def busca_bfs(estado_inicial, verifica_objetivo, gerar_sucessores):
    fronteira = deque([No(estado_inicial)])
    visitados = {estado_inicial}
    nos_expandidos = 0

    while fronteira:
        no = fronteira.popleft()
        nos_expandidos += 1

        if verifica_objetivo(no.estado):
            return reconstruir_caminho(no), no.custo_g, nos_expandidos

        for acao, filho_est, custo in gerar_sucessores(no.estado):
            if filho_est not in visitados:
                visitados.add(filho_est)
                fronteira.append(No(filho_est, no, acao, no.custo_g + custo))

    return None, 0, nos_expandidos


def busca_dfs(estado_inicial, verifica_objetivo, gerar_sucessores, limite_profundidade=None):
    fronteira = [(No(estado_inicial), 0)]
    visitados = set()
    nos_expandidos = 0

    while fronteira:
        no, prof = fronteira.pop()
        if no.estado in visitados:
            continue

        visitados.add(no.estado)
        nos_expandidos += 1

        if verifica_objetivo(no.estado):
            return reconstruir_caminho(no), no.custo_g, nos_expandidos

        if limite_profundidade is None or prof < limite_profundidade:
            for acao, filho_est, custo in gerar_sucessores(no.estado):
                if filho_est not in visitados:
                    fronteira.append((No(filho_est, no, acao, no.custo_g + custo), prof + 1))

    return None, 0, nos_expandidos


def busca_heuristica(estado_inicial, verifica_objetivo, gerar_sucessores, heuristica, tipo="A*", detalhado=False):
    eh_gulosa = (tipo == "Gulosa")
    h_inicial = heuristica(estado_inicial)
    no_raiz = No(estado_inicial, custo_g=0, heuristica_h=h_inicial, apenas_heuristica=eh_gulosa)

    fronteira = []
    heapq.heappush(fronteira, no_raiz)
    visitados = {estado_inicial: 0}
    nos_expandidos = 0
    passo = 1

    while fronteira:
        no = heapq.heappop(fronteira)
        nos_expandidos += 1

        if detalhado:
            print(f"\n[{tipo} - PASSO {passo}] Expandindo estado: {no.estado}")
            if verifica_objetivo(no.estado):
                print("  -> OBJETIVO ALCANÇADO! A estimativa heurística restante agora é zero.")
                print(f"  -> Matemática Final: F(n) = {no.custo_g} (G real) + 0 (H zerada na meta) = {no.f}")
            else:
                print(f"  -> Custo acumulado G(n) = {no.custo_g} | Heurística H(n) = {no.heuristica_h} | F(n) = {no.f}")
            print("  " + "-" * 55)

        if verifica_objetivo(no.estado):
            return reconstruir_caminho(no), no.custo_g, nos_expandidos

        for acao, filho_est, custo in gerar_sucessores(no.estado):
            novo_g = no.custo_g + custo
            h = heuristica(filho_est)
            f = h if eh_gulosa else (novo_g + h)

            deve_inserir = (
                (filho_est not in visitados)
                if eh_gulosa
                else (filho_est not in visitados or novo_g < visitados[filho_est])
            )

            if deve_inserir:
                visitados[filho_est] = novo_g
                heapq.heappush(fronteira, No(filho_est, no, acao, novo_g, h, apenas_heuristica=eh_gulosa))

                if detalhado:
                    print(f"     + Ação '{acao}' -> {filho_est} (custo do passo: {custo})")
                    print(f"       [ACUMULANDO G]: {no.custo_g} + {custo} = {novo_g}")
                    if verifica_objetivo(filho_est):
                        print(f"       [HEURÍSTICA H]: {h} <<< H(n) = 0 pois atingiu o estado objetivo!")
                    else:
                        print(f"       [HEURÍSTICA H]: {h}")
                    print(f"       [FÓRMULA F(n)]: F(n) = {novo_g} + {h} = {f}")
            elif detalhado and (no.pai is None or filho_est != no.pai.estado):
                print(f"     x [DESCARTADO] '{acao}' -> {filho_est}: G={novo_g} não melhora melhor G já salvo ({visitados[filho_est]})")

        passo += 1

    return None, 0, nos_expandidos


# ==========================================
# 3. DOMÍNIO 1: MALHA RODOVIÁRIA DO PIAUÍ
# ==========================================
GRAFO_PI = {
    'Sao Raimundo Nonato': [('Canto do Buriti', 100), ('Floriano', 250)],
    'Canto do Buriti': [('Sao Raimundo Nonato', 100), ('Floriano', 160)],
    'Floriano': [('Sao Raimundo Nonato', 250), ('Canto do Buriti', 160), ('Oeiras', 100), ('Teresina', 240)],
    'Oeiras': [('Floriano', 100), ('Picos', 90)],
    'Picos': [('Oeiras', 90), ('Teresina', 310)],
    'Teresina': [('Floriano', 240), ('Picos', 310), ('Campo Maior', 80)],
    'Campo Maior': [('Teresina', 80), ('Piripiri', 90)],
    'Piripiri': [('Campo Maior', 90), ('Parnaiba', 150)],
    'Parnaiba': [('Piripiri', 150)]
}

# Distância aproximada em linha reta até Parnaíba (h(n))
H_PI = {
    'Parnaiba': 0, 'Piripiri': 130, 'Campo Maior': 200,
    'Teresina': 270, 'Oeiras': 420, 'Picos': 400,
    'Floriano': 450, 'Canto do Buriti': 520, 'Sao Raimundo Nonato': 600
}


def sucessores_pi(estado):
    return [(f"Ir para {dest}", dest, custo) for dest, custo in GRAFO_PI[estado]]


def obj_pi(estado):
    return estado == 'Parnaiba'


def h_linha_reta(estado):
    return H_PI[estado]


# ==========================================
# 4. DOMÍNIO 2: JOGO DOS 8 NÚMEROS (8-PUZZLE)
# ==========================================
OBJETIVO_8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def sucessores_8(estado):
    idx_zero = estado.index(0)
    linha, col = divmod(idx_zero, 3)
    movimentos = []

    # Movimentos válidos da célula vazia (0): Cima, Baixo, Esquerda, Direita
    direcoes = [
        ('Cima', -1, 0),
        ('Baixo', 1, 0),
        ('Esquerda', 0, -1),
        ('Direita', 0, 1)
    ]

    for acao, dl, dc in direcoes:
        nl, nc = linha + dl, col + dc
        if 0 <= nl < 3 and 0 <= nc < 3:
            novo_idx = nl * 3 + nc
            novo_est = list(estado)
            novo_est[idx_zero], novo_est[novo_idx] = novo_est[novo_idx], novo_est[idx_zero]
            movimentos.append((acao, tuple(novo_est), 1))  # Custo g(n) = 1 por movimento

    return movimentos


def obj_8(estado):
    return estado == OBJETIVO_8


def h1_pecas_fora(estado):
    """Heurística h1(n): quantidade de peças fora do lugar (Misplaced Tiles)."""
    return sum(1 for i in range(9) if estado[i] != 0 and estado[i] != OBJETIVO_8[i])


def h2_manhattan(estado):
    """Heurística h2(n): soma das distâncias de Manhattan até a posição final."""
    dist = 0
    for i in range(9):
        val = estado[i]
        if val != 0:
            l_atual, c_atual = divmod(i, 3)
            l_obj, c_obj = divmod(OBJETIVO_8.index(val), 3)
            dist += abs(l_atual - l_obj) + abs(c_atual - c_obj)
    return dist


def imprimir_tabuleiro(estado):
    print(f"    {estado[0]} {estado[1]} {estado[2]}")
    print(f"    {estado[3]} {estado[4]} {estado[5]}")
    print(f"    {estado[6]} {estado[7]} {estado[8]}")


# ==========================================
# 5. EXECUÇÃO PRINCIPAL (DOMÍNIO 1 + DOMÍNIO 2)
# ==========================================
if __name__ == "__main__":
    print("=" * 70)
    print(" DOMÍNIO 1: COMPARATIVO GERAL (SÃO RAIMUNDO NONATO -> PARNAÍBA)")
    print("=" * 70)

    algoritmos_pi = [
        ("BFS", lambda: busca_bfs('Sao Raimundo Nonato', obj_pi, sucessores_pi)),
        ("DFS", lambda: busca_dfs('Sao Raimundo Nonato', obj_pi, sucessores_pi)),
        ("Gulosa", lambda: busca_heuristica('Sao Raimundo Nonato', obj_pi, sucessores_pi, h_linha_reta, "Gulosa")),
        ("A*", lambda: busca_heuristica('Sao Raimundo Nonato', obj_pi, sucessores_pi, h_linha_reta, "A*")),
    ]

    for nome, func in algoritmos_pi:
        inicio = time.perf_counter()
        caminho, custo_total, nos = func()
        tempo = time.perf_counter() - inicio
        print(f"[{nome:6}] Nós Expandidos: {nos:2} | Tempo: {tempo:.5f}s | Custo: {custo_total} km")
        print(f"         Rota: {[passo[1] for passo in caminho]}\n")

    print("=" * 70)
    print(" DOMÍNIO 1: RASTREAMENTO DETALHADO DO A* (PASSO A PASSO)")
    print("=" * 70)
    busca_heuristica('Sao Raimundo Nonato', obj_pi, sucessores_pi, h_linha_reta, "A*", detalhado=True)

    print("\n" + "=" * 70)
    print(" DOMÍNIO 2: 8-PUZZLE — COMPARAÇÃO A* (h1 vs h2) + BFS/GULOSA")
    print("=" * 70)

    # Estados iniciais correspondentes à Tabela 2 do Relatório Técnico
    estados_iniciais = {
        "d=5": (1, 2, 3, 4, 0, 5, 7, 8, 6),
        "d=10": (1, 0, 2, 4, 6, 3, 7, 5, 8),
        "d=15": (4, 1, 2, 7, 6, 3, 0, 5, 8),
    }

    for rotulo, estado in estados_iniciais.items():
        print(f"\n>>> Cenário {rotulo} | Estado inicial: {estado}")

        # BFS
        t0 = time.perf_counter()
        cam_bfs, custo_bfs, nos_bfs = busca_bfs(estado, obj_8, sucessores_8)
        t_bfs = time.perf_counter() - t0

        # Busca Gulosa com h2
        t0 = time.perf_counter()
        cam_gul, custo_gul, nos_gul = busca_heuristica(estado, obj_8, sucessores_8, h2_manhattan, "Gulosa")
        t_gul = time.perf_counter() - t0

        # A* com h1 (Peças fora do lugar)
        t0 = time.perf_counter()
        cam_h1, custo_h1, nos_h1 = busca_heuristica(estado, obj_8, sucessores_8, h1_pecas_fora, "A*")
        t_h1 = time.perf_counter() - t0

        # A* com h2 (Distância de Manhattan)
        t0 = time.perf_counter()
        cam_h2, custo_h2, nos_h2 = busca_heuristica(estado, obj_8, sucessores_8, h2_manhattan, "A*")
        t_h2 = time.perf_counter() - t0

        print(f"  [BFS]             Nós: {nos_bfs:4} | Movimentos: {custo_bfs:2} | Tempo: {t_bfs:.5f}s")
        print(f"  [Gulosa - h2]     Nós: {nos_gul:4} | Movimentos: {custo_gul:2} | Tempo: {t_gul:.5f}s")
        print(f"  [A* - h1 Peças]   Nós: {nos_h1:4} | Movimentos: {custo_h1:2} | Tempo: {t_h1:.5f}s")
        print(f"  [A* - h2 Manhat.] Nós: {nos_h2:4} | Movimentos: {custo_h2:2} | Tempo: {t_h2:.5f}s")

    print("\n" + "=" * 70)
    print(" DOMÍNIO 2: RASTREAMENTO DETALHADO DO 8-PUZZLE (A* com Manhattan)")
    print("=" * 70)
    caminho_8, movimentos_8, nos_8 = busca_heuristica(
        estados_iniciais["d=5"], obj_8, sucessores_8, h2_manhattan, "A*", detalhado=True
    )

    print(f"\n[RESULTADO FINAL - 8-PUZZLE] Nós Expandidos: {nos_8} | Movimentos: {movimentos_8}")
    for acao, tab in caminho_8:
        print(f" -> Ação: {acao if acao else 'Estado Inicial'}")
        imprimir_tabuleiro(tab)