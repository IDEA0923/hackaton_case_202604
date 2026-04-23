from datetime import datetime

def date_to_seconds(date_string: str, date_format: str = "%d.%m.%Y %H:%M") -> int:
    """
    Переводит строку с датой в секунды (Unix timestamp).
    Возвращает int (секунды) или None, если формат неверный.
    """
    try:
        # Преобразуем строку в объект datetime
        dt = datetime.strptime(date_string, date_format)
        # Получаем timestamp и переводим в целое число
        return int(dt.timestamp())
    except ValueError as e:
        print(f"[-] Ошибка парсинга даты: {e}")
        return None
    
