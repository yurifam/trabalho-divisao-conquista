"""Algoritmos das etapas 1 e 2. Índices de entrada são baseados em zero.

Não usa soluções lineares para o problema de subarranjo, conforme o escopo.
"""
from __future__ import annotations

from math import isfinite, sqrt
from typing import Sequence

Subarray = tuple[int, int, int]  # soma, índice inicial, índice final
Ponto = tuple[float | int, float | int]
ResultadoPontos = tuple[int | float, int, int]  # distância ao quadrado, IDs 0-based


def _melhor_subarranjo(a: Subarray, b: Subarray) -> Subarray:
    """Maior soma; em empates, menor início e depois menor fim."""
    return a if (-a[0], a[1], a[2]) <= (-b[0], b[1], b[2]) else b


def _validar_vetor(v: Sequence[int]) -> None:
    if not v:
        raise ValueError("O vetor precisa ter ao menos um elemento.")
    if any(type(x) is not int for x in v):
        raise ValueError("O subarranjo exige valores inteiros.")


def subarranjo_bruto(v: Sequence[int]) -> Subarray:
    """Enumera todos os n(n+1)/2 subarranjos em Theta(n²), espaço O(1)."""
    _validar_vetor(v)
    melhor: Subarray = (v[0], 0, 0)
    for inicio in range(len(v)):
        acumulado = 0
        for fim in range(inicio, len(v)):
            acumulado += v[fim]
            candidato = (acumulado, inicio, fim)
            melhor = _melhor_subarranjo(melhor, candidato)
    return melhor


def subarranjo_divisao(v: Sequence[int]) -> Subarray:
    """Resolve os lados e examina prefixo/sufixo da fronteira: Theta(n log n)."""
    _validar_vetor(v)

    def resolver(inicio: int, fim_exclusivo: int) -> Subarray:
        if fim_exclusivo - inicio == 1:
            return (v[inicio], inicio, inicio)
        meio = (inicio + fim_exclusivo) // 2
        esquerda = resolver(inicio, meio)
        direita = resolver(meio, fim_exclusivo)
        soma = 0
        melhor_soma_esq = None
        melhor_ini = meio - 1
        for i in range(meio - 1, inicio - 1, -1):
            soma += v[i]
            if melhor_soma_esq is None or soma > melhor_soma_esq or (soma == melhor_soma_esq and i < melhor_ini):
                melhor_soma_esq = soma
                melhor_ini = i
        soma = 0
        melhor_soma_dir = None
        melhor_fim = meio
        for j in range(meio, fim_exclusivo):
            soma += v[j]
            if melhor_soma_dir is None or soma > melhor_soma_dir:
                melhor_soma_dir = soma
                melhor_fim = j
        assert melhor_soma_esq is not None and melhor_soma_dir is not None
        cruzado: Subarray = (melhor_soma_esq + melhor_soma_dir, melhor_ini, melhor_fim)
        return _melhor_subarranjo(_melhor_subarranjo(esquerda, direita), cruzado)

    return resolver(0, len(v))


def _validar_pontos(pontos: Sequence[Ponto]) -> None:
    if len(pontos) < 2:
        raise ValueError("São necessários pelo menos dois pontos.")
    for p in pontos:
        if len(p) != 2 or any(not isinstance(a, (int, float)) or not isfinite(a) for a in p):
            raise ValueError("Cada ponto deve ter duas coordenadas numéricas finitas.")


def _dist2(a: tuple, b: tuple) -> int | float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _par(a: tuple, b: tuple) -> ResultadoPontos:
    i, j = sorted((a[2], b[2]))
    return (_dist2(a, b), i, j)


def pontos_bruto(pontos: Sequence[Ponto]) -> ResultadoPontos:
    """Todos os n(n-1)/2 pares: Theta(n²), espaço O(1)."""
    _validar_pontos(pontos)
    primeiro = (pontos[0][0], pontos[0][1], 0)
    segundo = (pontos[1][0], pontos[1][1], 1)
    melhor = _par(primeiro, segundo)
    for i in range(len(pontos) - 1):
        x1, y1 = pontos[i]
        for j in range(i + 1, len(pontos)):
            x2, y2 = pontos[j]
            candidato = ((x1-x2)**2 + (y1-y2)**2, i, j)
            if candidato < melhor:
                melhor = candidato
    return melhor


def pontos_divisao(pontos: Sequence[Ponto], limiar: int = 8) -> ResultadoPontos:
    """Divisão por x; listas ordenadas por y; faixa com até 7 vizinhos.

    Tempo Theta(n log n), espaço auxiliar O(n) (incluindo ordenações),
    admitindo o custo convencional O(n log n) das ordenações da biblioteca.
    O limiar controla caso-base resolvido por comparação exaustiva.
    """
    _validar_pontos(pontos)
    if not isinstance(limiar, int) or limiar < 2:
        raise ValueError("O limiar precisa ser inteiro >= 2.")
    px = sorted(((x, y, i) for i, (x, y) in enumerate(pontos)), key=lambda p: (p[0], p[1], p[2]))
    py = sorted(px, key=lambda p: (p[1], p[0], p[2]))

    # Distância zero: trata globalmente pontos coincidentes, inclusive na linha divisória.
    # Evita ambiguidades quando delta=0 e resolve empates por (índice1, índice2).
    empate_zero = None
    for anterior, atual in zip(px, px[1:]):
        if anterior[:2] == atual[:2]:
            candidato = _par(anterior, atual)
            if empate_zero is None or candidato < empate_zero:
                empate_zero = candidato
    if empate_zero is not None:
        return empate_zero

    def resolver(xord: list[tuple], yord: list[tuple]) -> ResultadoPontos:
        n = len(xord)
        if n <= max(3, limiar):
            melhor = _par(xord[0], xord[1])
            for i in range(n-1):
                for j in range(i+1, n):
                    candidato = _par(xord[i], xord[j])
                    if candidato < melhor:
                        melhor = candidato
            return melhor
        metade = n // 2
        esqx = xord[:metade]
        dirx = xord[metade:]
        corte = dirx[0][0]
        ids_esq = {p[2] for p in esqx}
        esqy = []
        diry = []
        for p in yord:
            if p[2] in ids_esq:
                esqy.append(p)
            else:
                diry.append(p)
        melhor = min(resolver(esqx, esqy), resolver(dirx, diry))
        d2 = melhor[0]
        faixa = [p for p in yord if (p[0] - corte)**2 <= d2]
        for i, p in enumerate(faixa):
            # Geometria do par mais próximo: no máximo sete sucessores em y.
            for q in faixa[i + 1:i + 8]:
                if (q[1] - p[1])**2 > melhor[0]:
                    break
                candidato = _par(p, q)
                if candidato < melhor:
                    melhor = candidato
        return melhor

    return resolver(px, py)


def distancia(resultado: ResultadoPontos) -> float:
    """Distância euclidiana (apenas na apresentação; comparação usa d²)."""
    return sqrt(resultado[0])
