# Relatório Técnico - SCIC (Sistema de Comunicação Interplanetária da Colônia)

**Projeto:** Aurora Siger | **Atividade:** Integradora

| Integrante | RM |
|---|---|
| Ana Gabriela | rm571312 |
| Kaique | rm570533 |
| Miguel Antunes | rm573643 |
| Miguel Gonçalves | rm573793 |

---

## 1. Contexto da solução

A Aurora Siger é uma colônia fictícia formada por módulos de comunicação, comando, energia, habitação,
agricultura, laboratório, suporte médico, armazenamento de dados e sensores externos. Todos dependem de uma
comunicação interplanetária com **latência alta e variável**: quando a latência real se afasta da prevista,
decisões operacionais podem ser tomadas com informação defasada.

O **SCIC** é um protótipo em Python que:

1. organiza os dados operacionais e de comunicação dos módulos;
2. mede a diferença entre a latência prevista e a observada (erro absoluto e relativo);
3. estima a latência com um modelo simples e avalia sua confiabilidade;
4. prioriza os alertas mais críticos com um **heap**;
5. permite consultar módulos, tipos e sensores por prefixo com uma **trie**;
6. conecta o sistema a dispositivos de E/S, bases numéricas e eletricidade básica;
7. gera uma análise final de apoio à decisão.

O sistema funciona em terminal, com um menu de 7 opções (`python codigo_fonte.py`).

## 2. Descrição dos dados

**Arquivo:** `dados_aurora_siger.csv`, base simulada com **30 registros** (10 módulos × 3 ciclos), gerada com
semente fixa (`42`) para ser reproduzível. Se o arquivo não existir, o programa o recria automaticamente.

| Campo | Descrição |
|---|---|
| `modulo`, `tipo` | Nome e tipo do módulo (comunicação, habitação, agricultura, laboratório, suporte médico, armazenamento de dados) |
| `codigo_sensor` | Código do sensor em hexadecimal (ex.: `0xA001`) |
| `ciclo` | Ciclo de registro (1 a 3) |
| `tensao_V`, `corrente_A`, `potencia_W` | Grandezas elétricas do transmissor; `potencia_W = tensão × corrente` |
| `carga_pct` | Percentual de uso do módulo |
| `latencia_obs_ms`, `latencia_prev_ms` | Latência observada e latência prevista |
| `status` | `ativo`, `manutenção` ou `alerta` |
| `essencial` | 1 se o módulo é essencial para a colônia, 0 caso contrário (15 dos 30 registros) |
| `prioridade_base` | Prioridade de 1 (baixa) a 5 (crítica) |
| `mensagem` | Mensagem resumida do alerta |

**Organização e limpeza (Pandas):** o CSV é lido com `pd.read_csv`; nulos e duplicados são removidos
(`dropna`, `drop_duplicates`). Listas e dicionários são usados na geração da base e nas estruturas do heap e da trie.

**Visão geral da base:**

- Status: 21 ativos, 6 em alerta e 3 em manutenção.
- Latência observada: média de **102,69 ms**, máxima de **184,51 ms** e desvio padrão de **31,10 ms**.
- Potência média: **56,98 W** (de 12,12 W a 187,20 W).

> Os dados são fictícios. A latência foi construída como função da carga e da potência, com ruído, e algumas
> anomalias foram injetadas de propósito (latência bem acima da prevista) para testar a detecção de alertas.

## 3. Indicadores e análise de erros

### 3.1 Definições

- **Erro absoluto** = |latência observada − latência prevista|, em ms.
- **Erro relativo** = erro absoluto / |latência observada| × 100, em %. Ele permite comparar módulos com escalas de latência diferentes.

### 3.2 Resultados

| Indicador | Valor |
|---|---|
| Erro absoluto médio | 15,32 ms |
| Erro relativo médio | 12,54 % |
| Erro relativo mediano | 8,04 % |
| Maior erro relativo | 42,94 % (Armazenamento de Dados, ciclo 3) |
| Registros com latência > 125 % da prevista | 6 |

