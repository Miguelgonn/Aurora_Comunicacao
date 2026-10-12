"""
SCIC - Sistema de Comunicação Interplanetária da Colônia
"""

import os
import unicodedata

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # salva gráficos em arquivo (funciona sem interface gráfica)
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ARQUIVO_DADOS = "dados_aurora_siger.csv"
PASTA_IMG = "graficos_ou_imagens"


# ----------------------------------------------------------------------------
# 1. BASE DE DADOS SIMULADA
# ----------------------------------------------------------------------------
def gerar_base_simulada(caminho=ARQUIVO_DADOS, semente=42):
    """Cria o CSV com dados simulados da Aurora Siger (10 módulos x 3 ciclos)."""
    rng = np.random.default_rng(semente)
    modulos = [
        ("Comunicação Principal", "comunicação", 1),
        ("Comando Central", "comunicação", 1),
        ("Controle de Energia", "armazenamento de dados", 1),
        ("Habitação Alfa", "habitação", 0),
        ("Habitação Beta", "habitação", 0),
        ("Agricultura Hidropônica", "agricultura", 0),
        ("Laboratório Científico", "laboratório", 0),
        ("Suporte Médico", "suporte médico", 1),
        ("Armazenamento de Dados", "armazenamento de dados", 1),
        ("Sensores Externos", "comunicação", 0),
    ]
    linhas = []
    for i, (nome, tipo, essencial) in enumerate(modulos):
        for ciclo in (1, 2, 3):
            tensao = rng.choice([12, 24, 48])
            corrente = round(float(rng.uniform(0.5, 4.0)), 2)
            potencia = round(tensao * corrente, 2)  # P = V * I
            carga = round(float(rng.uniform(20, 95)), 1)
            lat_obs = 40 + 0.9 * carga + 0.05 * potencia + rng.normal(0, 4)
            # latência prevista pelo sistema (estimativa original, com algum desvio)
            lat_prev = lat_obs * rng.uniform(0.85, 1.15)
            # injeta algumas anomalias (latência bem acima do previsto)
            if rng.random() < 0.25:
                lat_obs *= rng.uniform(1.35, 1.8)
            lat_obs, lat_prev = round(float(lat_obs), 2), round(float(lat_prev), 2)
            if lat_obs > lat_prev * 1.25:
                status, msg = "alerta", "Latência acima do previsto"
            elif rng.random() < 0.1:
                status, msg = "manutenção", "Manutenção preventiva agendada"
            else:
                status, msg = "ativo", "Operação normal"
            linhas.append({
                "modulo": nome,
                "tipo": tipo,
                "codigo_sensor": f"0x{0xA000 + i * 16 + ciclo:04X}",
                "ciclo": ciclo,
                "tensao_V": int(tensao),
                "corrente_A": corrente,
                "potencia_W": potencia,
                "carga_pct": carga,
                "latencia_obs_ms": lat_obs,
                "latencia_prev_ms": lat_prev,
                "status": status,
                "essencial": essencial,
                "prioridade_base": int(rng.integers(1, 6)),
                "mensagem": msg,
            })
    pd.DataFrame(linhas).to_csv(caminho, index=False, encoding="utf-8")
    return caminho


def carregar_dados(caminho=ARQUIVO_DADOS):
    """Carrega o CSV (gera a base se ainda não existir) e faz uma limpeza básica."""
    if not os.path.exists(caminho):
        print(f"Arquivo {caminho} não encontrado. Gerando base simulada...")
        gerar_base_simulada(caminho)
    df = pd.read_csv(caminho, encoding="utf-8")
    df = df.dropna().drop_duplicates().reset_index(drop=True)
    return df


# ----------------------------------------------------------------------------
# 2. ERROS NUMÉRICOS E INDICADORES
# ----------------------------------------------------------------------------
def calcular_erros(df):
    """Erro absoluto e relativo entre latência prevista e observada."""
    df = df.copy()
    df["erro_abs_ms"] = (df["latencia_obs_ms"] - df["latencia_prev_ms"]).abs()
    # erro relativo = |obs - prev| / |obs|  (permite comparar escalas diferentes)
    df["erro_rel_pct"] = df["erro_abs_ms"] / df["latencia_obs_ms"].abs() * 100
    return df


def classificar_erro(erro_rel):
    """Critério usado no relatório: <10% aceitável, 10-25% atenção, >25% preocupante."""
    if erro_rel < 10:
        return "aceitável"
    if erro_rel <= 25:
        return "atenção"
    return "preocupante"


