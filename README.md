# 🛰️ SCIC - Sistema de Comunicação Interplanetária da Colônia

> Protótipo em Python para organizar, analisar e priorizar dados de comunicação da colônia **Aurora Siger**.

## 👥 Equipe

| Nome | RM |
|------|----|
| Ana Gabriela | rm571312 |
| Kaique | rm570533 |
| Miguel Antunes | rm573643 |
| Miguel Gonçalves | rm573793 |

## 📌 Sobre o projeto

A Aurora Siger é uma colônia fictícia cujos módulos (habitação, agricultura, comunicação, comando, energia,
laboratório, suporte médico, armazenamento de dados e sensores externos) dependem de uma comunicação
interplanetária com latência alta e variável. O **SCIC** ajuda a equipe a:

- organizar os dados operacionais e de comunicação dos módulos;
- medir a diferença entre a latência prevista e a observada (erro absoluto e relativo);
- estimar a latência com um modelo simples e avaliar sua confiabilidade;
- decidir **quais alertas tratar primeiro** (heap);
- localizar módulos, tipos e sensores **por prefixo** (trie);
- relacionar o sistema a dispositivos de E/S, bases numéricas e eletricidade básica;
- gerar uma análise final de apoio à decisão.

## ✨ Funcionalidades

| Menu | Funcionalidade | Conceito aplicado |
|:---:|---|---|
| 1 | Carregar/consultar registros | Pandas, limpeza de dados, contagem por status |
| 2 | Indicadores e erros (absoluto/relativo) | Análise numérica, ponto flutuante |
| 3 | Modelo de previsão e métricas | Regressão linear, treino/teste, MAE, MSE, RMSE, R² |
| 4 | Priorizar alertas | Heap (max-heap, heapify-up/down) |
| 5 | Buscar por prefixo | Trie |
| 6 | Dispositivos, bases numéricas e eletricidade | E/S, hex/bin/dec, P = V·I, Lei de Ohm |
| 7 | Analisar alertas de comunicação (análise final) | Síntese dos resultados |
| 0 | Sair | - |

## 🗂️ Estrutura do repositório

```
.
├── codigo_fonte.py           
├── dados_aurora_siger.csv     
├── README.md                  
├── relatorio_tecnico.md       
├── link_video.txt             
```

## ⚙️ Instalação e execução

 Python 3.9 ou superior.

```bash
# 1. Clone o repositório

# 2. Instale as dependências
pip install numpy pandas matplotlib scikit-learn

# 3. Execute o sistema
python codigo_fonte.py
```

## 📊 Dados

Base simulada com **30 registros** (10 módulos × 3 ciclos) e 14 campos:

| Campo | Descrição |
|---|---|
| `modulo`, `tipo` | Nome e tipo do módulo |
| `codigo_sensor` | Código do sensor em hexadecimal (ex.: `0xA001`) |
| `ciclo` | Ciclo de registro (1 a 3) |
| `tensao_V`, `corrente_A`, `potencia_W` | Grandezas elétricas (P = V × I) |
| `carga_pct` | Percentual de uso do módulo |
| `latencia_obs_ms`, `latencia_prev_ms` | Latência observada e prevista |
| `status` | `ativo`, `manutenção` ou `alerta` |
| `essencial` | 1 se o módulo é essencial para a colônia, 0 caso contrário |
| `prioridade_base` | Prioridade de 1 (baixa) a 5 (crítica) |
| `mensagem` | Mensagem resumida do alerta |


## 🔍 Como funciona

### Erros numéricos
- **Erro absoluto** = |latência observada − latência prevista|
- **Erro relativo** = erro absoluto / |latência observada| × 100


### Modelo e métricas
Regressão linear que estima a latência observada a partir de **carga (%)** e **potência (W)**, com 70 % dos dados
para treino e 30 % para teste.

| Métrica | Resultado |
|---|---|
| MAE | 21,13 ms |
| MSE | 731,22 |
| RMSE | 27,04 ms |
| R² | 0,38 |


### Priorização de alertas (heap)
Pontuação = `3 × prioridade_base` + `5 se módulo essencial` + `0,5 × erro relativo (%)` + `4 se status = alerta`.

O **max-heap** (implementado manualmente) mantém o alerta mais urgente na raiz. A inserção usa *heapify-up* e a remoção
usa *heapify-down*, ambas em **O(log n)**, contra O(n) ou O(n log n) de uma lista simples.

### Busca por prefixo (trie)
Armazena módulos, tipos e códigos de sensor, sem diferenciar acentos ou maiúsculas. A busca percorre só o caminho do prefixo,
então o custo depende do tamanho do prefixo e não da quantidade de registros.

```
> com   ->  Comando Central, Comunicação Principal, comunicação
> hab   ->  Habitação Alfa, Habitação Beta, habitação
> 0xA0  ->  0xA001, 0xA002, ... (30 códigos de sensor)
```

### Dispositivos, bases numéricas e eletricidade
- **Entrada:** sensores e medidores simulados. **Saída:** terminal, relatório e gráficos.
- O código `0xA001` equivale a 40961 (decimal) e `1010000000000001` (binário).
- Para V = 12 V e I = 2,04 A: P = V × I = **24,48 W** e R = V / I = **5,88 Ω** (Lei de Ohm).

### Exemplo de saída (fila de alertas)

```
6 alertas inseridos no heap.

1º | pontuação  39.47 | Armazenamento de Dados (ciclo 3) | erro rel. 42.9% | Latência acima do previsto
2º | pontuação  35.57 | Habitação Alfa (ciclo 1) | erro rel. 39.1% | Latência acima do previsto
3º | pontuação  35.00 | Agricultura Hidropônica (ciclo 3) | erro rel. 38.0% | Latência acima do previsto
4º | pontuação  33.02 | Suporte Médico (ciclo 1) | erro rel. 30.0% | Latência acima do previsto
5º | pontuação  23.62 | Sensores Externos (ciclo 3) | erro rel. 33.2% | Latência acima do previsto
```

## 🌱 Gerenciamento inteligente, sustentabilidade e responsabilidade

O relatório relaciona o SCIC a sensores e medidores inteligentes, monitoramento contínuo, automação, redundância de enlaces,
manutenção preditiva e microrredes. Também discute o uso eficiente da comunicação para reduzir desperdício, a inspiração em
saberes indígenas de uso consciente dos recursos, a revisão dos pesos da pontuação para evitar viés, a transparência da fórmula
e a **validação humana** das decisões automatizadas. Detalhes em [`relatorio_tecnico.md`](relatorio_tecnico.md).


## 🎥 Vídeo de apresentação

https://youtu.be/3Oig8-A9MMY


