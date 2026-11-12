import heapq
from collections import deque
import time

# ==========================================
# 1. ESTRUTURA BASE (O NÓ DE BUSCA)
# ==========================================
class No:
    def __init__(self, estado, pai=None, acao=None, custo_g=0, heuristica_h=0):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.custo_g = custo_g       
        self.heuristica_h = heuristica_h 
        
    @property
    def f(self):
        return self.custo_g + self.heuristica_h

    # Desempate na fila de prioridade
    def __lt__(self, outro):
        return self.f < outro.f

def reconstruir_caminho(no):
    caminho = []
    while no:
        caminho.append((no.acao, no.estado))
        no = no.pai
    return caminho[::-1]

# ==========================================
# 2. ALGORITMOS DE BUSCA (COM MODO DIDÁTICO PROFESSOR)
# ==========================================
def busca_bfs(estado_inicial, verifica_objetivo, gerar_sucessores):
    fronteira = deque([No(estado_inicial)]) 
    visitados = {estado_inicial}
    nos_expandidos = 0
    
    while fronteira:
        no = fronteira.popleft()
        nos_expandidos += 1
        if verifica_objetivo(no.estado): return reconstruir_caminho(no), nos_expandidos
        for acao, filho_est, custo in gerar_sucessores(no.estado):
            if filho_est not in visitados:
                visitados.add(filho_est)
                fronteira.append(No(filho_est, no, acao, no.custo_g + custo))
    return None, nos_expandidos

def busca_dfs(estado_inicial, verifica_objetivo, gerar_sucessores):
    fronteira = [No(estado_inicial)] 
    visitados = set()
    nos_expandidos = 0
    
    while fronteira:
        no = fronteira.pop()
        if no.estado in visitados: continue
        visitados.add(no.estado)
        nos_expandidos += 1
        if verifica_objetivo(no.estado): return reconstruir_caminho(no), nos_expandidos
        for acao, filho_est, custo in gerar_sucessores(no.estado):
            if filho_est not in visitados:
                fronteira.append(No(filho_est, no, acao, no.custo_g + custo))
    return None, nos_expandidos

def busca_heuristica(estado_inicial, verifica_objetivo, gerar_sucessores, heuristica, tipo="A*", detalhado=False):
    no_raiz = No(estado_inicial, custo_g=0, heuristica_h=heuristica(estado_inicial))
    fronteira = []
    heapq.heappush(fronteira, no_raiz)
    visitados = {estado_inicial: 0 if tipo == "A*" else heuristica(estado_inicial)}
    nos_expandidos = 0
    passo = 1
    
    while fronteira:
        no = heapq.heappop(fronteira)
        nos_expandidos += 1
        
        if detalhado:
            print(f"\n[{tipo} - PASSO {passo}] Analisando cidade atual: {no.estado.upper()}")
            
            if no.estado == 'Parnaiba':
                print(f"  -> CHEGAMOS NO DESTINO! A distância em linha reta acabou.")
                print(f"  -> Matemática Final: F(n) = {no.custo_g} (G: real percorrido) + 0 (H: zerada no alvo) = {no.f}")
            else:
                print(f"  -> Estamos em {no.estado}. O custo real percorrido até aqui é G(n) = {no.custo_g}.")
            print("  - - - - - - - - - - - - - - - - - - - - - - - - -")
            
        if verifica_objetivo(no.estado): 
            return reconstruir_caminho(no), nos_expandidos
            
        for acao, filho_est, custo in gerar_sucessores(no.estado):
            # AQUI ACONTECE A ACUMULAÇÃO DO G(n)
            novo_g = no.custo_g + (custo if tipo == "A*" else 0)
            
            if filho_est not in visitados or novo_g < visitados[filho_est]:
                visitados[filho_est] = novo_g
                h = heuristica(filho_est)
                f = novo_g + h
                heapq.heappush(fronteira, No(filho_est, no, acao, novo_g, h))
                
                if detalhado:
                    print(f"     + Possibilidade: Ir para {filho_est} (Distância da estrada: {custo}km)")
                    print(f"       [ACUMULANDO G]: {no.custo_g} (anterior) + {custo} (estrada) = {novo_g}")
                    
                    if filho_est == 'Parnaiba':
                        print(f"       [HEURÍSTICA H]: {h} <<< ATENÇÃO: H(n) = 0 pois {filho_est} é a meta!")
                    else:
                        print(f"       [HEURÍSTICA H]: {h} (em linha reta até Parnaíba)")
                        
                    print(f"       [FÓRMULA F(n)]: F(n) = {novo_g} + {h} = {f}\n")
        passo += 1
    return None, nos_expandidos

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

# Heurística corrigida: Início é 600 em linha reta
H_PI = {
    'Parnaiba': 0, 'Piripiri': 130, 'Campo Maior': 200, 
    'Teresina': 270, 'Oeiras': 420, 'Picos': 400, 
    'Floriano': 450, 'Canto do Buriti': 520, 'Sao Raimundo Nonato': 600
}

def sucessores_pi(estado): return [(f"Ir para {dest}", dest, custo) for dest, custo in GRAFO_PI[estado]]
def obj_pi(estado): return estado == 'Parnaiba'
def h_linha_reta(estado): return H_PI[estado]

# ==========================================
# 5. EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("="*70)
    print(" DOMÍNIO 1: SÃO RAIMUNDO NONATO -> PARNAÍBA (A* DIDÁTICO)")
    print("="*70)
    
    caminho_pi, nos_pi = busca_heuristica('Sao Raimundo Nonato', obj_pi, sucessores_pi, h_linha_reta, "A*", detalhado=True)
    custo_total = sum(GRAFO_PI[c[1]][[x[0] for x in GRAFO_PI[c[1]]].index(caminho_pi[i+1][1])][1] for i, c in enumerate(caminho_pi[:-1])) if caminho_pi else 0
    
    print("\n[RESULTADO FINAL - ROTA ÓTIMA ENCONTRADA PELO A*]")
    print(f"Nós Expandidos: {nos_pi}")
    print(f"Custo Real Percorrido G(n): {custo_total}km")
    print(f"Rota Completa: {[passo[1] for passo in caminho_pi]}")