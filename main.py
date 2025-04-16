from core.base_scraper import WhatsappScraper

if __name__ == "__main__":
    # Cria uma instância do scraper do WhatsApp
    scraper = WhatsappScraper()

    # Extrai informações do WhatsApp Web
    scraper.extract_group_content("Grupo")