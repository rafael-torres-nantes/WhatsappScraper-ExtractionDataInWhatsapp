# modules/file_manager.py
import os
import re
import requests
import time

class FileManager:
    """
    Gerencia operações de arquivo e download de conteúdo.
    """
    def __init__(self, driver, output_dir, main_window):
        """
        Inicializa o gerenciador de arquivos.
        
        Args:
            driver (webdriver): Instância do webdriver do Selenium
            output_dir (str): Diretório de saída para salvar os arquivos
            main_window (str): Handle da janela principal do navegador
        """
        self.driver = driver
        self.output_dir = output_dir
        self.main_window = main_window
        
        # Garante que o diretório de saída exista
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_group_directories(self, group_name):
        """
        Cria diretórios para armazenar o conteúdo extraído do grupo.
        
        Args:
            group_name (str): Nome do grupo ou contato
            
        Returns:
            tuple: Diretórios criados (group_dir, images_dir, docs_dir, messages_file)
        """
        # Cria um diretório específico para o grupo
        group_dir = os.path.join(self.output_dir, re.sub(r'[\\/*?:"<>|]', '', group_name))
        os.makedirs(group_dir, exist_ok=True)
        print(f"[DEBUG] Diretório criado: {group_dir}")
            
        # Cria subdiretórios para imagens e documentos
        images_dir = os.path.join(group_dir, "images")
        docs_dir = os.path.join(group_dir, "documents")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)
        print(f"[DEBUG] Subdiretórios criados: {images_dir}, {docs_dir}")
            
        # Arquivo para salvar as mensagens de texto
        messages_file = os.path.join(group_dir, "messages.txt")
        
        return group_dir, images_dir, docs_dir, messages_file
    
    def save_messages_to_file(self, messages, file_path):
        """
        Salva mensagens em um arquivo de texto.
        
        Args:
            messages (list): Lista de strings de mensagens
            file_path (str): Caminho do arquivo para salvar
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            for message in messages:
                f.write(message + "\n")
    
    def download_file(self, url, local_path):
        """
        Baixa um arquivo da URL especificada para o caminho local.
        
        Args:
            url (str): URL do arquivo
            local_path (str): Caminho local para salvar o arquivo
        """
        try:
            # Para URLs blob:, precisamos usar o webdriver para baixá-las
            if url.startswith('blob:'):
                # Abre uma nova aba
                self.driver.execute_script("window.open(arguments[0]);", url)
                
                # Muda para a nova aba
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # Aguarda o carregamento da imagem
                time.sleep(2)
                
                # Salva a página (imagem)
                self.driver.save_screenshot(local_path)
                
                # Fecha a aba e volta para a aba principal
                self.driver.close()
                self.driver.switch_to.window(self.main_window)
            else:
                # Para URLs HTTP normais, usa requests
                response = requests.get(url, stream=True)
                with open(local_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            
            print(f"[DEBUG] Arquivo baixado com sucesso: {local_path}")
                            
        except Exception as e:
            print(f"[ERROR] Erro ao baixar arquivo {url}: {str(e)}")
            raise