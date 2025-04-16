# core/browser.py
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class BrowserSetup:
    @staticmethod
    def setup_chrome_options():
        """
        Configura as opções do Chrome para otimizar a automação.
        
        Returns:
            ChromeOptions: Objeto contendo todas as configurações do navegador.
        """
        options = webdriver.ChromeOptions()

        # Configurações para evitar detecção de automação
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument('--disable-features=VizDisplayCompositor')

        # Define um perfil customizado para o WhatsApp Bot
        # Isso cria um perfil separado que será usado apenas pelo bot
        user_data_dir = os.path.join(os.path.expanduser("~"), "whatsapp_bot_profile")
        
        # Cria o diretório se não existir
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--start-maximized")

        # Mantém o navegador aberto após a execução
        options.add_experimental_option("detach", True)
        
        return options
        
    @staticmethod
    def get_chrome_driver(options):
        """
        Retorna uma instância do Chrome WebDriver com as opções especificadas.
        
        Args:
            options: Opções de configuração do Chrome
            
        Returns:
            WebDriver: Instância do Chrome WebDriver
        """
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)