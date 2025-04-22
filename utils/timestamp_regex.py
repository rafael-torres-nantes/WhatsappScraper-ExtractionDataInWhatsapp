import re
import datetime

def get_timestamp_regex(message) -> str:
    """
    Obtém o timestamp e o usuário remetente da mensagem no WhatsApp Web.

    Args:
        message (WebElement): O elemento da mensagem no WhatsApp Web.


    """
    # Obtém o usuário remetente da mensagem 
    match = re.search(r'\[(\d{2}:\d{2}), (\d{2}/\d{2}/\d{4})\] (.*?):', message)
    
    # Obtém a hora da mensagem
    time_part = match.group(1)

    # Obtém a data da mensagem
    date_part = match.group(2)

    # Obtém o usuário remetente da mensagem
    user = match.group(3)

    # Formata a data e hora para o padrão desejado
    timestamp = datetime.datetime.strptime(f"{date_part} {time_part}", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d-%H:%M")
    print(f"[DEBUG] Timestamp: {timestamp}, Usuário: {user}")

    return user, timestamp