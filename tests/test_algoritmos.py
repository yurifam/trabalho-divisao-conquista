import json
import random
import unittest
from pathlib import Path

from src.algoritmos import (subarranjo_bruto, subarranjo_divisao,
                            pontos_bruto, pontos_divisao)

CASOS = json.loads((Path(__file__).parent / 'casos_teste.json').read_text(encoding='utf-8'))


class TestCasosComSaidasEsperadas(unittest.TestCase):
    def test_subarranjo_fixtures(self):
        for caso in CASOS['subarranjo']:
            esperado = (caso['esperado']['soma'], caso['esperado']['inicio'], caso['esperado']['fim'])
            for algoritmo in (subarranjo_bruto, subarranjo_divisao):
                with self.subTest(id=caso['id'], metodo=algoritmo.__name__):
                    self.assertEqual(algoritmo(caso['entrada']), esperado)

    def test_pontos_fixtures(self):
        for caso in CASOS['pontos']:
            pontos = caso['entrada']
            dist2 = caso['esperado']['distancia_quadrada']
            for algoritmo in (pontos_bruto, pontos_divisao):
                with self.subTest(id=caso['id'], metodo=algoritmo.__name__):
                    retorno = algoritmo(pontos)
                    self.assertAlmostEqual(retorno[0], dist2)
                    self.assertTrue(0 <= retorno[1] < retorno[2] < len(pontos))
                    p1, p2 = pontos[retorno[1]], pontos[retorno[2]]
                    self.assertAlmostEqual((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2, dist2)

    def test_entradas_invalidas(self):
        for metodo in (subarranjo_bruto, subarranjo_divisao):
            with self.assertRaises(ValueError): metodo([])
            with self.assertRaises(ValueError): metodo([1, 2.5])
        for metodo in (pontos_bruto, pontos_divisao):
            with self.assertRaises(ValueError): metodo([(1, 2)])
            with self.assertRaises(ValueError): metodo([(1, 2), (float('nan'), 3)])
        with self.assertRaises(ValueError): pontos_divisao([(0, 0), (1, 1)], limiar=1)


class TestDiferencial(unittest.TestCase):
    def test_subarranjo_randomizado(self):
        rng = random.Random(20261027)
        for n in range(1, 65):
            for _ in range(50):
                v = [rng.randint(-8, 8) for _ in range(n)]
                self.assertEqual(subarranjo_divisao(v), subarranjo_bruto(v), v)

    def test_pontos_randomizados_por_limiar(self):
        rng = random.Random(4827)
        for n in range(2, 52):
            for _ in range(20):
                pontos = [(rng.randint(-12, 12), rng.randint(-12, 12)) for _ in range(n)]
                esperado = pontos_bruto(pontos)
                for limiar in (2, 3, 4, 8, 16, 32):
                    resultado = pontos_divisao(pontos, limiar=limiar)
                    self.assertEqual(resultado[0], esperado[0], (n, pontos, limiar))
                    self.assertEqual(resultado[0], (pontos[resultado[1]][0]-pontos[resultado[2]][0])**2 + (pontos[resultado[1]][1]-pontos[resultado[2]][1])**2)

    def test_pontos_sem_duplicatas_ties(self):
        rng = random.Random(82271)
        for n in (17, 31, 64, 127, 256):
            for _ in range(12):
                pontos = rng.sample([(x, y) for x in range(-20, 21) for y in range(-20, 21)], n)
                self.assertEqual(pontos_divisao(pontos)[0], pontos_bruto(pontos)[0])


if __name__ == '__main__':
    unittest.main()
