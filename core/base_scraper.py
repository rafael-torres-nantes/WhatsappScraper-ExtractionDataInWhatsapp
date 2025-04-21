from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from config.settings import BASE_URL, TIME_WAIT, OUTPUT_DIR
from core.browser_setup import BrowserSetup

from modules.file_manager import FileManager
from modules.chat_interaction import ChatInteraction
from modules.content_extractor import ContentExtractor

class WhatsappScraper:
    """
    Classe para automação do WhatsApp Web.
    Gerencia a navegação e as interações com o WhatsApp Web.
    """
        
    def __init__(self):
        """
        Inicializa o scraper com as configurações necessárias do webdriver.
        """
        self.base_url = BASE_URL
        self.options = BrowserSetup.setup_chrome_options()
        self.driver = BrowserSetup.get_chrome_driver(self.options)
        self.main_window = None
        self.output_dir = OUTPUT_DIR

        # Inicializa o gerenciador de navegador
        self.open_whatsapp()
        
        # Inicializa módulos após abrir o WhatsApp
        self.main_window = self.main_window
        self.chat_interaction = ChatInteraction(self.driver)
        self.content_extractor = ContentExtractor(self.driver)
        self.file_manager = FileManager(self.driver, self.output_dir, self.main_window)
            

    def open_whatsapp(self):
        """
        Abre o WhatsApp Web na URL base e verifica o status de login.
        """
        self.driver.get(self.base_url)
        self.main_window = self.driver.current_window_handle
        self.driver.maximize_window()
        
        print("[DEBUG] Abrindo o site do WhatsApp Web")
        
        try:
            # Aguarda até 120 segundos pelo carregamento inicial
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verifica se precisa escanear o QR code
            self.check_login_status()
            
        except TimeoutException:
            print("[TIMEOUT] Timeout ao carregar a página do WhatsApp Web.")
            
    def check_login_status(self):
        """
        Verifica se o usuário está logado ou se precisa escanear o QR code.
        """
        try:
            # Primeiro verifica se já está na tela principal (já logado)
            chat_list = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Lista de conversas" and @role="grid"]'))
            )
            print("[DEBUG] Já está logado no WhatsApp Web!")
            return True
            
        except TimeoutException:
            # Se não encontrou a lista de chats, verifica se o QR code está presente
            try:
                qr_code = WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan this QR code to link a device!" and @role="img"]'))
                )
                
                print("[DEBUG] Por favor, escaneie o QR code com seu celular para fazer login no WhatsApp Web.")
                print("[DEBUG] Aguardando autenticação...")
                
                # Aguarda até que o QR code desapareça (indicando login bem-sucedido)
                WebDriverWait(self.driver, 120).until_not(
                    EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan this QR code to link a device!" and @role="img"]'))
                )
                
                print("[DEBUG] Login realizado com sucesso!")
                self.wait_for_chats_to_load()
                return True
                
            except TimeoutException:
                print("[ERROR] Não foi possível detectar o estado do login. Verifique manualmente.")
                return False
    
    def wait_for_chats_to_load(self):
        """
        Aguarda até que a lista de conversas seja carregada.
        """
        try:
            # Espera pelo painel de conversas
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Lista de conversas" and @role="grid"]'))
            )
            print("[DEBUG] WhatsApp Web carregado com sucesso!")
            
        except TimeoutException:
            print("[ERROR] Não foi possível carregar a lista de conversas. Verifique sua conexão.")
    
    def extract_group_content(self, group_name):
        """
        Extrai todas as mensagens, imagens e documentos de um grupo ou contato.
        
        Args:
            group_name (str): Nome do grupo ou contato
            
        Returns:
            bool: True se a extração foi bem-sucedida, False caso contrário
        """
        try:
            print(f"[DEBUG] Iniciando extração de conteúdo do grupo: {group_name}")
            
            # Encontra o grupo ou contato
            if not self.chat_interaction.find_chat(group_name):
                print(f"[ERROR] Não foi possível encontrar o grupo: {group_name}")
                return False
                
            # Cria diretórios para o grupo
            group_dir, images_dir, docs_dir, messages_file = self.file_manager.create_group_directories(group_name)
            print(f"[DEBUG] Diretórios criados: {group_dir}")
            
            # Rola para cima para carregar mensagens mais antigas
            self.chat_interaction.load_all_messages()
            
            # Extrai as mensagens
            messages = []
            images_count = 0
            docs_count = 0
            
            # Obtém todos os elementos de mensagem
            message_elements = self.content_extractor.get_all_messages()
            print(f"[DEBUG] Encontradas {len(message_elements)} mensagens para processar")
            sleep(200)
            
            # Processa cada mensagem
            for msg_element in message_elements:
                try:
                    # Extrai informações da mensagem
                    sender = self.content_extractor.extract_sender(msg_element)
                    timestamp = self.content_extractor.extract_timestamp(msg_element)
                    text = self.content_extractor.extract_text(msg_element)
                    
                    # Salva a mensagem
                    if sender and timestamp and text:
                        message_data = f"[{timestamp}] {sender}: {text}"
                        messages.append(message_data)
                    
                    # Verifica se há imagens
                    images = self.content_extractor.extract_images(msg_element)
                    if images:
                        for img_url in images:
                            try:
                                img_filename = f"image_{images_count}_{timestamp.replace(':', '-').replace(' ', '_').replace('/', '-')}.jpg"
                                img_path = os.path.join(images_dir, img_filename)
                                self.file_manager.download_file(img_url, img_path)
                                images_count += 1
                            except Exception as e:
                                print(f"[ERROR] Falha ao baixar imagem: {str(e)}")
                    
                    # Verifica se há documentos
                    docs = self.content_extractor.extract_documents(msg_element)
                    if docs:
                        for doc_url, doc_name in docs:
                            try:
                                if not doc_name:
                                    doc_name = f"doc_{docs_count}_{timestamp.replace(':', '-').replace(' ', '_').replace('/', '-')}"
                                doc_path = os.path.join(docs_dir, doc_name)
                                self.file_manager.download_file(doc_url, doc_path)
                                docs_count += 1
                            except Exception as e:
                                print(f"[ERROR] Falha ao baixar documento: {str(e)}")
                                
                except StaleElementReferenceException:
                    print("[WARN] Elemento ficou obsoleto durante o processamento, ignorando...")
                    continue
                except Exception as e:
                    print(f"[ERROR] Erro ao processar mensagem: {str(e)}")
                    continue
            
            # Salva todas as mensagens no arquivo
            self.file_manager.save_messages_to_file(messages, messages_file)
            
            print(f"[DEBUG] Extração concluída para o grupo {group_name}:")
            print(f"[DEBUG] - Mensagens: {len(messages)}")
            print(f"[DEBUG] - Imagens: {images_count}")
            print(f"[DEBUG] - Documentos: {docs_count}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Erro durante a extração do grupo {group_name}: {str(e)}")
            return False
    
    def extract_from_multiple_groups(self, group_list):
        """
        Extrai conteúdo de múltiplos grupos.
        
        Args:
            group_list (list): Lista de nomes de grupos
            
        Returns:
            dict: Dicionário com os resultados para cada grupo
        """
        results = {}
        
        for group_name in group_list:
            print(f"[INFO] Iniciando extração do grupo: {group_name}")
            success = self.extract_group_content(group_name)
            results[group_name] = success
            
        return results
    
    def send_message_to_contact(self, contact_name, message):
        """
        Envia uma mensagem para um contato específico.
        
        Args:
            contact_name (str): Nome do contato
            message (str): Mensagem a ser enviada
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso
        """
        if self.chat_interaction.find_chat(contact_name):
            return self.chat_interaction.send_message(message)
        return False
    
    def close(self):
        """
        Fecha o navegador e encerra a sessão.
        """
        if self.driver:
            self.driver.quit()
            print("[DEBUG] Navegador fechado com sucesso.")
        else:
            print("[DEBUG] Navegador já fechado ou não inicializado.")