def indicadores(df):
    """Indicadores operacionais gerais."""
    return {
        "latência média observada (ms)": df["latencia_obs_ms"].mean(),
        "latência máxima observada (ms)": df["latencia_obs_ms"].max(),
        "desvio padrão da latência (ms)": df["latencia_obs_ms"].std(),
        "potência média (W)": df["potencia_W"].mean(),
        "registros em alerta": int((df["status"] == "alerta").sum()),
        "registros em manutenção": int((df["status"] == "manutenção").sum()),
    }


def demonstrar_ponto_flutuante():
    """Mostra um exemplo de imprecisão de ponto flutuante."""
    a = 0.1 + 0.2
    print(f"0.1 + 0.2 = {a!r}  (esperado 0.3)")
    print(f"0.1 + 0.2 == 0.3 ? {a == 0.3}")
    print(f"np.isclose(0.1 + 0.2, 0.3) ? {np.isclose(a, 0.3)}")
    print("Em comparações de latência usamos tolerância (np.isclose), "
          "não igualdade exata.")


# ----------------------------------------------------------------------------
# 3. MODELO SIMPLES (REGRESSÃO LINEAR) E MÉTRICAS
# ----------------------------------------------------------------------------
def treinar_modelo(df):
    """Prevê a latência observada a partir de carga (%) e potência (W)."""
    X = df[["carga_pct", "potencia_W"]]
    y = df["latencia_obs_ms"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42)
    modelo = LinearRegression().fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    mse = mean_squared_error(y_te, pred)
    metricas = {
        "MAE": mean_absolute_error(y_te, pred),
        "MSE": mse,
        "RMSE": float(np.sqrt(mse)),
        "R²": r2_score(y_te, pred),
    }
    return modelo, metricas, (y_te, pred)


def interpretar_metricas(m):
    print("\nInterpretação:")
    print(f"- MAE  = {m['MAE']:.2f} ms: erro médio típico das previsões.")
    print(f"- RMSE = {m['RMSE']:.2f} ms: penaliza mais os erros grandes.")
    if m["RMSE"] > 1.3 * m["MAE"]:
        print("  RMSE bem maior que MAE -> existem alguns registros com erro grande.")
    else:
        print("  RMSE próximo do MAE -> erros relativamente homogêneos.")
    print(f"- R²   = {m['R²']:.2f}: fração da variação explicada pelo modelo.")
    print("  Atenção: R² alto não garante modelo perfeito; a base é pequena e "
          "simulada, e o teste tem poucos registros.")


def gerar_grafico(df, y_te, pred):
    """Salva gráficos de apoio na pasta graficos_ou_imagens."""
    os.makedirs(PASTA_IMG, exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.scatter(y_te, pred)
    lim = [min(y_te.min(), pred.min()), max(y_te.max(), pred.max())]
    plt.plot(lim, lim, "r--", label="previsão perfeita")
    plt.xlabel("Latência observada (ms)")
    plt.ylabel("Latência prevista pelo modelo (ms)")
    plt.title("Modelo: observado x previsto (teste)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_IMG, "modelo_obs_vs_prev.png"))
    plt.close()

    plt.figure(figsize=(8, 4))
    media = df.groupby("modulo")["erro_rel_pct"].mean().sort_values()
    media.plot(kind="barh")
    plt.xlabel("Erro relativo médio (%)")
    plt.title("Erro relativo médio por módulo")
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_IMG, "erro_relativo_modulos.png"))
    plt.close()
    print(f"Gráficos salvos em ./{PASTA_IMG}/")


# ----------------------------------------------------------------------------
# 4. HEAP (FILA DE PRIORIDADE) - implementado manualmente (max-heap)
# ----------------------------------------------------------------------------
class HeapAlertas:
    """Max-heap: o alerta com maior pontuação fica na raiz (índice 0)."""

    def __init__(self):
        self.dados = []  # lista de tuplas (pontuacao, alerta_dict)

    def __len__(self):
        return len(self.dados)

    def inserir(self, pontuacao, alerta):
        self.dados.append((pontuacao, alerta))
        self._heapify_up(len(self.dados) - 1)  # O(log n)

    def remover_mais_urgente(self):
        if not self.dados:
            return None
        topo = self.dados[0]
        ultimo = self.dados.pop()
        if self.dados:
            self.dados[0] = ultimo
            self._heapify_down(0)  # O(log n)
        return topo

    def _heapify_up(self, i):
        while i > 0:
            pai = (i - 1) // 2
            if self.dados[i][0] > self.dados[pai][0]:
                self.dados[i], self.dados[pai] = self.dados[pai], self.dados[i]
                i = pai
            else:
                break

    def _heapify_down(self, i):
        n = len(self.dados)
        while True:
            esq, dir_, maior = 2 * i + 1, 2 * i + 2, i
            if esq < n and self.dados[esq][0] > self.dados[maior][0]:
                maior = esq
            if dir_ < n and self.dados[dir_][0] > self.dados[maior][0]:
                maior = dir_
            if maior == i:
                break
            self.dados[i], self.dados[maior] = self.dados[maior], self.dados[i]
            i = maior


