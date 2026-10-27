"""Medições reais e reproduzíveis; exclui geração de dados da cronometragem."""
import argparse
import csv
import json
import os
import platform
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from src.algoritmos import (subarranjo_bruto, subarranjo_divisao,
                            pontos_bruto, pontos_divisao)

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / 'resultados'
TAMANHOS = (100, 200, 400, 800, 1600, 3200, 6400)
LIMIARES = (4, 8, 16, 32, 64)


def entrada_subarranjo(n):
    rng = random.Random(120_000 + n)
    return [rng.randint(-100, 100) for _ in range(n)]


def entrada_pontos(n):
    rng = random.Random(220_000 + n)
    vistos = set()
    while len(vistos) < n:
        vistos.add((rng.randint(-1_000_000, 1_000_000), rng.randint(-1_000_000, 1_000_000)))
    lista = sorted(vistos)
    rng.shuffle(lista)  # Ordem de entrada não ordenada; evita favorecer Timsort.
    return lista


def cronometrar(funcao, dados):
    inicio = time.perf_counter_ns()
    retorno = funcao(dados)
    return time.perf_counter_ns() - inicio, retorno


def maquina():
    try:
        with open('/proc/cpuinfo', encoding='utf-8') as arq:
            cpu = next((linha.split(':', 1)[1].strip() for linha in arq if linha.startswith('model name')), 'não informada')
    except OSError:
        cpu = platform.processor() or 'não informado'
    try:
        quota = Path('/sys/fs/cgroup/cpu.max').read_text().strip()
    except OSError:
        quota = 'não informado'
    try:
        memory = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    except OSError:
        memory = 'não informado'
    return {'sistema': platform.platform(), 'arquitetura': platform.machine(),
            'processador_identificado': cpu, 'cpus_visiveis': os.cpu_count(),
            'quota_cpu_cgroup': quota, 'limite_memoria_cgroup_bytes': memory,
            'python': platform.python_version(), 'temporizador': 'time.perf_counter_ns'}


def calibrar(repeticoes=5):
    linhas = []
    for n in (200, 800, 3200):
        dados = entrada_pontos(n)
        referencia = pontos_bruto(dados)
        for limiar in LIMIARES:
            f = lambda p, l=limiar: pontos_divisao(p, l)
            if f(dados)[0] != referencia[0]:
                raise RuntimeError(f'Limiar {limiar} divergiu de força bruta!')
            f(dados)
            for repeticao in range(1, repeticoes + 1):
                ns, result = cronometrar(f, dados)
                assert result[0] == referencia[0]
                linhas.append({'n': n, 'limiar': limiar, 'repeticao': repeticao, 'tempo_ns': ns})
        print(f'Calibrado: n={n}', flush=True)
    RESULTADOS.mkdir(exist_ok=True)
    with (RESULTADOS / 'calibracao_limiar.csv').open('w', newline='', encoding='utf-8') as arq:
        gravador = csv.DictWriter(arq, fieldnames=['n', 'limiar', 'repeticao', 'tempo_ns'])
        gravador.writeheader()
        gravador.writerows(linhas)
    por_tamanho = {}
    for n in (200, 800, 3200):
        por_tamanho[n] = {k: statistics.mean(r['tempo_ns'] for r in linhas if r['n'] == n and r['limiar'] == k)
                          for k in LIMIARES}
    import math
    pontuacoes = {k: math.exp(sum(math.log(por_tamanho[n][k] / min(por_tamanho[n].values()))
                                  for n in por_tamanho) / len(por_tamanho)) for k in LIMIARES}
    melhor = min(pontuacoes, key=pontuacoes.get)
    print('Pontuacoes limiar (menor e melhor):', {k: round(v, 3) for k, v in pontuacoes.items()}, flush=True)
    print('Limiar escolhido:', melhor, flush=True)
    return melhor, por_tamanho, pontuacoes


