# Robô Mega Sena

Sistema inteligente para geração de jogos da Mega Sena baseado em análise estatística e aprendizado de máquina.

## Funcionalidades

- Geração de jogos inteligentes com base no histórico de sorteios
- Análise de padrões e tendências
- Cálculo de probabilidades personalizadas
- Interface web amigável

## Tecnologias Utilizadas

- Python 3.8+
- Flask (Backend)
- HTML/CSS/JavaScript (Frontend)
- Scikit-learn (Machine Learning)
- Pandas (Análise de Dados)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pedrohd4280/Robo_Mega_SENA.git
cd Robo_Mega_SENA
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Baixe o modelo treinado:
   - Acesse [este link do Google Drive](https://drive.google.com/drive/folders/seu_link_aqui)
   - Baixe o arquivo `modelo_rf.pkl`
   - Coloque o arquivo na raiz do projeto

## Como Usar

1. Inicie o servidor da API:
```bash
python gerador_mega_sena.py
```

2. Em outro terminal, inicie o servidor web:
```bash
python servidor_web.py
```

3. Acesse a interface web em `http://localhost:8000`

## Análise de Probabilidade

O sistema utiliza diversos fatores para calcular a probabilidade de cada jogo:

- Frequência histórica dos números
- Análise de pares frequentes
- Distribuição por regiões
- Sequências comuns
- Padrões de sorteios anteriores

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 