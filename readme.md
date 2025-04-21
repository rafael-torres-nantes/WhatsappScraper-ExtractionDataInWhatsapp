# Whatsapp Scraper - Automação de Extração de Conteúdo no WhatsApp Web

## 👨‍💻 Projeto desenvolvido por: 
[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

* [📚 Contextualização do projeto](#-contextualização-do-projeto)
* [🛠️ Tecnologias/Ferramentas utilizadas](#%EF%B8%8F-tecnologiasferramentas-utilizadas)
* [🖥️ Funcionamento do sistema](#%EF%B8%8F-funcionamento-do-sistema)
   * [🧩 Parte 1 - Extração de Conteúdo](#parte-1---extração-de-conteúdo)
   * [🎨 Parte 2 - Gerenciamento de Arquivos](#parte-2---gerenciamento-de-arquivos)
* [🔀 Arquitetura da aplicação](#arquitetura-da-aplicação)
* [📁 Estrutura do projeto](#estrutura-do-projeto)
* [📌 Como executar o projeto](#como-executar-o-projeto)
* [🕵️ Dificuldades Encontradas](#%EF%B8%8F-dificuldades-encontradas)

## 📚 Contextualização do projeto

Este projeto tem como objetivo automatizar a extração de mensagens, imagens e documentos de conversas no WhatsApp Web utilizando **Selenium**. Ele foi projetado para interagir com a interface do WhatsApp Web, navegar por chats, carregar mensagens antigas e salvar o conteúdo extraído em arquivos organizados.

## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white">](https://www.selenium.dev/)
[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/ChromeDriver-4285F4?logo=googlechrome&logoColor=white">](https://chromedriver.chromium.org/)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white">](https://github.com/)

## 🖥️ Funcionamento do sistema

### 🧩 Parte 1 - Extração de Conteúdo

O sistema utiliza a classe [`WhatsappScraper`](core/base_scraper.py) para gerenciar a navegação no WhatsApp Web e a extração de conteúdo. As principais funcionalidades incluem:

* **Interação com Chats:** A classe [`ChatInteraction`](modules/chat_interaction.py) gerencia a busca por contatos, envio de mensagens e carregamento de mensagens antigas.
* **Extração de Mensagens:** A classe [`ContentExtractor`](modules/content_extractor.py) é responsável por extrair remetentes, timestamps, textos, imagens e documentos das mensagens.
* **Carregamento de Mensagens Antigas:** Métodos como `scroll_to_top` e `find_message` garantem que o histórico completo de mensagens seja carregado.

### 🎨 Parte 2 - Gerenciamento de Arquivos

A classe [`FileManager`](modules/file_manager.py) organiza e salva o conteúdo extraído:

* **Criação de Diretórios:** Diretórios específicos para cada grupo ou contato são criados para armazenar mensagens, imagens e documentos.
* **Download de Arquivos:** URLs de imagens e documentos são baixadas e salvas localmente.
* **Armazenamento de Mensagens:** Mensagens de texto são salvas em arquivos `.txt`.

## 🔀 Arquitetura da aplicação

A aplicação segue uma arquitetura modular, com separação clara entre as responsabilidades:

1. **Core:** Contém a lógica principal de navegação e controle do scraper.
2. **Modules:** Implementa funcionalidades específicas, como interação com chats, extração de conteúdo e gerenciamento de arquivos.
3. **Config:** Armazena configurações globais, como URLs e diretórios de saída.

## 📁 Estrutura do projeto

A estrutura do projeto é organizada da seguinte maneira:

```
.
├── config/
│   ├── settings.py
├── controller/
├── core/
│   ├── base_scraper.py
│   ├── browser_setup.py
├── modules/
│   ├── chat_interaction.py
│   ├── content_extractor.py
│   ├── file_manager.py
├── tmp/
│   ├── whatsapp/
│       ├── Grupo/
│           ├── messages.txt
├── main.py
├── requirements.txt
└── readme.md
```

## 📌 Como executar o projeto

Para executar o projeto localmente, siga as instruções abaixo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafael-torres-nantes/Project-ScrapingWhatsapp.git
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o scraper:**
   ```bash
   python main.py
   ```

4. **Resultados:**
   O conteúdo extraído será salvo na pasta `tmp/whatsapp/`.

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento, algumas dificuldades foram enfrentadas, como:

- **Carregamento de Mensagens Antigas:** Garantir que todas as mensagens fossem carregadas exigiu a implementação de múltiplas estratégias de rolagem e detecção de botões.
- **Manutenção de Sessão no WhatsApp Web:** A configuração do ChromeDriver para evitar detecção de automação foi um desafio.
- **Extração de Conteúdo Dinâmico:** A estrutura do WhatsApp Web muda frequentemente, exigindo ajustes nos seletores XPath.