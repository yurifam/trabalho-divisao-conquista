# Trabalho Prático — Divisão e Conquista

**Disciplina:** Complexidade e Análise de Algoritmos — UNIFOR  
**Prazo indicado no enunciado:** 28/10/2026  
**Equipe:** dupla; Yuri Freitas Andrade Maia (2510459) e **[preencher segundo integrante e matrícula]**.  
**Escopo:** Etapas 1, 2 e 3. A questão desafio NÃO foi implementada, conforme solicitado.

Este repositório implementa, testa e compara soluções de **força bruta** e **divisão e conquista** para os dois problemas exigidos, com resultados experimentais **efetivamente medidos** e relatados em sete páginas de PDF.

## 1. Estrutura dos arquivos

```text
.
├── README.md
├── main.py                       # Entrada e saída via terminal
├── src/
│   ├── __init__.py
│   └── algoritmos.py             # Quatro implementações
├── tests/
│   ├── casos_teste.json          # Entradas e saídas esperadas (22 casos)
│   ├── entradas_e_saidas.txt     # Versão legível com exemplos prontos
│   └── test_algoritmos.py        # Bateria automatizada e diferencial
├── benchmark.py                  # 5 medições reais por método/tamanho
├── gerar_relatorio.py             # Gera gráficos e PDF a partir do CSV
├── requirements-relatorio.txt    # Bibliotecas opcionais para gerar o PDF
├── resultados/
│   ├── medicoes_brutas.csv       # 140 tempos medidos em nanossegundos
│   ├── resumo_medicoes.csv       # Médias e desvios em milissegundos
│   ├── calibracao_limiar.csv     # 75 medições de tamanho do caso-base
│   ├── ambiente_e_protocolo.json # Máquina, versão Python, seeds etc.
│   ├── grafico_subarranjo.png
│   └── grafico_pontos.png
└── relatorio/
    └── Relatorio_Divisao_e_Conquista.pdf
```

## 2. Pré-requisitos

- Python **3.10 ou mais novo**;
- Para executar os quatro algoritmos e testes: **nenhuma biblioteca externa**;
- Para **regerar** gráficos e relatório: `pip install -r requirements-relatorio.txt`.

Execute os comandos no diretório do projeto. Os exemplos abaixo funcionam no terminal Linux/macOS; no PowerShell, a entrada também pode ser fornecida por arquivo, como indicado.

## 3. Como executar — Etapa 1

A entrada é `n` seguido por `n` inteiros. Os índices apresentados são **base zero**, início e fim **inclusivos**. Subarranjos devem ser **não vazios**. Em empate de soma, vence o menor índice de início; depois o menor índice de fim.

**Exemplo de entrada:**

```text
9
-2 1 -3 4 -1 2 1 -5 4
```

**Força bruta:**

```bash
python main.py subarranjo bruto < exemplos/subarranjo.txt
```

**Divisão e conquista:**

```bash
python main.py subarranjo divisao < exemplos/subarranjo.txt
```

**Saída esperada para ambos:**

```text
6 3 6
```

## 4. Como executar — Etapa 2

A entrada é `n` seguido de `n` linhas `x y`. Coordenadas inteiras ou reais são aceitas. A saída apresenta a distância euclidiana, a distância ao quadrado e o par de índices da entrada, iniciando em zero. Se houver mais de um par com distância mínima, **qualquer um é resposta correta**.

**Exemplo de entrada:**

```text
4
-1 0
-100 5
1 0
100 5
```

**Força bruta:**

```bash
python main.py pontos bruto < exemplos/pontos.txt
```

**Divisão e conquista:**

```bash
python main.py pontos divisao < exemplos/pontos.txt
```

**Saída esperada para ambos:**

```text
2 0 2
```

O caso-base do algoritmo de divisão e conquista usa por padrão um limiar de **8 pontos**, calibrado experimentalmente, alterável por `--limiar 16` (por exemplo). A opção `--detalhado` imprime campos nomeados e também a distância ao quadrado; o modo padrão usa somente três valores, adequado para correção automática.

**Windows PowerShell:** use `Get-Content exemplos/subarranjo.txt | python main.py subarranjo divisao`; analogamente para o arquivo de pontos.

## 5. Como rodar a bateria de testes