A média (12,54 %) bem acima da mediana (8,04 %) indica que poucos registros com erro muito grande puxam a média para cima.
Os registros em alerta têm erro relativo médio de **34,4 %**, contra 7,4 % dos ativos e 4,5 % dos em manutenção.

### 3.3 Critério de aceitabilidade

| Faixa de erro relativo | Classificação | Registros |
|---|---|---|
| < 10 % | Aceitável | 19 |
| 10 % a 25 % | Atenção | 6 |
| > 25 % | Preocupante | 5 |

Em uma comunicação interplanetária, pequenos desvios são esperados e toleráveis. O erro vira preocupante quando a
latência real passa a diferir muito da prevista, pois a equipe deixa de confiar na estimativa. Em módulos essenciais
(comunicação, comando, energia, suporte médico e armazenamento) mesmo a faixa de atenção merece acompanhamento.

**Erro médio por módulo:**

| Módulo | Erro abs. (ms) | Erro rel. (%) | Classificação |
|---|---|---|---|
| Sensores Externos | 24,46 | 21,58 | atenção |
| Agricultura Hidropônica | 24,56 | 19,28 | atenção |
| Armazenamento de Dados | 31,70 | 19,24 | atenção |
| Habitação Alfa | 26,34 | 18,40 | atenção |
| Suporte Médico | 13,17 | 13,58 | atenção |
| Comunicação Principal | 11,98 | 11,60 | atenção |
| Habitação Beta | 7,63 | 7,03 | aceitável |
| Comando Central | 7,28 | 6,49 | aceitável |
| Controle de Energia | 3,61 | 4,46 | aceitável |
| Laboratório Científico | 2,42 | 3,73 | aceitável |

**Observação:** o erro absoluto de Armazenamento de Dados (31,70 ms) é o maior, mas o erro relativo de Sensores Externos
(21,58 %) é o maior entre os módulos. Isso mostra por que os dois indicadores devem ser lidos juntos.

### 3.4 Ponto flutuante e precisão numérica

O computador representa números decimais em binário, o que gera pequenas imprecisões: `0.1 + 0.2` resulta em
`0.30000000000000004`, e `0.1 + 0.2 == 0.3` é `False`. Por isso, o sistema compara valores com tolerância
(`np.isclose`) em vez de igualdade exata, e arredonda os valores apenas na exibição. Pequenas diferenças nos
cálculos de latência podem vir desse tipo de aproximação e não de uma falha real do enlace.

## 4. Modelo simples e avaliação de performance

**Modelo:** regressão linear (scikit-learn) que estima a **latência observada** a partir da **carga (%)** e da
**potência (W)**. Os dados foram divididos em **70 % para treino e 30 % para teste** (`random_state=42`).

- Coeficientes: carga = **0,874**; potência = **−0,106**; intercepto = **56,50**.

| Métrica | Valor |
|---|---|
| MAE | 21,13 ms |
| MSE | 731,22 |
| RMSE | 27,04 ms |
| R² | 0,38 |

### Interpretação

- **MAE = 21,13 ms:** em média, a previsão erra cerca de 21 ms, o que é relevante diante de uma latência média de ~103 ms.
- **RMSE = 27,04 ms:** é um pouco maior que o MAE, mas não passa de 1,3 vezes o MAE; os erros são relativamente
  homogêneos, sem um pequeno grupo de erros enormes dominando o resultado.
- **R² = 0,38:** o modelo explica apenas cerca de 38 % da variação da latência. É um desempenho **modesto**.
- **Um único número não basta:** um R² alto não garantiria um bom modelo, e aqui o R² baixo sozinho também não diz onde ele falha.
  A leitura conjunta de MAE, RMSE e R² mostra que o modelo captura a tendência geral, mas deixa de fora boa parte da variação.

### Por que o desempenho é modesto?

1. A base é **pequena** (30 registros; apenas ~9 no teste), então as métricas variam bastante conforme a divisão.
2. As **anomalias injetadas** nos dados não dependem de carga nem de potência, portanto uma regressão com essas duas variáveis não consegue explicá-las.
3. O modelo é **intencionalmente simples**, como pede a atividade.

