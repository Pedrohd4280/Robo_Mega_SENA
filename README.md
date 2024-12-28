# Robô Mega Sena

Sistema inteligente para geração de jogos da Mega Sena com análise de probabilidade baseada em histórico de sorteios.

## Funcionalidades

- Geração inteligente de jogos com base em análise estatística
- Cálculo avançado de probabilidades considerando múltiplos fatores
- Interface web amigável
- Análise de padrões históricos
- Suporte para jogos de 6 a 12 dezenas
- Geração de múltiplos cartões simultaneamente
- Timer para medição do tempo de geração

## Tecnologias Utilizadas

- Backend:
  - Python
  - Flask
  - NumPy
  - Pandas
  - Scikit-learn
  - LightGBM

- Frontend:
  - HTML
  - CSS
  - JavaScript

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Robo_Mega_SENA.git
cd Robo_Mega_SENA
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Inicie o servidor da API:
```bash
python gerador_mega_sena.py
```

2. Em outro terminal, inicie o servidor web:
```bash
python servidor_web.py
```

3. Acesse a interface web em:
```
http://127.0.0.1:8000
```

## Estrutura do Projeto

- `gerador_mega_sena.py`: Servidor da API e lógica de geração de jogos
- `servidor_web.py`: Servidor web para servir os arquivos estáticos
- `frontend/`: Diretório com os arquivos da interface web
  - `index.html`: Página principal
  - `styles.css`: Estilos da interface
  - `app.js`: Lógica do frontend

## Análise de Probabilidade

O sistema utiliza diversos fatores para calcular a probabilidade de cada jogo:

- Frequência histórica dos números
- Análise de pares e trios frequentes
- Distribuição por dezenas e quadrantes
- Análise de sequências
- Paridade e números primos
- Soma e média dos números
- Números quentes e frios
- Similaridade com jogos anteriores

## Contribuição

Sinta-se à vontade para contribuir com o projeto. Abra uma issue para discutir mudanças propostas ou envie um pull request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 