def pontuacao_alerta(linha):
    """
    Critério de prioridade (quanto maior, mais urgente):
      3 x prioridade_base (1-5) + 5 se módulo essencial
      + 0.5 x erro relativo (%) + 4 se status = alerta
    """
    pts = 3 * linha["prioridade_base"]
    pts += 5 if linha["essencial"] == 1 else 0
    pts += 0.5 * linha["erro_rel_pct"]
    pts += 4 if linha["status"] == "alerta" else 0
    return round(float(pts), 2)


def montar_heap(df):
    """Insere no heap os registros com status 'alerta' ou erro relativo > 25%."""
    heap = HeapAlertas()
    criticos = df[(df["status"] == "alerta") | (df["erro_rel_pct"] > 25)]
    for _, linha in criticos.iterrows():
        heap.inserir(pontuacao_alerta(linha), linha.to_dict())
    return heap


# ----------------------------------------------------------------------------
# 5. TRIE (BUSCA POR PREFIXO)
# ----------------------------------------------------------------------------
def normalizar(texto):
    """Minúsculas e sem acentos: 'Comunicação' -> 'comunicacao'."""
    t = unicodedata.normalize("NFD", str(texto).lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


class NoTrie:
    def __init__(self):
        self.filhos = {}
        self.fim = False
        self.originais = []  # textos originais que terminam neste nó


class Trie:
    def __init__(self):
        self.raiz = NoTrie()

    def inserir(self, palavra):
        no = self.raiz
        for c in normalizar(palavra):
            no = no.filhos.setdefault(c, NoTrie())
        no.fim = True
        if palavra not in no.originais:
            no.originais.append(palavra)

    def buscar_prefixo(self, prefixo):
        """Percorre apenas o caminho do prefixo: custo O(tamanho do prefixo)."""
        no = self.raiz
        for c in normalizar(prefixo):
            if c not in no.filhos:
                return []
            no = no.filhos[c]
        resultados = []
        self._coletar(no, resultados)
        return sorted(resultados)

    def _coletar(self, no, acc):
        if no.fim:
            acc.extend(no.originais)
        for filho in no.filhos.values():
            self._coletar(filho, acc)


def montar_trie(df):
    trie = Trie()
    for nome in df["modulo"].unique():
        trie.inserir(nome)
    for cod in df["codigo_sensor"].unique():
        trie.inserir(cod)
    for tipo in df["tipo"].unique():
        trie.inserir(tipo)
    return trie


# ----------------------------------------------------------------------------
# 6. BASES NUMÉRICAS E ELETRICIDADE BÁSICA
# ----------------------------------------------------------------------------
def converter_bases(codigo_hex):
    """Converte código hexadecimal de sensor para decimal e binário."""
    valor = int(codigo_hex, 16)
    return valor, bin(valor), hex(valor)


def calcular_eletrica(tensao, corrente):
    """P = V x I  e  R = V / I (lei de Ohm)."""
    return tensao * corrente, tensao / corrente


# ----------------------------------------------------------------------------
# 7. FUNÇÕES DE MENU
# ----------------------------------------------------------------------------
def opcao_consultar(df):
    print("\n--- Consulta de registros ---")
    print(f"Total de registros: {len(df)}")
    print(df[["modulo", "codigo_sensor", "ciclo", "latencia_obs_ms",
              "latencia_prev_ms", "status"]].head(15).to_string(index=False))
    print("\n(Exibindo os 15 primeiros registros.)")
    print("Registros por status:")
    print(df["status"].value_counts().to_string())


def opcao_erros(df):
    print("\n--- Indicadores e erros numéricos ---")
    for nome, v in indicadores(df).items():
        print(f"{nome}: {v:.2f}")
    print("\nErros por módulo (média):")
    tab = df.groupby("modulo")[["erro_abs_ms", "erro_rel_pct"]].mean().round(2)
    tab["classificação"] = tab["erro_rel_pct"].apply(classificar_erro)
    print(tab.to_string())
    print("\nPonto flutuante:")
    demonstrar_ponto_flutuante()


def opcao_modelo(df):
    print("\n--- Modelo de previsão (Regressão Linear) ---")
    modelo, m, (y_te, pred) = treinar_modelo(df)
    print("Variáveis: carga_pct e potencia_W -> latencia_obs_ms")
    print(f"Coeficientes: {np.round(modelo.coef_, 3)} | intercepto: {modelo.intercept_:.2f}")
    for k, v in m.items():
        print(f"{k}: {v:.3f}")
    interpretar_metricas(m)
    gerar_grafico(df, y_te, pred)


def opcao_heap(df):
    print("\n--- Priorização de alertas (heap) ---")
    heap = montar_heap(df)
    print(f"{len(heap)} alertas inseridos no heap.\n")
    pos = 1
    while len(heap) > 0 and pos <= 5:
        pts, a = heap.remover_mais_urgente()
        print(f"{pos}º | pontuação {pts:6.2f} | {a['modulo']} (ciclo {a['ciclo']}) | "
              f"erro rel. {a['erro_rel_pct']:.1f}% | {a['mensagem']}")
        pos += 1
    print("\nVantagem: heap retorna o mais urgente em O(log n); "
          "uma lista simples exigiria ordenar/varrer (O(n log n) ou O(n)).")


def opcao_trie(df):
    print("\n--- Busca por prefixo (trie) ---")
    trie = montar_trie(df)
    prefixo = input("Digite um prefixo (ex.: com, hab, 0xA0): ").strip()
    if not prefixo:
        print("Prefixo vazio.")
        return
    res = trie.buscar_prefixo(prefixo)
    if res:
        print(f"{len(res)} resultado(s):")
        for r in res:
            print(" -", r)
    else:
        print("Nenhum resultado encontrado.")


def opcao_dispositivos(df):
    print("\n--- Dispositivos, bases numéricas e eletricidade ---")
    print("Entrada: sensores/medidores simulados (tensão, corrente, latência).")
    print("Saída: terminal, relatório e gráficos (monitor/dashboard simulado).")
    print("Interfaces (conceitual): rede, USB, Wi-Fi, Bluetooth.\n")

    linha = df.iloc[0]
    dec, binario, hexa = converter_bases(linha["codigo_sensor"])
    print(f"Sensor {linha['codigo_sensor']} ({linha['modulo']}):")
    print(f"  decimal = {dec} | binário = {binario} | hexadecimal = {hexa}")

    p, r = calcular_eletrica(linha["tensao_V"], linha["corrente_A"])
    print(f"\nTransmissor: V = {linha['tensao_V']} V, I = {linha['corrente_A']} A")
    print(f"  Potência P = V x I = {p:.2f} W")
    print(f"  Resistência equivalente R = V / I = {r:.2f} ohm (lei de Ohm)")


def opcao_analise_final(df):
    print("\n=== ANÁLISE FINAL DE ALERTAS DE COMUNICAÇÃO ===")
    acima = df[df["latencia_obs_ms"] > df["latencia_prev_ms"] * 1.25]
    print(f"Registros com latência > 125% do previsto: {len(acima)}")
    pior = df.loc[df["erro_rel_pct"].idxmax()]
    print(f"Maior erro relativo: {pior['modulo']} (ciclo {pior['ciclo']}) "
          f"= {pior['erro_rel_pct']:.1f}%")
    heap = montar_heap(df)
    if len(heap) > 0:
        pts, a = heap.remover_mais_urgente()
        print(f"Alerta mais urgente: {a['modulo']} (pontuação {pts})")
    _, m, _ = treinar_modelo(df)
    print(f"Desempenho do modelo -> MAE {m['MAE']:.2f} | RMSE {m['RMSE']:.2f} | R² {m['R²']:.2f}")
    print("\nObservação: decisões automatizadas devem ser validadas pela equipe "
          "humana; os dados são simulados e a base é pequena.")


def menu():
    df = calcular_erros(carregar_dados())
    while True:
        print("\n" + "=" * 52)
        print(" SCIC - Aurora Siger | Comunicação Interplanetária")
        print("=" * 52)
        print("1 - Carregar/consultar registros")
        print("2 - Indicadores e erros (absoluto/relativo)")
        print("3 - Modelo de previsão e métricas")
        print("4 - Priorizar alertas (heap)")
        print("5 - Buscar por prefixo (trie)")
        print("6 - Dispositivos, bases numéricas e eletricidade")
        print("7 - Analisar alertas de comunicação (análise final)")
        print("0 - Sair")
        op = input("Escolha: ").strip()
        if op == "1":
            opcao_consultar(df)
        elif op == "2":
            opcao_erros(df)
        elif op == "3":
            opcao_modelo(df)
        elif op == "4":
            opcao_heap(df)
        elif op == "5":
            opcao_trie(df)
        elif op == "6":
            opcao_dispositivos(df)
        elif op == "7":
            opcao_analise_final(df)
        elif op == "0":
            print("Encerrando o SCIC. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
