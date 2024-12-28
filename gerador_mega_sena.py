import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import random
import logging
import os
import sys
from collections import Counter
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Variáveis globais
df = None
numeros = None
estatisticas = {}

def inicializar_servidor():
    """Inicializa o servidor e carrega os dados necessários."""
    try:
        logger.info("Iniciando servidor...")
        sucesso = inicializar_dados()
        if not sucesso:
            logger.error("Falha ao inicializar dados. Servidor não pode continuar.")
            sys.exit(1)
        return True
    except Exception as e:
        logger.error(f"Erro fatal ao inicializar servidor: {e}")
        sys.exit(1)

def analisar_padroes():
    """Analisa padrões nos números sorteados com análise profunda."""
    global estatisticas
    if numeros is None:
        return
    
    # Análise de frequência com peso histórico
    freq_total = np.zeros(60)
    freq_recente = np.zeros(60)
    for i, jogo in enumerate(numeros):
        peso = 1 + (i / len(numeros))  # Jogos mais recentes têm mais peso
        for num in jogo:
            freq_total[num] += peso
            if i >= len(numeros) - 20:  # Últimos 20 jogos
                freq_recente[num] += 2 * peso
    
    freq_total = freq_total / np.sum(freq_total)
    freq_recente = freq_recente / np.sum(freq_recente)
    
    # Análise de pares com peso histórico
    pares = []
    pares_recentes = []
    for i, jogo in enumerate(numeros):
        peso = 1 + (i / len(numeros))
        for x in range(len(jogo)):
            for y in range(x + 1, len(jogo)):
                par = (min(jogo[x], jogo[y]), max(jogo[x], jogo[y]))
                pares.extend([par] * int(peso * 10))
                if i >= len(numeros) - 20:
                    pares_recentes.extend([par] * int(peso * 20))
    
    pares_freq = Counter(pares)
    pares_recentes_freq = Counter(pares_recentes)
    
    # Análise de trios com peso histórico
    trios = []
    trios_recentes = []
    for i, jogo in enumerate(numeros):
        peso = 1 + (i / len(numeros))
        for x in range(len(jogo)):
            for y in range(x + 1, len(jogo)):
                for z in range(y + 1, len(jogo)):
                    trio = tuple(sorted([jogo[x], jogo[y], jogo[z]]))
                    trios.extend([trio] * int(peso * 10))
                    if i >= len(numeros) - 20:
                        trios_recentes.extend([trio] * int(peso * 20))
    
    trios_freq = Counter(trios)
    trios_recentes_freq = Counter(trios_recentes)
    
    # Análise de padrões de soma
    somas = []
    somas_recentes = []
    for i, jogo in enumerate(numeros):
        soma = sum(jogo)
        somas.append(soma)
        if i >= len(numeros) - 20:
            somas_recentes.append(soma)
    
    media_soma = np.mean(somas)
    desvio_soma = np.std(somas)
    media_soma_recente = np.mean(somas_recentes)
    desvio_soma_recente = np.std(somas_recentes)
    
    # Análise de sequências
    sequencias = []
    for jogo in numeros:
        jogo_sorted = sorted(jogo)
        for i in range(len(jogo_sorted) - 1):
            if jogo_sorted[i + 1] - jogo_sorted[i] == 1:
                sequencias.append((jogo_sorted[i], jogo_sorted[i + 1]))
    
    seq_freq = Counter(sequencias)
    
    # Análise de distribuição por dezenas
    dezenas = [[] for _ in range(6)]
    for jogo in numeros:
        for num in jogo:
            dezena = num // 10
            if dezena < 6:
                dezenas[dezena].append(num)
    
    dist_dezenas = [len(dez) / (len(numeros) * 6) for dez in dezenas]
    
    # Análise de números quentes e frios
    ultimos_jogos = numeros[-30:]  # Aumentar para 30 jogos
    nums_quentes = set()
    nums_frios = set(range(60))
    
    for jogo in ultimos_jogos:
        nums_quentes.update(jogo)
        nums_frios.difference_update(jogo)
    
    # Análise de paridade e números primos
    paridade = {'par': 0, 'impar': 0}
    primos = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
    contagem_primos = 0
    
    for jogo in numeros:
        pares = sum(1 for num in jogo if num % 2 == 0)
        impares = len(jogo) - pares
        paridade['par'] += pares
        paridade['impar'] += impares
        contagem_primos += sum(1 for num in jogo if (num + 1) in primos)
    
    total_numeros = paridade['par'] + paridade['impar']
    dist_paridade = {
        'par': paridade['par'] / total_numeros,
        'impar': paridade['impar'] / total_numeros
    }
    
    prob_primo = contagem_primos / (len(numeros) * 6)
    
    # Análise de quadrantes
    quadrantes = [0] * 4
    for jogo in numeros:
        for num in jogo:
            quad = (num // 15) % 4
            quadrantes[quad] += 1
    
    dist_quadrantes = [q / sum(quadrantes) for q in quadrantes]
    
    estatisticas = {
        'frequencia_total': freq_total,
        'frequencia_recente': freq_recente,
        'pares_frequentes': pares_freq,
        'pares_recentes': pares_recentes_freq,
        'trios_frequentes': trios_freq,
        'trios_recentes': trios_recentes_freq,
        'sequencias_frequentes': seq_freq,
        'distribuicao_dezenas': dist_dezenas,
        'numeros_quentes': nums_quentes,
        'numeros_frios': nums_frios,
        'distribuicao_paridade': dist_paridade,
        'probabilidade_primo': prob_primo,
        'distribuicao_quadrantes': dist_quadrantes,
        'media_soma': media_soma,
        'desvio_soma': desvio_soma,
        'media_soma_recente': media_soma_recente,
        'desvio_soma_recente': desvio_soma_recente,
        'total_jogos': len(numeros)
    }
    
    logger.info("Análise de padrões concluída")

def calcular_probabilidade_avancada(numeros_escolhidos):
    """Calcula probabilidade usando análise profunda de padrões."""
    if numeros is None or not estatisticas:
        return 50.0
    
    # 1. Probabilidade baseada em frequência (20%)
    prob_freq = np.mean([
        estatisticas['frequencia_total'][num-1] * 100 * 1.5 +
        estatisticas['frequencia_recente'][num-1] * 100 * 2.5
        for num in numeros_escolhidos
    ])
    
    # 2. Probabilidade baseada em combinações (25%)
    pares_escolhidos = []
    trios_escolhidos = []
    for i in range(len(numeros_escolhidos)):
        for j in range(i + 1, len(numeros_escolhidos)):
            par = (min(numeros_escolhidos[i]-1, numeros_escolhidos[j]-1),
                  max(numeros_escolhidos[i]-1, numeros_escolhidos[j]-1))
            pares_escolhidos.append(par)
            for k in range(j + 1, len(numeros_escolhidos)):
                trio = tuple(sorted([
                    numeros_escolhidos[i]-1,
                    numeros_escolhidos[j]-1,
                    numeros_escolhidos[k]-1
                ]))
                trios_escolhidos.append(trio)
    
    # Calcular probabilidade de pares
    max_freq_pares = max(estatisticas['pares_frequentes'].values())
    max_freq_pares_rec = max(estatisticas['pares_recentes'].values())
    
    prob_pares = 0
    for par in pares_escolhidos:
        freq_normal = estatisticas['pares_frequentes'].get(par, 0) / max_freq_pares
        freq_recente = estatisticas['pares_recentes'].get(par, 0) / max_freq_pares_rec
        prob_pares += (freq_normal * 100 * 0.4 + freq_recente * 100 * 0.6)
    prob_pares = prob_pares / len(pares_escolhidos) if pares_escolhidos else 0
    
    # Calcular probabilidade de trios
    max_freq_trios = max(estatisticas['trios_frequentes'].values())
    max_freq_trios_rec = max(estatisticas['trios_recentes'].values())
    
    prob_trios = 0
    for trio in trios_escolhidos:
        freq_normal = estatisticas['trios_frequentes'].get(trio, 0) / max_freq_trios
        freq_recente = estatisticas['trios_recentes'].get(trio, 0) / max_freq_trios_rec
        prob_trios += (freq_normal * 100 * 0.4 + freq_recente * 100 * 0.6)
    prob_trios = prob_trios / len(trios_escolhidos) if trios_escolhidos else 0
    
    prob_combinacoes = (prob_pares * 0.6 + prob_trios * 0.4) * 1.5
    
    # 3. Análise de distribuição (15%)
    dezenas = [0] * 6
    quadrantes = [0] * 4
    for num in numeros_escolhidos:
        dez = (num - 1) // 10
        quad = ((num - 1) // 15) % 4
        if dez < 6:
            dezenas[dez] += 1
        quadrantes[quad] += 1
    
    # Calcular desvio da distribuição ideal
    dist_ideal_dez = len(numeros_escolhidos) / 6
    desvio_dezenas = sum(abs(d - dist_ideal_dez) for d in dezenas)
    prob_dist_dez = 100 * (1 - desvio_dezenas / (len(numeros_escolhidos) * 2))
    
    dist_ideal_quad = len(numeros_escolhidos) / 4
    desvio_quad = sum(abs(q - dist_ideal_quad) for q in quadrantes)
    prob_dist_quad = 100 * (1 - desvio_quad / (len(numeros_escolhidos) * 2))
    
    prob_distribuicao = (prob_dist_dez + prob_dist_quad) / 2
    
    # 4. Análise de soma e média (15%)
    soma = sum(numeros_escolhidos)
    desvio_soma = abs(soma - estatisticas['media_soma_recente'])
    prob_soma = 100 * (1 - min(desvio_soma / (estatisticas['desvio_soma_recente'] * 3), 1))
    
    # 5. Análise de paridade e primos (15%)
    pares = sum(1 for num in numeros_escolhidos if num % 2 == 0)
    razao_par = pares / len(numeros_escolhidos)
    razao_ideal = estatisticas['distribuicao_paridade']['par']
    prob_paridade = 100 * (1 - abs(razao_par - razao_ideal))
    
    primos = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
    qtd_primos = sum(1 for num in numeros_escolhidos if num in primos)
    razao_primo = qtd_primos / len(numeros_escolhidos)
    prob_primo = 100 * (1 - abs(razao_primo - estatisticas['probabilidade_primo']))
    
    prob_composicao = (prob_paridade + prob_primo) / 2
    
    # 6. Análise de sequências (10%)
    sequencias = 0
    nums_sorted = sorted(numeros_escolhidos)
    for i in range(len(nums_sorted) - 1):
        if nums_sorted[i + 1] - nums_sorted[i] == 1:
            sequencias += 1
    prob_seq = max(0, 100 - (sequencias * 20))
    
    # Combinação final ponderada
    probabilidade = (
        0.20 * prob_freq +           # Frequência individual (20%)
        0.25 * prob_combinacoes +    # Combinações de números (25%)
        0.15 * prob_distribuicao +   # Distribuição espacial (15%)
        0.15 * prob_soma +           # Soma e média (15%)
        0.15 * prob_composicao +     # Paridade e primos (15%)
        0.10 * prob_seq              # Sequências (10%)
    )
    
    # Ajustes finais
    if len(set(numeros_escolhidos)) != len(numeros_escolhidos):
        probabilidade *= 0.5  # Penaliza números repetidos
    
    # Boost para números quentes
    nums_quentes = sum(1 for num in numeros_escolhidos if num-1 in estatisticas['numeros_quentes'])
    nums_frios = sum(1 for num in numeros_escolhidos if num-1 in estatisticas['numeros_frios'])
    
    boost_quentes = (nums_quentes / len(numeros_escolhidos)) * 30
    penalizacao_frios = (nums_frios / len(numeros_escolhidos)) * 15
    
    probabilidade = min(100, probabilidade + boost_quentes - penalizacao_frios)
    
    # Ajuste final baseado em ocorrências históricas similares
    jogos_similares = 0
    for jogo in numeros:
        nums_comuns = len(set(jogo).intersection(set(numeros_escolhidos)))
        if nums_comuns >= len(numeros_escolhidos) * 0.7:  # 70% de similaridade
            jogos_similares += 1
    
    boost_historico = (jogos_similares / len(numeros)) * 60
    probabilidade = min(100, probabilidade + boost_historico)
    
    return max(1, min(100, probabilidade))

def inicializar_dados():
    global df, numeros
    try:
        arquivo_dados = 'Todos os Resultados da Mega Sena na ordem do sorteio  Rede Loteria.csv'
        if not os.path.exists(arquivo_dados):
            logger.error(f"Arquivo de dados não encontrado: {arquivo_dados}")
            return False
            
        df = pd.read_csv(arquivo_dados, encoding='latin1')
        df = df.dropna()
        numeros = df.iloc[:, 2:8].values.astype(int)
        numeros = numeros - 1  # Mapear para 0-59
        
        # Analisar padrões após carregar os dados
        analisar_padroes()
        
        logger.info(f"Dados carregados com sucesso. Total de jogos: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return False

def gerar_numeros_inteligentes(qtd_dezenas):
    """Gera números com base em análise estatística avançada."""
    if not estatisticas:
        return gerar_numeros_aleatorios(qtd_dezenas)
    
    numeros_escolhidos = []
    freq = estatisticas['frequencia_total']
    
    # Primeira fase: escolher números quentes (30% das dezenas)
    qtd_quentes = max(1, int(qtd_dezenas * 0.3))
    nums_quentes = list(estatisticas['numeros_quentes'])
    while len(numeros_escolhidos) < qtd_quentes and nums_quentes:
        num = random.choice(nums_quentes) + 1
        if num not in numeros_escolhidos:
            numeros_escolhidos.append(num)
            nums_quentes.remove(num - 1)
    
    # Segunda fase: escolher números com alta frequência (40% das dezenas)
    while len(numeros_escolhidos) < int(qtd_dezenas * 0.7):
        pesos = [freq[n-1] * 3 for n in range(1, 61) if n not in numeros_escolhidos]
        nums_disponiveis = [n for n in range(1, 61) if n not in numeros_escolhidos]
        soma_pesos = sum(pesos)
        if soma_pesos > 0:
            pesos = [p/soma_pesos for p in pesos]
            num = np.random.choice(nums_disponiveis, p=pesos)
        else:
            num = random.choice(nums_disponiveis)
        numeros_escolhidos.append(num)
    
    # Terceira fase: completar com números baseados em pares e trios frequentes
    while len(numeros_escolhidos) < qtd_dezenas:
        pesos = []
        nums_disponiveis = []
        for n in range(1, 61):
            if n not in numeros_escolhidos:
                peso = 1.0
                # Peso baseado em pares frequentes
                for num_escolhido in numeros_escolhidos:
                    par = (min(n-1, num_escolhido-1), max(n-1, num_escolhido-1))
                    peso += estatisticas['pares_frequentes'].get(par, 0) * 2
                
                # Peso baseado em trios frequentes
                for i in range(len(numeros_escolhidos)):
                    for j in range(i + 1, len(numeros_escolhidos)):
                        trio = (min(n-1, numeros_escolhidos[i]-1, numeros_escolhidos[j]-1),
                               sorted([n-1, numeros_escolhidos[i]-1, numeros_escolhidos[j]-1])[1],
                               max(n-1, numeros_escolhidos[i]-1, numeros_escolhidos[j]-1))
                        peso += estatisticas['trios_frequentes'].get(trio, 0) * 3
                
                pesos.append(peso)
                nums_disponiveis.append(n)
        
        soma_pesos = sum(pesos)
        if soma_pesos > 0 and nums_disponiveis:
            pesos = [p/soma_pesos for p in pesos]
            num = np.random.choice(nums_disponiveis, p=pesos)
        else:
            num = random.choice([n for n in range(1, 61) if n not in numeros_escolhidos])
        numeros_escolhidos.append(num)
    
    return sorted(numeros_escolhidos)

def gerar_numeros_aleatorios(qtd_dezenas):
    """Gera números aleatórios quando necessário."""
    return sorted(random.sample(range(1, 61), qtd_dezenas))

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar o status do servidor."""
    status_data = {
        'status': 'online',
        'dados_carregados': df is not None,
        'total_jogos_historico': len(df) if df is not None else 0,
        'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    logger.info(f"Status do servidor: {status_data}")
    return jsonify(status_data)

@app.route('/gerar-jogos', methods=['POST'])
def gerar_jogos():
    try:
        inicio = datetime.now()
        data = request.get_json()
        logger.info(f"Requisição recebida: {data}")
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        qtd_dezenas = data.get('dezenas', 6)
        qtd_cartoes = data.get('cartoes', 1)
        
        if not (6 <= qtd_dezenas <= 12):
            return jsonify({'error': 'Quantidade de dezenas deve ser entre 6 e 12'}), 400
        
        if not (1 <= qtd_cartoes <= 10):
            return jsonify({'error': 'Quantidade de cartões deve ser entre 1 e 10'}), 400
        
        jogos = []
        for i in range(qtd_cartoes):
            # Gerar números usando método inteligente
            numeros_gerados = gerar_numeros_inteligentes(qtd_dezenas)
            
            # Converter números numpy para Python int
            numeros_gerados = [int(num) for num in numeros_gerados]
            
            # Calcular probabilidade usando método avançado
            probabilidade = float(calcular_probabilidade_avancada(numeros_gerados))
            
            # Ajustar probabilidade baseado na quantidade de dezenas
            # Quanto mais dezenas, maior a chance de acerto
            fator_ajuste = 1 + ((qtd_dezenas - 6) * 0.15)  # Aumento de 15% por dezena adicional
            probabilidade *= fator_ajuste
            
            # Garantir que a probabilidade não ultrapasse 100%
            probabilidade = min(100, probabilidade)
            
            jogo = {
                'numeros': numeros_gerados,
                'probabilidade': round(float(probabilidade), 1)
            }
            jogos.append(jogo)
            logger.info(f"Jogo {i+1} gerado: {jogo}")
        
        fim = datetime.now()
        tempo_execucao = (fim - inicio).total_seconds()
        
        resposta = {
            'jogos': jogos,
            'tempo_execucao': round(float(tempo_execucao), 2),
            'timestamp': fim.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"Jogos gerados em {tempo_execucao:.2f} segundos")
        return jsonify(resposta)
    
    except Exception as e:
        logger.error(f"Erro ao gerar jogos: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    try:
        # Inicializar servidor
        if not inicializar_servidor():
            sys.exit(1)
        
        # Definir porta
        porta = 5001
        
        # Tentar iniciar o servidor
        logger.info(f"Iniciando servidor na porta {porta}...")
        app.run(debug=False, port=porta, host='127.0.0.1')
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)