Como a estimativa original (`latencia_prev_ms`) teve erro absoluto médio de 15,32 ms em toda a base, **o modelo não superou
a estimativa existente** neste conjunto. Esse é um resultado honesto e útil: indica que seriam necessárias mais variáveis
(tráfego, distância do enlace, histórico) e mais dados antes de adotar o modelo na operação.

Os gráficos `modelo_obs_vs_prev.png` (observado × previsto) e `erro_relativo_modulos.png` ficam em `graficos_ou_imagens/`.

## 5. Priorização de alertas com heap

**Representação:** cada alerta é um dicionário com os dados do registro, guardado em uma tupla `(pontuação, alerta)`.
Entram no heap os registros com `status = alerta` **ou** erro relativo > 25 %.

**Critério de prioridade** (quanto maior, mais urgente):

```
pontuação = 3 × prioridade_base + 5 (se módulo essencial) + 0,5 × erro relativo (%) + 4 (se status = alerta)
```

**Estrutura:** um **max-heap** implementado manualmente (`HeapAlertas`), em que o alerta de maior pontuação fica na raiz.

- Na **inserção**, o item entra no fim e sobe com *heapify-up* enquanto for maior que o pai.
- Na **remoção do mais urgente**, a raiz é retirada, o último item ocupa seu lugar e desce com *heapify-down*.

**Resultado da execução (6 alertas no heap):**

| Ordem | Módulo (ciclo) | Pontuação | Erro rel. |
|:---:|---|:---:|:---:|
| 1º | Armazenamento de Dados (3) | 39,47 | 42,9 % |
| 2º | Habitação Alfa (1) | 35,57 | 39,1 % |
| 3º | Agricultura Hidropônica (3) | 35,00 | 38,0 % |
| 4º | Suporte Médico (1) | 33,02 | 30,0 % |
| 5º | Sensores Externos (3) | 23,62 | 33,2 % |

(O 6º alerta, Sensores Externos no ciclo 1, tem erro relativo de 23,2 %.)

O alerta de **Armazenamento de Dados** lidera por combinar módulo essencial, maior erro relativo e status de alerta.
Já **Suporte Médico** supera módulos não essenciais com prioridade-base maior por ser essencial.

**Vantagem sobre uma lista simples:** inserir e retirar o mais urgente custa **O(log n)**. Com uma lista simples seria preciso
varrer todos os itens (O(n)) ou reordenar a lista a cada novo alerta (O(n log n)). Em uma colônia em que alertas chegam
continuamente, isso é importante.

## 6. Busca de registros com trie

A **trie** (árvore de prefixos) armazena **nomes de módulos, códigos de sensores e tipos de módulo**, normalizados
(minúsculas e sem acentos), de modo que "com" encontra "Comunicação".

| Prefixo | Resultados |
|---|---|
| `com` | Comando Central, Comunicação Principal, comunicação |
| `hab` | Habitação Alfa, Habitação Beta, habitação |
| `0xA0` | Os 30 códigos de sensor (`0xA001` a `0xA093`) |

**Por que a trie é adequada:** a busca percorre só o caminho do prefixo digitado, então o custo depende do
**tamanho do prefixo**, e não da quantidade de registros. Todos os termos que compartilham o início ficam sob o mesmo nó,
tornando a coleta dos resultados direta, ao contrário de percorrer toda uma lista comparando texto. Isso favorece
consultas rápidas e autocompletar em comandos e códigos de sensor.

## 7. Dispositivos, bases numéricas e eletricidade básica

**Dispositivos de E/S:**

- **Entrada:** sensores e medidores simulados de tensão, corrente e latência (neste protótipo, o CSV).
- **Saída:** terminal, relatório técnico e gráficos, que fazem o papel de monitor ou dashboard simulado.
- **Interfaces (conceitual):** rede e Wi-Fi para telemetria, USB para coleta local, Bluetooth para sensores próximos.

