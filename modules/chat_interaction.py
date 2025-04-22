# modules/chat_interaction.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from config.settings import TIME_WAIT

class ChatInteraction:
    """
    Gerencia interações com chats e contatos no WhatsApp Web.
    """
    def __init__(self, driver):
        """Inicializa com o driver do selenium."""
        self.driver = driver
    
    def find_chat(self, contact_name):
        """
        Procura por um contato ou grupo específico.
        
        Args:
            contact_name (str): Nome do contato ou grupo a ser buscado
            
        Returns:
            bool: True se encontrado, False caso contrário
        """
        try:
            # Clica na barra de pesquisa
            search_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Caixa de texto de pesquisa"]'))
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(contact_name)
            
            time.sleep(TIME_WAIT * 2)  # Aguarda a busca ser realizada
            
            # Tenta encontrar o contato na lista de resultados
            try:
                contact = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
                )
                contact.click()
                print(f"[DEBUG] Contato '{contact_name}' encontrado e selecionado!")
                return True
            
            # Caso o contato não seja encontrado, trata a exceção
            except TimeoutException:
                print(f"[DEBUG] Contato '{contact_name}' não encontrado.")
                return False
                
        except Exception as e:
            print(f"Erro ao buscar contato: {str(e)}")
            return False
    
    def send_message(self, message):
        """
        Envia uma mensagem para o contato/grupo selecionado atualmente.
        
        Args:
            message (str): Mensagem a ser enviada
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Encontra a caixa de texto
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-compose-box-input"]'))
            )
            message_box.click()
            
            # Digita a mensagem
            actions = ActionChains(self.driver)
            actions.send_keys(message)
            actions.perform()
            
            # Clica no botão de enviar
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]'))
            )
            send_button.click()
            
            print(f"Mensagem enviada: '{message}'")
            return True
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return False
    
    def scroll_to_top(self):
        """
        Rola para cima para carregar mensagens mais antigas.
        Implementa múltiplos métodos para garantir que a rolagem funcione.
        """
        print("[DEBUG] Iniciando carregamento de mensagens antigas...")
          
        # Método 1: Usar o HOME do teclado
        try:
            # Clica no contêiner de mensagens primeiro para focar
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()
            
            actions = ActionChains(self.driver)
            
            # Número de rolagens (ajuste conforme necessário)
            scroll_attempts = 100
            
            for i in range(scroll_attempts):
                actions.send_keys(Keys.HOME).perform()
                time.sleep(0.1)  # Espera um pouco entre as rolagens
                
        except Exception as e:
            print(f"[DEBUG] Método de rolagem HOME falhou: {str(e)}")
    
    def find_message(self):
        """
        Tenta encontrar o botão "Carregar mensagens anteriores" ou a primeira mensagem.
        Se encontrar o botão, clica nele para carregar mais mensagens.
        """
        try:
            # Comando para rolar para o topo da conversa
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.HOME).perform()

            # Tenta encontrar o botão "Carregar mensagens anteriores"
            # Os XPaths podem variar de acordo com a versão do WhatsApp Web
            load_more_selectors = [
                '//div[contains(text(), "Clique neste aviso para carregar mensagens mais antigas do seu celular.")]',
                '//div[contains(text(), "Carregar mais")]',
                '//span[contains(text(), "mensagens anteriores")]',
                '//div[contains(@data-testid, "load-earlier-messages")]',
                '//div[contains(text(), "Carregando")]',
                '//div[contains(text(), "carregar")]', 
            ]
            
            # Percorre os seletores para encontrar o botão
            for selector in load_more_selectors:
                try:
                    load_more_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    load_more_button.click()
                    print("[DEBUG] Botão 'Carregar mensagens anteriores' encontrado e clicado")
                    time.sleep(5)  # Espera carregar as mensagens
                    return True
                
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
            
            print("[DEBUG] Botão 'Carregar mensagens anteriores' não encontrado")
            return False
            
        except Exception as e:
            print(f"[DEBUG] Não foi possível encontrar o botão de carregar mensagens")
            return False
    
    def load_all_messages(self, max_attempts=100):
        """
        Combina várias estratégias para tentar carregar o máximo de mensagens antigas.
        
        Args:
            max_attempts (int): Número máximo de tentativas
        """
        print("[DEBUG] Iniciando carregamento completo do histórico de mensagens...")      
            
        # Permite que o usuário role para cima manualmente
        loading_messages = True
        
        # Número máximo de tentativas para rolar e carregar mensagens
        max_attempt = 1 

        # Lógica para continuar rolando até que não haja mais mensagens a carregar
        while loading_messages and max_attempt > 0:
            
            # Aguarda um pouco para garantir que as mensagens sejam carregadas
            self.scroll_to_top()

            # Verifica novamente se o botão de carregar mensagens ainda está presente
            loading_messages = self.find_message()

            # Aumenta o contador de tentativas
            max_attempt -= 1
    
        print("[DEBUG] Processo de carregamento de mensagens antigas concluído")