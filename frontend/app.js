document.addEventListener('DOMContentLoaded', () => {
    const btnGerar = document.getElementById('gerarJogos');
    const resultadosDiv = document.getElementById('resultados');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const API_URL = 'http://127.0.0.1:5001';

    // Criar elemento do timer
    const timerDiv = document.createElement('div');
    timerDiv.className = 'timer';
    document.body.appendChild(timerDiv);

    let timerInterval;
    let startTime;

    function atualizarTimer() {
        const tempoDecorrido = (Date.now() - startTime) / 1000;
        timerDiv.textContent = `Tempo: ${tempoDecorrido.toFixed(1)}s`;
    }

    function iniciarTimer() {
        startTime = Date.now();
        timerDiv.classList.add('active');
        timerInterval = setInterval(atualizarTimer, 100);
        atualizarTimer();
    }

    function pararTimer() {
        clearInterval(timerInterval);
        timerDiv.classList.remove('active');
    }

    // Verificar status do servidor ao carregar
    verificarStatusServidor();

    btnGerar.addEventListener('click', gerarJogos);

    async function verificarStatusServidor() {
        try {
            const response = await fetch(`${API_URL}/status`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Servidor não está respondendo corretamente');
            }
            
            const status = await response.json();
            console.log('Status do servidor:', status);
            
            if (!status.dados_carregados) {
                mostrarErro('Aviso: Base de dados não carregada. O sistema funcionará com números aleatórios.');
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            mostrarErro('Erro: Não foi possível conectar ao servidor. Verifique se o servidor está rodando.');
            btnGerar.disabled = true;
        }
    }

    function mostrarErro(mensagem, isTemporary = true) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = mensagem;
        
        if (document.querySelector('.error-message')) {
            document.querySelector('.error-message').remove();
        }
        
        resultadosDiv.insertAdjacentElement('beforebegin', errorDiv);
        
        if (isTemporary) {
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    }

    async function gerarJogos() {
        const dezenas = parseInt(document.getElementById('dezenas').value);
        const cartoes = parseInt(document.getElementById('cartoes').value);

        // Validações
        if (dezenas < 6 || dezenas > 12) {
            mostrarErro('Quantidade de dezenas deve ser entre 6 e 12');
            return;
        }

        if (cartoes < 1 || cartoes > 10) {
            mostrarErro('Quantidade de cartões deve ser entre 1 e 10');
            return;
        }

        try {
            // Mostrar loading e iniciar timer
            loadingSpinner.style.display = 'block';
            resultadosDiv.innerHTML = '';
            btnGerar.disabled = true;
            iniciarTimer();

            console.log('Enviando requisição para:', `${API_URL}/gerar-jogos`);
            console.log('Dados:', { dezenas, cartoes });

            const response = await fetch(`${API_URL}/gerar-jogos`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ dezenas, cartoes })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Erro ao gerar jogos');
            }

            const data = await response.json();
            console.log('Resposta recebida:', data);
            
            exibirJogos(data.jogos, data.tempo_execucao);
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro(`Erro ao gerar jogos: ${error.message}`, false);
        } finally {
            loadingSpinner.style.display = 'none';
            btnGerar.disabled = false;
            pararTimer();
        }
    }

    function exibirJogos(jogos, tempoServidor) {
        resultadosDiv.innerHTML = '';

        // Adicionar informações de tempo
        const tempoInfo = document.createElement('div');
        tempoInfo.className = 'tempo-info';
        tempoInfo.innerHTML = `
            <div class="tempo-header">
                <h3>Informações de Tempo</h3>
                <div class="tempo-detalhes">
                    <p>Tempo de processamento no servidor: ${tempoServidor} segundos</p>
                    <p>Tempo total (incluindo rede): ${((Date.now() - startTime) / 1000).toFixed(2)} segundos</p>
                </div>
            </div>
        `;
        resultadosDiv.appendChild(tempoInfo);

        // Container para os cartões
        const cartoesContainer = document.createElement('div');
        cartoesContainer.className = 'cartoes-container';

        jogos.forEach((jogo, index) => {
            const cartao = document.createElement('div');
            cartao.className = 'cartao';
            
            cartao.innerHTML = `
                <div class="cartao-header">
                    <span class="cartao-titulo">Jogo ${index + 1}</span>
                    <span class="probabilidade">${jogo.probabilidade}% chance</span>
                </div>
                <div class="numeros">
                    ${jogo.numeros.map(num => `
                        <span class="numero">${String(num).padStart(2, '0')}</span>
                    `).join('')}
                </div>
            `;

            cartoesContainer.appendChild(cartao);
        });

        resultadosDiv.appendChild(cartoesContainer);

        // Animação de entrada
        const cartoes = document.querySelectorAll('.cartao');
        cartoes.forEach((cartao, index) => {
            cartao.style.opacity = '0';
            cartao.style.transform = 'translateY(20px)';
            setTimeout(() => {
                cartao.style.transition = 'all 0.5s ease';
                cartao.style.opacity = '1';
                cartao.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
});