```bash
python -m unittest discover -s tests -v
```

O arquivo `tests/casos_teste.json` oferece **22 casos documentados**, com a entrada e a saída esperadas. A suíte também compara as duas soluções em **3.200 vetores aleatórios**; usa **1.000 conjuntos de pontos** em seis limiares e outros **60 conjuntos sem duplicatas**; verifica a distância e os índices retornados; testa entradas inválidas.

As condições destacadas são: vetor apenas negativo, tamanho 1, empates, cruzamento do meio, todos zeros, pontos repetidos, x iguais, pontos colineares, empates entre pares, coordenadas negativas, valores grandes e coordenadas reais.

## 6. Reproduzir as medições e os gráficos

```bash
python benchmark.py
pip install -r requirements-relatorio.txt
python gerar_relatorio.py
```

O benchmark reexecuta a calibração de limiar com cinco valores (4, 8, 16, 32, 64) e registra, para cada algoritmo e n = 100, 200, 400, 800, 1600, 3200, 6400, **cinco medições**. As médias e os gráficos são derivados diretamente dos CSVs gravados.

- Cronômetro de alta resolução: `time.perf_counter_ns()`.
- Dataset gerado antes de iniciar o tempo cronometrado; aquecimento também fora do intervalo.
- Subarranjo: inteiros entre -100 e 100, seed `120000 + n`.
- Pontos: coordenadas inteiras aleatórias entre -1.000.000 e +1.000.000, sem duplicatas, **embaralhadas**, seed `220000 + n`.
- Todos os métodos de um mesmo problema e n usam **exatamente a mesma entrada**.
- Comparações de distância são feitas por **distância ao quadrado**; a raiz só é calculada ao exibir a saída.
- A medição pode apresentar variações de máquina para máquina. Use os CSVs existentes como evidência da execução registrada; para atribuir resultados ao PC da dupla, gere novas medidas nessa máquina.

As medições existentes foram realizadas em um **contêiner Linux** identificado como AMD EPYC 9V74 80-Core Processor, com limite de memória de 4 GiB, quota de CPU de 4 núcleos e Python 3.13.5. Não representam medições feitas no computador pessoal de nenhum integrante.

## 7. Resumo teórico

| Problema | Solução | Recorrência | Tempo | Espaço auxiliar |
| --- | --- | --- | --- | --- |
| Subarranjo | Força bruta | T(n) = T(n−1) + Θ(n) | Θ(n²) | Θ(1) |
| Subarranjo | Divisão e conquista | T(n) = 2T(n/2) + Θ(n) | Θ(n log n) | Θ(log n) |
| Par mais próximo | Força bruta | T(n) = T(n−1) + Θ(n) | Θ(n²) | Θ(1) |
| Par mais próximo | Divisão e conquista | T(n) = 2T(n/2) + Θ(n) | Θ(n log n) | Θ(n) |

Na Etapa 2, mantém-se a lista ordenada por y a cada nível; a faixa em torno da mediana compara no máximo **sete vizinhos seguintes por y**. O motivo geométrico está no relatório. Pontos coincidentes são identificados antes da recursão.

## 8. Git e entrega

Este diretório inclui um repositório Git local com commits realizados **na data real da preparação dos arquivos**. Não foi fabricado histórico retroativo de semanas anteriores. Para criar o repositório remoto (GitHub, GitLab etc.), algum integrante precisa autenticar-se e executar, após criar um repositório remoto vazio:

```bash
git remote add origin https://github.com/USUARIO/NOME-DO-REPOSITORIO.git
git branch -M main
git push -u origin main
```

Substitua o endereço de exemplo pela URL verdadeira. A URL acima **não é um repositório existente**. Antes de entregar, preencha o nome e matrícula do segundo integrante no **README e no relatório**, suba o projeto para um Git remoto e confira o link do repositório. O requisito de um histórico que reflita **semanas de desenvolvimento** não pode ser satisfeito retroativamente sem inventar datas.

## 9. Observações sobre a especificação

O texto do enunciado menciona “dígitos” na Etapa 2, porém o problema trata de pontos; por isso, adotam-se os tamanhos sugeridos como **quantidade de pontos**. Os arquivos não incluem resolução da “questão desafio”, deliberadamente desconsiderada.
