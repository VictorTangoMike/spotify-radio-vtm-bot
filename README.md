# 📻 Spotify Morning Radio Bot

Um robô autônomo construído em Python que transforma o Spotify em uma verdadeira rádio matinal personalizada. Executado diariamente via GitHub Actions, o bot compila uma playlist inteligente misturando músicas da biblioteca do usuário, recomendações inéditas e podcasts diários/rotativos, garantindo que a manhã nunca seja repetitiva.

## ✨ Arquitetura e Funcionalidades

O código foi desenhado para ser resiliente às limitações da API do Spotify e garantir a melhor experiência de usuário:

* 🎵 **Algoritmo de "Fila Justa" (Memória Contínua):** O bot rastreia o histórico de reprodução em um arquivo `.json`. Ele garante que **toda** a biblioteca de músicas do usuário seja tocada antes que qualquer faixa se repita. Quando o estoque de faixas inéditas acaba, ele aciona o "Botão de Amnésia" e reinicia o ciclo automaticamente.
* 🛡️ **Chave Composta (Composite Key):** Utiliza um registro no formato `nome_da_musica | nome_do_artista` para diferenciar músicas homônimas (ex: *Animals* do Maroon 5 vs. *Animals* do Pink Floyd), evitando falsos positivos no bloqueio de repetições.
* 💎 **Motor de "Hidden Gems":** Busca as faixas mais populares dos artistas favoritos do usuário e adiciona 20 recomendações diárias que **não** estão na biblioteca de curtidas, expandindo o repertório de forma assertiva (contornando o encerramento da API oficial de recomendações do Spotify).
* 🎙️ **Fila Dinâmica de Podcasts (Fallback):** Intercala blocos musicais com noticiários diários (ex: *Flow News*) e pílulas de reflexão (*Bom dia, Jesus!*). Se um noticiário atrasar a publicação, o sistema reorganiza a fila automaticamente para não deixar "buracos" na playlist.
* 🎰 **Roleta de Podcasts Longos:** Gerencia uma roleta de podcasts densos (ex: *Inteligência LTDA, Nerdcast, SciCast*). Usando paginação profunda e ordenação cronológica reversa, o bot encontra o episódio mais antigo que o usuário **ainda não ouviu** e o encaixa no final da rádio para um "pouso suave".
* ☁️ **Automação Serverless:** Projetado para rodar de madrugada na nuvem através do GitHub Actions, utilizando *Secrets* para proteger as credenciais da API.

## 🚀 Como Configurar e Rodar Localmente

### 1. Pré-requisitos
* Python 3.10 ou superior.
* Uma conta no [Spotify Developer](https://developer.spotify.com/) para criar o seu App e obter o `Client ID` e `Client Secret`.
* Adicionar `http://127.0.0.1:8888/callback` como *Redirect URI* no painel do Spotify.

### 2. Instalação
Clone o repositório e instale as dependências:
```bash
git clone [https://github.com/VictorTangoMike/spotify-radio-vtm-bot.git](https://github.com/VictorTangoMike/spotify-radio-vtm-bot.git)
cd spotify-radio-vtm-bot
pip install spotipy python-dotenv
