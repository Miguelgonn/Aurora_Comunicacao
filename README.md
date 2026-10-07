# 🛰️ SCIC - Sistema de Comunicação Interplanetária da Colônia

> Protótipo em Python para organizar, analisar e priorizar dados de comunicação da colônia **Aurora Siger**.

## 👥 Equipe

| Nome | RM |
|------|----|
| Ana Gabriela     | rm571312 |
| Kaique           | rm570533 |
| Miguel Antunes   | rm573643 |
| Miguel Gonçalves | rm573793 |

## 📌 Sobre o projeto

A Aurora Siger é uma colônia fictícia cujos módulos (habitação, agricultura, comunicação, controle,
comando, laboratório, suporte médico e armazenamento de dados) dependem de uma comunicação
interplanetária com latência alta e variável. O **SCIC** ajuda a equipe a:

- organizar os dados operacionais e de comunicação dos módulos;
- medir a diferença entre a latência prevista e a observada;
- estimar a latência com um modelo simples e avaliar sua confiabilidade;
- decidir **quais alertas tratar primeiro** (heap);
- localizar módulos, sensores e alertas **por prefixo** (trie);
- gerar uma análise final de apoio à decisão.

## ✨ Funcionalidades

| Menu | Funcionalidade | Conceito aplicado |
|:---:|---|---|
| 1 | Carregar dados da colônia (CSV) | NumPy, Pandas, limpeza de dados |
| 2 | Consultar registros por módulo ou status | Filtros em DataFrame |
| 3 | Erro absoluto e relativo (prevista × observada) | Análise numérica, ponto flutuante |
| 4 | Treinar modelo e avaliar | Regressão linear, treino/teste, MAE, MSE, RMSE, R² |
| 5 | Priorizar alertas | Heap (max-heap, heapify-up/down) |
| 6 | Busca por prefixo | Trie |
| 7 | Eletricidade, bases numéricas e E/S | P = V·I, Lei de Ohm, hex/bin/dec |
| 8 | Simulação da latência | Método de Euler |
| 9 | Análise final | Indicadores por módulo + gráfico |

## 🗂️ Estrutura do repositório

```
.
├── codigo_fonte.py           
├── dados_aurora_siger.csv    
├── relatorio_tecnico.md       
├── README.md                 
├── link_video.txt            
└── graficos_ou_imagens/       
```

## ⚙️ Instalação e execução

Python 3.9 ou superior.

```bash
# 1. Clone o repositório

# 2. Instale as dependências
pip install numpy pandas matplotlib scikit-learn

# 3. Execute
python codigo_fonte.py     
```


## 🔍 Como funciona

### Erros numéricos
- **Erro absoluto** = observada − prevista
- **Erro relativo** = erro absoluto / observada × 100
- Classificação: ≤ 10 % *aceitável*, 10-20 % *atenção*, > 20 % *preocupante*.

### Modelo e métricas
Regressão linear (carga, tráfego e potência → latência), com 70 % treino e 30 % teste.

| Métrica | Resultado |
|---|---|
| MAE | 27,28 ms |
| RMSE | 36,11 ms |
| R² | 0,924 |

Um único número não basta: o R² é alto, mas o RMSE maior que o MAE mostra que alguns registros têm erro maior.

### Priorização de alertas (heap)
Pontuação = `prioridade × 12` + `erro relativo (máx. 40)` + `30 se módulo essencial` + `20 se status = alerta`.
O **max-heap** mantém o alerta mais urgente na raiz; inserção e remoção custam **O(log n)**,
contra O(n) ou O(n log n) de uma lista simples.

### Busca por prefixo (trie)
Armazena módulos, códigos de sensores e mensagens, sem diferenciar acentos ou maiúsculas.

```
> com   ->  ['Comando', 'Comunicação']
> 0x1   ->  ['0x144', '0x157', '0x160', '0x186']
```

### Exemplo de saída (fila de alertas)

```
=== FILA DE ALERTAS (26 alertas) - mais urgentes primeiro ===
1. [ 126.8 pts] Suporte Médico  disp 0x5A7 | lat 761 ms | erro 16.8% | Perda de pacotes no enlace
2. [ 116.5 pts] Habitação       disp 0x892 | lat 767 ms | erro 18.5% | Perda de pacotes no enlace
3. [ 116.4 pts] Comando         disp 0xC12 | lat 920 ms | erro 36.4% | Perda de pacotes no enlace
```

## 🌱 Gerenciamento inteligente, sustentabilidade e responsabilidade

O relatório relaciona o SCIC a sensores e medidores inteligentes, monitoramento contínuo, redundância
de enlaces, manutenção preditiva e microrredes. Também discute o uso eficiente da comunicação para
reduzir desperdício, a inspiração em saberes indígenas de uso consciente dos recursos, a revisão dos pesos
para evitar viés e a **validação humana** das decisões automatizadas.

Detalhes completos em [`relatorio_tecnico.md`](relatorio_tecnico.md).

## ⚠️ Limitações e próximos passos

- Dados simulados e em pequeno volume; modelo linear simples.
- Melhorias possíveis: comparação de modelos com AIC/BIC, Grid/Random Search, validação cruzada,
  pesos de alerta configuráveis e dados de sensores reais.

## 🎥 Vídeo de apresentação

O link (YouTube, não listado) está em [`link_video.txt`](link_video.txt).


