"""Testes de ponta a ponta para a interface de linha de comando.

Complementam os testes das funcoes: validam leitura de entrada,
formato da saida e sinalizacao de erros para quem corrigir o trabalho.
"""
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class TestInterfaceTerminal(unittest.TestCase):
    def executar(self, problema, metodo, entrada, *opcoes):
        return subprocess.run(
            [sys.executable, str(RAIZ / 'main.py'), problema, metodo, *opcoes],
            input=entrada,
            text=True,
            capture_output=True,
            cwd=RAIZ,
            timeout=10,
            check=False,
        )

    def test_subarranjo_exemplo_nos_dois_metodos(self):
        entrada = '9\n-2 1 -3 4 -1 2 1 -5 4\n'
        for metodo in ('bruto', 'divisao'):
            with self.subTest(metodo=metodo):
                resultado = self.executar('subarranjo', metodo, entrada)
                self.assertEqual(resultado.returncode, 0)
                self.assertEqual(resultado.stdout.strip(), '6 3 6')
                self.assertEqual(resultado.stderr, '')

    def test_subarranjo_so_negativos(self):
        entrada = '4\n-9 -3 -3 -8\n'
        for metodo in ('bruto', 'divisao'):
            with self.subTest(metodo=metodo):
                resultado = self.executar('subarranjo', metodo, entrada)
                self.assertEqual(resultado.returncode, 0)
                self.assertEqual(resultado.stdout.strip(), '-3 1 1')

    def test_pontos_exemplo_nos_dois_metodos(self):
        entrada = '4\n-1 0\n-100 5\n1 0\n100 5\n'
        for metodo in ('bruto', 'divisao'):
            with self.subTest(metodo=metodo):
                resultado = self.executar('pontos', metodo, entrada)
                self.assertEqual(resultado.returncode, 0)
                self.assertEqual(resultado.stdout.strip(), '2 0 2')

    def test_pontos_decimal_e_limiar_customizado(self):
        entrada = '3\n0.5 0.5\n0.5 1.5\n50 50\n'
        resultado = self.executar('pontos', 'divisao', entrada, '--limiar', '16')
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout.strip(), '1 0 1')

    def test_saida_detalhada(self):
        entrada = '4\n-1 0\n-100 5\n1 0\n100 5\n'
        resultado = self.executar('pontos', 'divisao', entrada, '--detalhado')
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(
            resultado.stdout.strip(),
            'distancia=2 distancia_quadrada=4 ponto1=0 ponto2=2',
        )

    def test_entrada_vazia_retorna_erro(self):
        resultado = self.executar('subarranjo', 'bruto', '')
        self.assertEqual(resultado.returncode, 2)
        self.assertEqual(resultado.stdout, '')
        self.assertIn('Erro de entrada:', resultado.stderr)

    def test_quantidade_incorreta_retorna_erro(self):
        resultado = self.executar('pontos', 'divisao', '3\n0 0\n1 1\n')
        self.assertEqual(resultado.returncode, 2)
        self.assertEqual(resultado.stdout, '')
        self.assertIn('Erro de entrada:', resultado.stderr)


if __name__ == '__main__':
    unittest.main()