def medir(limiar, repeticoes, tamanhos):
    linhas = []
    for n in tamanhos:
        for problema, dados, brute, div in (
            ('subarranjo', entrada_subarranjo(n), subarranjo_bruto, subarranjo_divisao),
            ('pontos', entrada_pontos(n), pontos_bruto, lambda d: pontos_divisao(d, limiar))):
            esperado = brute(dados)
            resultado = div(dados)
            if ((esperado != resultado) if problema == 'subarranjo' else (esperado[0] != resultado[0])):
                raise RuntimeError(f'Resultados distintos para {problema}, n={n}: {esperado} != {resultado}')
            for metodo, funcao in [('bruto', brute), ('divisao', div)]:
                funcao(dados)
                for repeticao in range(1, repeticoes + 1):
                    ns, retorno = cronometrar(funcao, dados)
                    if ((retorno != esperado) if problema == 'subarranjo' else (retorno[0] != esperado[0])):
                        raise RuntimeError('Divergência durante a medição')
                    linhas.append({'problema': problema, 'metodo': metodo, 'n': n,
                                   'repeticao': repeticao, 'tempo_ns': ns,
                                   'semente': (120_000 if problema == 'subarranjo' else 220_000) + n,
                                   'limiar': limiar if problema == 'pontos' and metodo == 'divisao' else ''})
                print(f'Medido: {problema:10s} {metodo:8s} n={n:5d}', flush=True)
        RESULTADOS.mkdir(exist_ok=True)
        with (RESULTADOS / 'medicoes_brutas.csv').open('w', newline='', encoding='utf-8') as arq:
            gravador = csv.DictWriter(arq, fieldnames=['problema', 'metodo', 'n', 'repeticao', 'tempo_ns', 'semente', 'limiar'])
            gravador.writeheader()
            gravador.writerows(linhas)
    medias = []
    for problema in ('subarranjo', 'pontos'):
        for n in tamanhos:
            for metodo in ('bruto', 'divisao'):
                valores = [r['tempo_ns']/1e6 for r in linhas if r['problema'] == problema and r['n'] == n and r['metodo'] == metodo]
                medias.append({'problema': problema, 'metodo': metodo, 'n': n,
                               'media_ms': statistics.mean(valores), 'desvio_ms': statistics.stdev(valores),
                               'minimo_ms': min(valores), 'maximo_ms': max(valores)})
    with (RESULTADOS / 'resumo_medicoes.csv').open('w', newline='', encoding='utf-8') as arq:
        gravador = csv.DictWriter(arq, fieldnames=['problema', 'metodo', 'n', 'media_ms', 'desvio_ms', 'minimo_ms', 'maximo_ms'])
        gravador.writeheader()
        gravador.writerows(medias)
    return medias


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeticoes', type=int, default=5)
    parser.add_argument('--limiar', type=int, default=0, help='0 para calibrar automaticamente')
    parser.add_argument('--tamanhos', type=int, nargs='+', default=TAMANHOS)
    args = parser.parse_args()
    if args.repeticoes < 5:
        parser.error('São exigidas pelo menos cinco repetições.')
    inicio = datetime.now(timezone.utc).isoformat()
    if args.limiar:
        limiar = args.limiar
        calibracao, pontuacoes = {}, {}
    else:
        limiar, calibracao, pontuacoes = calibrar()
    medir(limiar, args.repeticoes, args.tamanhos)
    metadados = {'inicio_utc': inicio, 'termino_utc': datetime.now(timezone.utc).isoformat(),
                 'repeticoes': args.repeticoes, 'tamanhos': args.tamanhos,
                 'limiar_escolhido': limiar, 'limiares_testados': LIMIARES if calibracao else [],
                 'calibracao_media_ns': calibracao, 'pontuacoes_calibracao': pontuacoes,
                 'dados': 'subarranjo: inteiros uniformes [-100,100]; pontos: unicos aleatorios inteiros [-1e6,1e6]^2',
                 'maquina': maquina(), 'observacao': 'CPU e memoria informadas pelo contêiner de execução, não pela máquina do aluno.'}
    (RESULTADOS / 'ambiente_e_protocolo.json').write_text(json.dumps(metadados, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Concluído.', flush=True)

if __name__ == '__main__':
    main()
