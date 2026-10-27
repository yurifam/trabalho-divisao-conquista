"""Interface em terminal para os dois problemas do trabalho."""
import argparse
import sys
from src.algoritmos import (subarranjo_bruto, subarranjo_divisao,
                            pontos_bruto, pontos_divisao, distancia)


def main() -> int:
    parser = argparse.ArgumentParser(description='Trabalho de Divisão e Conquista')
    parser.add_argument('problema', choices=['subarranjo', 'pontos'])
    parser.add_argument('metodo', choices=['bruto', 'divisao'])
    parser.add_argument('--detalhado', action='store_true', help='Mostra nomes dos campos e distância quadrada')
    parser.add_argument('--limiar', type=int, default=8,
                        help='Limiar da Etapa 2 (padrão: 8)')
    args = parser.parse_args()
    try:
        tokens = sys.stdin.read().split()
        if not tokens:
            raise ValueError('Nenhuma entrada recebida.')
        n = int(tokens[0])
        if args.problema == 'subarranjo':
            if n < 1 or len(tokens) != n + 1:
                raise ValueError('Informe n >= 1 seguido de exatamente n inteiros.')
            v = list(map(int, tokens[1:]))
            f = subarranjo_bruto if args.metodo == 'bruto' else subarranjo_divisao
            soma, inicio, fim = f(v)
            if args.detalhado:
                print(f'soma_maxima={soma} inicio={inicio} fim={fim}')
            else:
                print(soma, inicio, fim)
        else:
            if n < 2 or len(tokens) != 2*n + 1:
                raise ValueError('Informe n >= 2 seguido de exatamente n pares x y.')
            # Aceita números reais, inclusive decimais; usa inteiros se possível.
            coords = [float(item) if any(c in item.lower() for c in '.e') else int(item)
                      for item in tokens[1:]]
            pontos = list(zip(coords[0::2], coords[1::2]))
            resultado = (pontos_bruto(pontos) if args.metodo == 'bruto'
                         else pontos_divisao(pontos, args.limiar))
            d2, i, j = resultado
            if args.detalhado:
                print(f'distancia={distancia(resultado):.12g} distancia_quadrada={d2} ponto1={i} ponto2={j}')
            else:
                print(f'{distancia(resultado):.12g} {i} {j}')
    except (ValueError, OverflowError) as exc:
        print(f'Erro de entrada: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