**Bases numéricas:** o código do sensor `0xA001` (Comunicação Principal) equivale a **40961** em decimal e a
`1010000000000001` em binário. O código hexadecimal serve como identificador compacto do dispositivo; os endereços
seguem um padrão (`0xA000 + 16 × índice do módulo + ciclo`).

**Eletricidade básica:** para o mesmo sensor, com V = 12 V e I = 2,04 A:

- Potência: **P = V × I = 24,48 W**
- Resistência equivalente (Lei de Ohm): **R = V / I = 5,88 Ω**

A potência entra no modelo como variável explicativa da latência e permite comparar o consumo de transmissão entre módulos.

## 8. Gerenciamento inteligente da comunicação

Esta seção parte dos resultados do SCIC.

- **Sensores e medidores inteligentes:** os campos `tensao_V`, `corrente_A`, `carga_pct` e `latencia_obs_ms` representam o que
  medidores inteligentes enviariam em tempo real, no lugar do CSV.
- **Monitoramento contínuo e detecção de anomalias:** o erro relativo identifica anomalias. Os 6 registros em alerta têm erro médio de
  34,4 % contra 7,4 % dos ativos, o que mostra que o indicador separa bem o comportamento anormal do normal.
- **Automação em situações críticas:** a fila de prioridade indica automaticamente qual alerta atender primeiro (hoje, Armazenamento de Dados),
  reduzindo o tempo de decisão. A ação final continua dependendo de validação humana.
- **Armazenamento e redundância:** o módulo de Armazenamento de Dados lidera a fila de alertas; se ele falha, perde-se o histórico usado
  para detectar anomalias. Enlaces redundantes e cópias dos dados reduziriam esse risco para módulos essenciais.
- **Manutenção preditiva:** módulos com erro relativo médio na faixa de atenção (Sensores Externos, Agricultura, Armazenamento, Habitação Alfa)
  são candidatos a inspeção antes de uma falha. Já os 3 registros em manutenção mostram erro médio de apenas 4,5 %, indicando que a manutenção
  hoje ocorre de forma preventiva.
- **Redes inteligentes e microrredes:** a potência média de 56,98 W por transmissor (até 187,20 W) mostra que comunicação e energia
  estão ligadas. Em uma microrrede, a rede poderia reduzir a potência de transmissores ociosos e reservar energia para os módulos essenciais.

## 9. Reflexão social, cultural e sustentável

- **Sustentabilidade:** prever bem a latência e priorizar os alertas evita retransmissões e uso desnecessário de energia nos transmissores.
  Cada watt economizado em uma colônia isolada preserva recursos limitados.
- **Conhecimentos indígenas e respeito à natureza:** muitas culturas indígenas praticam o uso consciente e cíclico dos recursos, retirando
  da natureza apenas o necessário. Essa ideia inspira operar os módulos com folga de capacidade, sem levá-los ao limite de carga.
- **Diversidade e sistemas não enviesados:** a pontuação dá peso fixo a módulos "essenciais", e essa escolha é humana e pode excluir
  módulos importantes para certos grupos (por exemplo, a agricultura que sustenta a comunidade). Os pesos devem ser revistos com a participação
  de pessoas de diferentes áreas e culturas da colônia.
- **Transparência:** a pontuação é uma fórmula simples e explícita, o que permite explicar por que cada alerta ficou em determinada posição.
- **Responsabilidade humana:** o sistema só **recomenda** a ordem de atendimento; a equipe humana valida as decisões e pode corrigir o resultado.
- **Linguagem e interpretações justas:** as mensagens de alerta são técnicas e neutras, descrevem o fenômeno (por exemplo, "Latência acima do previsto")
  e não responsabilizam pessoas ou grupos.


## 10. Como executar

```bash
pip install numpy pandas matplotlib scikit-learn
python codigo_fonte.py
```

Menu: 1 Consultar registros · 2 Indicadores e erros · 3 Modelo e métricas · 4 Heap de alertas · 5 Trie ·
6 Dispositivos, bases e eletricidade · 7 Análise final · 0 Sair.
