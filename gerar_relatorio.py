"""Gera gráficos e relatório PDF (máximo 8 páginas) a partir dos CSVs reais."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether)

BASE = Path(__file__).resolve().parent
RES = BASE / 'resultados'
PDF = BASE / 'relatorio' / 'Relatorio_Divisao_e_Conquista.pdf'
MEDIA = list(csv.DictReader((RES / 'resumo_medicoes.csv').open(encoding='utf-8')))
META = json.loads((RES / 'ambiente_e_protocolo.json').read_text(encoding='utf-8'))

pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold')

INK = colors.HexColor('#14263B')
BLUE = colors.HexColor('#145A88')
LIGHT = colors.HexColor('#ECF2F6')
MUTED = colors.HexColor('#465566')
BRUTE = '#D76C3B'
DIV = '#1670A7'

styles = {
 'cap': ParagraphStyle('cap', fontName='DejaVu', fontSize=9, leading=13, textColor=BLUE, spaceAfter=7),
 'titulo': ParagraphStyle('titulo', fontName='DejaVu-Bold', fontSize=25, leading=33, textColor=INK, spaceAfter=13),
 'subcapa': ParagraphStyle('subcapa', fontName='DejaVu', fontSize=14, leading=21, textColor=BLUE, spaceAfter=20),
 'h1': ParagraphStyle('h1', fontName='DejaVu-Bold', fontSize=15, leading=21, textColor=INK, spaceBefore=0, spaceAfter=12),
 'h2': ParagraphStyle('h2', fontName='DejaVu-Bold', fontSize=11, leading=16, textColor=BLUE, spaceBefore=8, spaceAfter=5),
 'p': ParagraphStyle('p', fontName='DejaVu', fontSize=9.0, leading=14.2, textColor=INK, spaceAfter=8),
 'sm': ParagraphStyle('sm', fontName='DejaVu', fontSize=8.0, leading=12.7, textColor=INK, spaceAfter=7),
 'tiny': ParagraphStyle('tiny', fontName='DejaVu', fontSize=7.0, leading=10.3, textColor=MUTED, spaceAfter=4),
 'tb': ParagraphStyle('tb', fontName='DejaVu', fontSize=8.1, leading=12, textColor=INK),
 'th': ParagraphStyle('th', fontName='DejaVu-Bold', fontSize=8.0, leading=11, textColor=colors.white),
}

def par(texto, st='p'):
    return Paragraph(texto, styles[st])


def title(st, *text):
    return [par(t, st) for t in text]


def tabela(linhas, widths, header=True):
    celulas = []
    for i, linha in enumerate(linhas):
        st = 'th' if i == 0 and header else 'tb'
        celulas.append([par(str(c), st) for c in linha])
    t = Table(celulas, colWidths=widths, hAlign='LEFT', repeatRows=1 if header else 0)
    comandos = [('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('LEFTPADDING',(0,0),(-1,-1),9), ('RIGHTPADDING',(0,0),(-1,-1),8),
                ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LINEBELOW',(0,-1),(-1,-1),0.5,colors.HexColor('#D6E1E9'))]
    if header:
        comandos += [('BACKGROUND',(0,0),(-1,0),INK),
                     ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, LIGHT])]
    t.setStyle(TableStyle(comandos))
    return t


def registros(problema):
    vals={}
    for d in MEDIA:
        if d['problema'] == problema:
            vals[(int(d['n']), d['metodo'])] = float(d['media_ms'])
    return vals


def fmt(x, casas=3):
    return f'{x:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X','.')


def grafico(problema, nome):
    d = registros(problema)
    ns = sorted({n for n, _ in d})
    yb = [d[(n, 'bruto')] for n in ns]
    yd = [d[(n, 'divisao')] for n in ns]
    def referencia(y, ordem):
        p = ns.index(400)
        return [y[p] * (ordem(n)/ordem(ns[p])) for n in ns]
    fig, ax = plt.subplots(figsize=(8.1, 3.75))
    ax.plot(ns,yb, color=BRUTE, marker='o', lw=2.2, label='Força bruta: média real')
    ax.plot(ns,yd, color=DIV, marker='s', lw=2.2, label='Divisão e conquista: média real')
    import math
    ax.plot(ns, referencia(yb, lambda n: n*n), color=BRUTE, ls='--', alpha=.5, lw=1.35, label='Referência n²')
    ax.plot(ns, referencia(yd, lambda n: n*math.log2(n)), color=DIV, ls='--', alpha=.5, lw=1.35, label='Referência n log₂ n')
    ax.set(xlabel='Tamanho da entrada (n)',ylabel='Tempo médio (ms)')
    ax.set_xscale('log',base=2)
    ax.set_yscale('log')
    ax.set_xticks(ns, [f'{n:,}'.replace(',','.') for n in ns])
    ax.grid(True,which='major',alpha=.23)
    ax.legend(loc='upper left', ncol=2, fontsize=8, frameon=False)
    fig.tight_layout(pad=1.3)
    destino = RES / nome
    fig.savefig(destino, dpi=185, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return destino

GRAF_S = grafico('subarranjo','grafico_subarranjo.png')
GRAF_P = grafico('pontos','grafico_pontos.png')

class Doc(BaseDocTemplate):
    def __init__(self, nome):
        BaseDocTemplate.__init__(self, str(nome), pagesize=A4, leftMargin=44, rightMargin=44,
                                 topMargin=55, bottomMargin=52, title='Divisão e Conquista - Relatório Experimental',
                                 author='Dupla - Complexidade e Análise de Algoritmos')
        w,h=A4
        area=Frame(44,52,w-88,h-107,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='paginas', frames=area, onPage=self.decorar))

    def decorar(self, canvas, doc):
        w,h=A4
        canvas.setStrokeColor(colors.HexColor('#C9D8E2'))
        canvas.setLineWidth(.7)
        canvas.line(44,h-38,w-44,h-38)
        canvas.setFont('DejaVu',8)
        canvas.setFillColor(MUTED)
        canvas.drawString(44,h-30,'UNIFOR  /  COMPLEXIDADE E ANÁLISE DE ALGORITMOS')
        canvas.line(44,40,w-44,40)
        canvas.drawString(44,26,'Trabalho prático - Divisão e Conquista  |  27/10/2026')
        canvas.drawRightString(w-44,26,f'Página {doc.page}')

STORY=[]
def add(*items): STORY.extend(items)
def space(n=6): add(Spacer(1,n))
def newpage(): add(PageBreak())

# Página 1 — capa executiva
space(86)
add(par('TRABALHO PRÁTICO  •  2026.2','cap'))
add(par('DIVISÃO E<br/>CONQUISTA','titulo'))
add(par('Implementação, testes e análise experimental','subcapa'))
add(HRFlowable(width='100%',thickness=2,color=BLUE,spaceAfter=18))
add(par('<b>Instituição:</b> Universidade de Fortaleza (UNIFOR)','p'))
add(par('<b>Disciplina:</b> Complexidade e Análise de Algoritmos','p'))
add(par('<b>Integrante 1:</b> Yuri Freitas Andrade Maia — 2510459','p'))
add(par('<b>Integrante 2:</b> Fernando Jose Simon Heck — 2510386','p'))
add(par('<b>Data:</b> 27 de outubro de 2026  |  <b>Entrega:</b> 28 de outubro de 2026','p'))
space(22)
add(par('Resumo','h1'))
add(par('Comparam-se quatro implementações em dois problemas: subarranjo de soma máxima e par de pontos mais próximo. Cada problema possui uma solução quadrática por força bruta e uma solução recursiva de divisão e conquista com ordem Θ(n log n). A validade foi examinada por casos de borda e testes diferenciais. Os tempos são medições efetivas em sete dimensões de entrada, com cinco execuções por combinação, registradas integralmente em CSV. O relatório apresenta as recorrências, a justificativa dos sete vizinhos, a escolha experimental do caso-base e as limitações do ambiente.','p'))
space(10)
add(par('<b>Escopo:</b> exclusivamente Etapas 1, 2 e 3 do enunciado; a questão desafio foi excluída, conforme solicitado.','sm'))
newpage()

# Página 2 — subarranjo
add(par('1. Subarranjo de soma máxima','h1'))
add(par('A entrada é um inteiro n seguido de n valores inteiros, positivos ou negativos. A saída é uma tripla (soma máxima, início, fim), em índices baseados em zero e ambos inclusivos. O subarranjo deve ser não vazio. Para desempatar somas iguais, adota-se o menor índice inicial e, persistindo o empate, o menor índice final.','p'))
add(par('1.1. Solução por força bruta','h2'))
add(par('O algoritmo fixa cada posição inicial e estende incrementalmente o limite final, atualizando a soma sem refazer a varredura. Examina todos os n(n + 1)/2 intervalos. Sua recorrência equivalente de custo é <b>T(n) = T(n − 1) + Θ(n)</b>, com T(1) = Θ(1); portanto, <b>T(n) = Θ(n²)</b>. O espaço auxiliar é Θ(1).','p'))
add(par('1.2. Solução por divisão e conquista','h2'))
add(par('Divide-se o vetor em duas metades, resolve-se a melhor soma em cada uma recursivamente e avalia-se o melhor intervalo que atravessa a posição central. A combinação faz uma passagem pela metade esquerda para obter o melhor sufixo e outra pela metade direita para obter o melhor prefixo. A melhor das três respostas resolve o problema completo.','p'))
add(par('A recorrência é <b>T(n) = 2T(n/2) + Θ(n)</b>, com T(1) = Θ(1). Pelo caso 2 do Teorema Mestre, n<super>log₂2</super> = n e f(n) = Θ(n), logo <b>T(n) = Θ(n log n)</b>. Profundidade de pilha: Θ(log n), com espaço adicional Θ(log n), além da entrada.','p'))
add(par('1.3. Argumento de correção','h2'))
add(par('Qualquer intervalo ótimo está integralmente à esquerda, integralmente à direita ou cruza a divisão. Por hipótese indutiva, os dois primeiros casos são calculados corretamente. No terceiro, toda solução que cruza o meio é a soma de um sufixo da esquerda e de um prefixo da direita, ambos maximizados pelas varreduras. Assim, escolher o melhor dos três candidatos é suficiente.','p'))
add(par('1.4. Testes críticos','h2'))
add(tabela([
 ['Situação','Comportamento esperado'],
 ['Todos negativos','Selecionar o maior elemento, sem aceitar intervalo vazio.'],
 ['n = 1','Retornar o único índice e o próprio valor.'],
 ['Empates','Aplicar início menor; em seguida fim menor.'],
 ['Intervalo cruzado','Combinar prefixo e sufixo corretos.'],
 ],[150,357]))
newpage()

# Página 3 — closest pair
add(par('2. Par de pontos mais próximo','h1'))
add(par('Cada estação é um par (x, y). A saída informa dois índices distintos da entrada, sua distância euclidiana e seu quadrado. As distâncias são comparadas ao quadrado, evitando raízes desnecessárias e preservando precisão para coordenadas inteiras.','p'))
add(par('2.1. Solução por força bruta','h2'))
add(par('Cada ponto é comparado com todos os seguintes: há n(n − 1)/2 pares. Uma recorrência para o custo das comparações é <b>T(n) = T(n − 1) + Θ(n)</b> (base n = 2), que se resolve em <b>Θ(n²)</b>; espaço auxiliar Θ(1).','p'))
add(par('2.2. Divisão e conquista em O(n log n)','h2'))
add(par('Os pontos são ordenados inicialmente por x e por y. A lista por x é dividida na mediana; para cada chamada recursiva, a sequência ordenada por y é particionada em uma única passagem. Obtém-se a menor distância δ das duas metades, constrói-se uma faixa |x − x<sub>mediana</sub>| ≤ δ e percorrem-se os pontos ordenados por y. Cada ponto é comparado apenas aos sete seguintes, descartando candidatos cuja diferença vertical já exceda a distância corrente.','p'))
add(par('A combinação custa Θ(n), pois mantém as listas ordenadas por y, realiza particionamentos lineares e faz no máximo 7 comparações por ponto. Portanto, <b>T(n) = 2T(n/2) + Θ(n) = Θ(n log n)</b>. As ordenações iniciais também têm custo O(n log n); o espaço auxiliar total é O(n).','p'))
add(par('2.3. Por que bastam sete vizinhos?','h2'))
add(par('Para um ponto p na faixa, só interessam sucessores em y separados por no máximo δ. Esses pontos cabem em um retângulo de largura 2δ e altura δ imediatamente acima de p. Corte-o pela linha mediana em duas regiões de largura δ; subdivida cada uma em quatro quadrados de lado δ/2. Existem oito quadrados. Como a diagonal de cada quadrado é δ/√2, inferior a δ, não cabem dois pontos da mesma metade num mesmo quadrado: isso contradiz a definição de δ como menor distância interna. Assim, incluindo p, há no máximo oito pontos nesse retângulo, isto é, no máximo sete possíveis sucessores a verificar.','p'))
add(par('2.4. Duplicatas e caso-base','h2'))
add(par('Pontos coincidentes são detectados na lista inicialmente ordenada por x e produzem distância zero (ótima global), evitando tratar δ = 0 como uma faixa degenerada. Para subproblemas de até um limiar constante, a busca exaustiva reduz overhead recursivo sem alterar a ordem assintótica. O limiar foi selecionado por calibração real descrita na Seção 4.','p'))
newpage()

# Página 4 — protocolo
add(par('3. Metodologia de avaliação','h1'))
add(par('3.1. Instrumentação e repetibilidade','h2'))
add(par('Foram executadas <b>5 repetições independentes de cronometragem por tamanho e por método</b>. O cronômetro <b>time.perf_counter_ns()</b> mede apenas a execução do algoritmo: geração de dados, validação prévia e aquecimento são externos ao intervalo cronometrado. São armazenados tempos em nanossegundos e calculados média, desvio amostral, mínimo e máximo em milissegundos.','p'))
add(par('As dimensões foram n = 100, 200, 400, 800, 1.600, 3.200 e 6.400. No enunciado aparece a palavra “dígitos” para a Etapa 2; ela foi interpretada como <b>quantidade de pontos</b>, coerente com o problema. Para cada valor de n, ambas as estratégias recebem exatamente o mesmo conjunto de dados, evitando diferenças de dificuldade entre execuções.','p'))
add(par('3.2. Perfil das entradas','h2'))
add(tabela([
 ['Problema','Geração determinística'],
 ['Subarranjo','n inteiros uniformes no intervalo [−100, 100]; semente 120000 + n.'],
 ['Pontos','n pares de inteiros sem duplicatas, x e y entre −10⁶ e 10⁶; semente 220000 + n; ordem embaralhada.'],
 ],[112,395]))
space(7)
add(par('3.3. Máquina utilizada nas medições','h2'))
maq=META['maquina']
q=maq['quota_cpu_cgroup']; mem=maq['limite_memoria_cgroup_bytes']
memg=f'{int(mem)/1073741824:g} GiB' if mem.isdigit() else mem
add(tabela([
 ['Item','Ambiente observado'],
 ['Processador (identificação exposta)',maq['processador_identificado']],
 ['CPU disponível',f"{maq['cpus_visiveis']} CPUs lógicas visíveis; quota cgroup: {q}"],
 ['Memória limitada por cgroup',memg],
 ['Sistema operacional',maq['sistema']],
 ['Linguagem / relógio',f"Python {maq['python']} / perf_counter_ns"],
 ],[185,322]))
space(7)
add(par('<b>Advertência de reprodutibilidade:</b> os testes foram executados num contêiner Linux disponibilizado durante a geração do trabalho, não no computador pessoal da dupla. Limites de CPU, virtualização, frequência e ruído do ambiente podem alterar as constantes de tempo. Os CSVs, a configuração e as sementes estão registrados no repositório para reexecução local.','sm'))
newpage()

# Página 5 — results 1
add(par('4. Resultados — subarranjo de soma máxima','h1'))
d=registros('subarranjo')
linhas=[['n','Força bruta (ms)','Divisão (ms)','Aceleração']]
for n in META['tamanhos']:
    a,b=d[(n,'bruto')],d[(n,'divisao')]
    linhas.append([f'{n:,}'.replace(',','.'),fmt(a),fmt(b),fmt(a/b,1)+'×'])
add(tabela(linhas,[68,153,141,145]))
space(14)
add(Image(str(GRAF_S),width=490,height=227))
add(par('Figura 1. Médias de cinco execuções por tamanho; escala logarítmica em ambos os eixos. As linhas tracejadas são referências teóricas reescaladas no ponto n = 400, não medidas adicionais.','tiny'))
add(par('4.1. Interpretação','h2'))
a0,b0=d[(100,'bruto')],d[(100,'divisao')]
a1,b1=d[(6400,'bruto')],d[(6400,'divisao')]
add(par(f'Para n = 100, a força bruta levou {fmt(a0)} ms, contra {fmt(b0)} ms da divisão e conquista (ganho de {fmt(a0/b0,1)}×). Em n = 6.400, os tempos passaram a {fmt(a1)} ms e {fmt(b1)} ms (ganho de {fmt(a1/b1,1)}×). O crescimento acelerado da curva quadrática e o menor declive da curva n log n são compatíveis com as recorrências; pequenas oscilações refletem custos de interpretação, alocação, cache e escalonamento.','p'))
newpage()

# Página 6 — results 2
add(par('5. Resultados — par de pontos mais próximo','h1'))
d=registros('pontos')
linhas=[['n','Força bruta (ms)','Divisão (ms)','Aceleração']]
for n in META['tamanhos']:
    a,b=d[(n,'bruto')],d[(n,'divisao')]
    linhas.append([f'{n:,}'.replace(',','.'),fmt(a),fmt(b),fmt(a/b,1)+'×'])
add(tabela(linhas,[68,153,141,145]))
space(12)
add(Image(str(GRAF_P),width=490,height=220))
add(par('Figura 2. Comparação em escala log–log das medições reais com duas curvas de referência n² e n log₂ n, ajustadas em n = 400.','tiny'))
add(par('5.1. Seleção justificada do limiar','h2'))
cal=META['calibracao_media_ns']
heads=['Limiar','n = 200','n = 800','n = 3.200']
rows=[heads]
for k in META['limiares_testados']:
    rows.append([str(k) + (' (adotado)' if k == META['limiar_escolhido'] else ''),
                 *[fmt(float(cal[str(n)][str(k)])/1e6,3) for n in (200,800,3200)]])
add(tabela(rows,[139,110,115,143]))
add(par(f"Tabela de calibração em ms (cinco repetições por célula). Critério: menor média geométrica das razões entre o tempo observado e o melhor tempo de cada tamanho, atribuindo peso igual aos três n. O limiar <b>{META['limiar_escolhido']}</b> apresentou a melhor pontuação nesse protocolo; a amostra não demonstra que ele seja ótimo em toda máquina.", 'sm'))
newpage()

# Página 7 — discussão e testes
add(par('6. Comparação, validade e conclusão','h1'))
dp=registros('pontos'); ds=registros('subarranjo')
add(par('6.1. Crescimento e pontos de cruzamento','h2'))
add(par('As duas soluções por força bruta realizam número quadrático de operações; as variantes recursivas mantêm o custo O(n log n) à custa de ordenação, particionamento ou pilha de chamadas. Para entradas pequenas, uma implementação exaustiva pode vencer por ter menos overhead e estruturas auxiliares, embora isso não tenha ocorrido nos sete tamanhos principais desta máquina. Os cruzamentos, quando existentes, dependem de compilador/interpretador, tamanho e distribuição da entrada, limiar, memória e carga de CPU; não são determinados apenas pela notação O.','p'))
add(par('6.2. Cobertura e correção','h2'))
add(tabela([
 ['Verificação','Cobertura'],
 ['Casos documentados','11 vetores e 11 coleções de pontos, com entrada e saída esperada em JSON.'],
 ['Subarranjo','3.200 entradas pseudoaleatórias; saída completa comparada à força bruta.'],
 ['Par de pontos','1.000 entradas pseudoaleatórias em seis limiares, mais 60 sem repetição.'],
 ['Condições especiais','n mínimo, negativos, zeros, empates, cruzamento, x repetido, coincidência, colinearidade, valores altos e fracionários.'],
 ['Entradas inválidas','Quantidade insuficiente, tipos impróprios e coordenadas não finitas.'],
 ],[155,352]))
space(10)
add(par('6.3. Reprodutibilidade e limitações','h2'))
add(par('O arquivo <b>resultados/medicoes_brutas.csv</b> contém os 140 tempos individuais (4 algoritmos × 7 tamanhos × 5 rodadas). O arquivo <b>resumo_medicoes.csv</b> contém médias e desvios; <b>calibracao_limiar.csv</b> registra as 75 medições de limiar; <b>ambiente_e_protocolo.json</b> detalha o hardware observável e as sementes. Os comandos completos constam do README.','p'))
add(par('A análise empírica verifica tendências no intervalo testado, não prova limites assintóticos sozinha. Tempos de uma máquina virtual contêm interferência e não podem ser apresentados como resultados de uma estação física da dupla. A implantação num repositório Git remoto e seu histórico distribuído precisam ser realizados pelos integrantes; as versões históricas de semanas anteriores não foram inventadas.','p'))
add(par('6.4. Conclusão','h2'))
add(par('Ambos os problemas admitem soluções diretas Θ(n²) e soluções de divisão e conquista Θ(n log n). A teoria, a validação funcional e as medições são coerentes: conforme n cresce, a variante recursiva amplia a vantagem sobre força bruta. A Etapa 2 exige atenção adicional à ordenação por y, à faixa de até sete vizinhos, a pontos coincidentes e à escolha do limiar, abordados na implementação.','p'))
add(par('<b>Referências didáticas:</b> Enunciado “Trabalho Prático: Divisão e Conquista”; material da disciplina “Aula 05 — Teorema Mestre” e “Aula 07 — Introdução à Construção de Algoritmos: Divisão e Conquista”.','tiny'))

PDF.parent.mkdir(parents=True,exist_ok=True)
Doc(PDF).build(STORY)
print('PDF:', PDF)
