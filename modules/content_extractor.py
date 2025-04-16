# modules/content_extractor.py
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

class ContentExtractor:
    """
    Extrai conteúdo das mensagens do WhatsApp.
    """
    def __init__(self, driver):
        """Inicializa com o driver do selenium."""
        self.driver = driver
    
    def get_all_messages(self):
        """Obtém todos os elementos de mensagem."""
        try:
            # Espera pelo contêiner de mensagensx
            message_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="application"]'))
            )
            # Encontra todas as mensagens (este XPath pode variar dependendo da estrutura do WhatsApp Web)
            messages = message_container.find_elements(By.XPATH, '//div[@class="message-out focusable-list-item _amjy _amjw"]')
            return messages
            
        except Exception as e:
            print(f"[ERROR] Erro ao obter mensagens: {str(e)}")
            return []
    
    def extract_sender(self, message_element):
        """Extrai o nome do remetente de uma mensagem."""
        try:
            sender_element = message_element.find_element(By.XPATH, './/span[@data-testid="author"]')
            return sender_element.text
        except NoSuchElementException:
            # Pode ser uma mensagem enviada pelo próprio usuário
            return "Você"
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o remetente: {str(e)}")
            return "Desconhecido"
    
    def extract_timestamp(self, message_element):
        """Extrai o timestamp de uma mensagem."""
        try:
            # Procura pelo elemento de timestamp
            timestamp_element = message_element.find_element(By.XPATH, './/div[@data-testid="msg-meta"]')
            return timestamp_element.text
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o timestamp: {str(e)}")
            return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def extract_text(self, message_element):
        """Extrai o texto de uma mensagem."""
        try:
            # Procura pelo elemento de texto
            text_element = message_element.find_element(By.XPATH, './/div[@data-testid="msg-container"]//span[@dir="ltr"]')
            return text_element.text
        except NoSuchElementException:
            # Pode ser uma mensagem sem texto (apenas mídia)
            return ""
        except Exception as e:
            print(f"[WARN] Não foi possível extrair o texto: {str(e)}")
            return ""
    
    def extract_images(self, message_element):
        """Extrai URLs de imagens de uma mensagem."""
        try:
            # Procura por imagens na mensagem
            image_elements = message_element.find_elements(By.XPATH, './/img[contains(@src, "blob:") or contains(@src, "https://")]')
            return [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]
        except Exception as e:
            print(f"[WARN] Não foi possível extrair imagens: {str(e)}")
            return []
    
    def extract_documents(self, message_element):
        """Extrai URLs de documentos de uma mensagem."""
        try:
            # Procura por links de documentos na mensagem
            doc_elements = message_element.find_elements(By.XPATH, './/a[contains(@href, "blob:") or contains(@href, "https://")]')
            
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