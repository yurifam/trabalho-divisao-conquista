"""Regressões determinísticas para situações com soluções concorrentes.

Os dois métodos devem produzir a mesma resposta para cada cenário;
na Etapa 2 a distância quadrada é usada para evitar arredondamento.
"""
import unittest

from src.algoritmos import (
    pontos_bruto,
    pontos_divisao,
    subarranjo_bruto,
    subarranjo_divisao,
)


class TestRegressoes(unittest.TestCase):
    def test_subarranjo_empate_todos_zeros(self):
        vetor = [0, 0, 0, 0]
        for metodo in (subarranjo_bruto, subarranjo_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(vetor), (0, 0, 0))

    def test_subarranjo_cruza_o_meio(self):
        vetor = [5, -2, 3, -1]
        for metodo in (subarranjo_bruto, subarranjo_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(vetor), (6, 0, 2))

    def test_subarranjo_valores_grandes(self):
        vetor = [10**12, -(10**12 + 5), 10**12]
        for metodo in (subarranjo_bruto, subarranjo_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(vetor), (10**12, 0, 0))

    def test_pontos_duplicados_nao_adjacentes(self):
        pontos = [(0, 0), (100, 100), (0, 0), (-10, 20)]
        for metodo in (pontos_bruto, pontos_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(pontos), (0, 0, 2))

    def test_pontos_mais_proximos_em_metades_diferentes(self):
        pontos = [(-8, 8), (-1, 0), (1, 0), (8, -8)]
        for metodo in (pontos_bruto, pontos_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(pontos), (4, 1, 2))

    def test_pontos_com_mesma_coordenada_x_e_reais(self):
        pontos = [(3.5, 0.0), (3.5, 1.0), (3.5, 4.0), (20, 20)]
        for metodo in (pontos_bruto, pontos_divisao):
            with self.subTest(metodo=metodo.__name__):
                self.assertEqual(metodo(pontos), (1.0, 0, 1))


if __name__ == '__main__':
    unittest.main()
