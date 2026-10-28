# Publicação no GitHub

**Situação:** repositório publicado e acessível.

**Endereço:** https://github.com/yurifam/trabalho-divisao-conquista

**Dupla:**
- Yuri Freitas Andrade Maia — 2510459
- Fernando Jose Simon Heck — 2510386

## Como baixar a versão publicada

```bash
git clone https://github.com/yurifam/trabalho-divisao-conquista.git
cd trabalho-divisao-conquista
```

## Como executar os testes

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem as funções dos dois problemas e também a interface de linha de comando. O relatório em PDF, gráficos e CSVs estão nas pastas `relatorio/` e `resultados/`.

## Atualizações posteriores

Para registrar alterações reais na máquina de um integrante, dentro do projeto:

```bash
git add .
git commit -m "Descreva objetivamente a melhoria realizada"
git push origin main
```

O histórico do Git registra quando os commits realmente ocorreram; não demonstra semanas de desenvolvimento que não estejam documentadas. Não altere datas para sugerir atividade inexistente.
