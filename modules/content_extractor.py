# modules/content_extractor.py
import datetime
from typing import List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from utils.timestamp_regex import get_timestamp_regex

class ContentExtractor:
    """
    Classe responsável por extrair conteúdo das mensagens do WhatsApp.
    Fornece métodos para obter mensagens, remetentes, timestamps e conteúdo de mídia.
    """
    def __init__(self, driver: webdriver.Chrome):
        """
        Inicializa o extrator de conteúdo.
        
        Args:
            driver: Instância do WebDriver Selenium para interação com a página
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def get_messages_by_date(self):
        """
        Obtém mensagens de uma conversa específica.

        Args:
            date (str): Data da conversa no formato "dd/mm/yyyy"
        """
        try:
            # Obtém as datas das mensagens
            list_messages_date = self.driver.find_elements(By.XPATH, '//div[@class="_amjw _amk1 _aotl  focusable-list-item"]')
            
            # Percorre as mensagens e verifica se há pelo menos duas mensagens
            for index in range(len(list_messages_date)):

                # Verifica se há pelo menos dois elementos na lista
                if 2 <= len(list_messages_date) and index < len(list_messages_date) - 1:

                    # Obtém o HTML entre o primeiro e o segundo elemento
                    first_element = list_messages_date[index]
                    second_element = list_messages_date[index + 1]
                    
                    # Usa JavaScript para obter o HTML entre os dois elementos
                    html_between = self.driver.execute_script(
                        """
                        let range = document.createRange();
                        range.setStart(arguments[0], 0);
                        range.setEnd(arguments[1], arguments[1].childNodes.length);
                        return range.cloneContents().textContent;
                        """,
                        first_element, second_element
                    )
                    
                    print(html_between.strip())

            return html_between.strip()

        except:
            print("[ERROR] Erro ao obter mensagens por data.")
            return []
        
    def get_all_messages(self) -> List[str]:
        """
        Obtém todos os textos de mensagens visíveis na conversa atual.
        
        Returns:
            Lista contendo o texto de todas as mensagens encontradas
        """
        try:
            # Aguarda o carregamento das mensagens
            chat_messages = self._get_incoming_messages()
            
            # Combina todas as mensagens
            return chat_messages
        
        except Exception as e:
            print(f"[ERROR] Erro ao obter mensagens: {str(e)}")
            return []
    
    def _get_incoming_messages(self) -> List[str]:
        """
        Obtém mensagens recebidas.
        
        Returns:
            Lista contendo o texto das mensagens recebidas
        """
        # Lista para armazenar mensagens recebidas
        messages_text = []

        try:
            # Localiza contêineres de mensagens recebidas
            list_message_container = self.driver.find_elements(By.XPATH, '//div[@class="copyable-text"]')                  
            
            for message_container in list_message_container:
                
                # Obtém o usuário remetente da mensagem 
                user, timestamp = get_timestamp_regex(message_container.get_attribute('data-pre-plain-text'))

                # Busca spans que contêm o texto das mensagens
                list_message = message_container.find_elements(By.XPATH, './/span[@class=""]')
                
                # Extrai o texto de cada mensagem
                for message in list_message:
                    text = message.text.strip()
                    
                    # Verifica se o texto não está vazio e se não é uma mensagem de sistema
                    if text:
                        messages_text.append({'user': user, 'timestamp': timestamp, 'text': text})
                        print(f"[DEBUG] Mensagem recebida: {text}")
            
            return messages_text
        
        # Tratamento de exceções para evitar falhas em mensagens não visíveis ou removidas
        except Exception as e:
            print(f"[ERROR] Erro ao obter mensagens recebidas: {str(e)}")
            return []
        
    def get_message_details(self):
        """
        Obtém detalhes completos de todas as mensagens visíveis.
        
        Returns:
            Lista de dicionários contendo detalhes das mensagens (remetente, timestamp, texto, mídia)
        """
        messages = []
        try:
            # Localiza todos os elementos de mensagem
            message_elements = self.driver.find_elements(
                By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]'
            )
            
            for element in message_elements:
                # Extrai detalhes da mensagem
                sender = self.extract_sender(element)
                timestamp = self.extract_timestamp(element)
                text = self.extract_text(element)
                images = self.extract_images(element)
                documents = self.extract_documents(element)
                
                messages.append({
                    'sender': sender,
                    'timestamp': timestamp,
                    'text': text,
                    'images': images,
                    'documents': documents
                })
            
            return messages
        except Exception as e:
            print(f"[ERROR] Erro ao obter detalhes das mensagens: {str(e)}")
            return []
    
    def extract_sender(self, message_element) -> str:
        """
        Extrai o nome do remetente de uma mensagem.
        
        Args:
            message_element: Elemento DOM da mensagem
            
        Returns:
            Nome do remetente ou "Você"/"Desconhecido" se não encontrado
        """
        try:
            sender_element = message_element.find_element(By.XPATH, './/span[@data-testid="author"]')
            return sender_element.text
        except NoSuchElementException:
            # Provavelmente é uma mensagem enviada pelo próprio usuário
            return "Você"
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o remetente: {str(e)}")
            return "Desconhecido"
    
    def extract_timestamp(self, message_element) -> str:
        """
        Extrai o timestamp de uma mensagem.
        
        Args:
            message_element: Elemento DOM da mensagem
            
        Returns:
            Timestamp da mensagem ou timestamp atual se não encontrado
        """
        try:
            timestamp_element = message_element.find_element(By.XPATH, './/div[@data-testid="msg-meta"]')
            return timestamp_element.text
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o timestamp: {str(e)}")
            return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def extract_text(self, message_element) -> str:
        """
        Extrai o texto de uma mensagem.
        
        Args:
            message_element: Elemento DOM da mensagem
            
        Returns:
            Texto da mensagem ou string vazia se não encontrado
        """
        try:
            # Tenta encontrar o elemento de texto
            text_element = message_element.find_element(
                By.XPATH, './/div[@data-testid="msg-container"]//span[@dir="ltr"]'
            )
            return text_element.text.strip()
        except NoSuchElementException:
            # Pode ser uma mensagem sem texto (apenas mídia)
            return ""
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o texto: {str(e)}")
            return ""
    
    def extract_images(self, message_element) -> List[str]:
        """
        Extrai URLs de imagens de uma mensagem.
        
        Args:
            message_element: Elemento DOM da mensagem
            
        Returns:
            Lista de URLs de imagens na mensagem
        """
        try:
            # Procura por imagens na mensagem
            image_elements = message_element.find_elements(
                By.XPATH, './/img[contains(@src, "blob:") or contains(@src, "https://")]'
            )
            return [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]
        except Exception as e:
            print(f"[WARN] Não foi possível extrair imagens: {str(e)}")
            return []
    
    def extract_documents(self, message_element) -> List[Tuple[str, str]]:
        """
        Extrai URLs e nomes de documentos de uma mensagem.
        
        Args:
            message_element: Elemento DOM da mensagem
            
        Returns:
            Lista de tuplas (url, nome_arquivo) de documentos na mensagem
        """
        try:
            # Procura por links de documentos na mensagem
            doc_elements = message_element.find_elements(
                By.XPATH, './/a[contains(@href, "blob:") or contains(@href, "https://")]'
            )
            
            docs = []
            for doc in doc_elements:
                href = doc.get_attribute('href')
                filename = doc.get_attribute('download') or ""
                if href:
                    docs.append((href, filename))
            
            return docs
        except Exception as e:
            print(f"[WARN] Não foi possível extrair documentos: {str(e)}")
            return []
    
    def wait_for_messages_to_load(self, timeout=10) -> bool:
        """
        Espera que as mensagens sejam carregadas na página.
        
        Args:
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            True se mensagens forem carregadas, False caso contrário
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="copyable-text"]'))
            )
            return True
        except TimeoutException:
            print("[WARN] Timeout esperando mensagens carregarem")
            return False