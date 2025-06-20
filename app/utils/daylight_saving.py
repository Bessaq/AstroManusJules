# daylight_saving.py

from datetime import datetime, date
from zoneinfo import ZoneInfo

def is_daylight_saving_active(check_date: date, tz_name: str = "America/Sao_Paulo") -> bool:
    """
    Retorna True se, na data dada, o horário de verão estava ativo no fuso indicado.
    Usa zoneinfo para determinar dinamicamente se a DST (Daylight Saving Time) está em
    vigor na data fornecida.

    Parâmetros:
        check_date (date): data a ser verificada.
        tz_name (str): nome do fuso horário a ser usado (padrão: "America/Sao_Paulo").

    Retorna:
        bool: True se estiver em horário de verão, False caso contrário.
    """
    # Usar o horário das 12:00 para evitar ambiguidades na troca de horário
    dt = datetime(
        year=check_date.year,
        month=check_date.month,
        day=check_date.day,
        hour=12,
        tzinfo=ZoneInfo(tz_name)
    )
    # dt.dst() retorna um timedelta > 0 se DST estiver ativo
    return bool(dt.dst())


def get_timezone_offset_with_dst(check_date: date, tz_name: str) -> float:
    """
    Retorna o offset UTC em horas considerando horário de verão.
    
    Parâmetros:
        check_date (date): data a ser verificada.
        tz_name (str): nome do fuso horário.
        
    Retorna:
        float: offset UTC em horas (pode ser negativo)
    """
    dt = datetime(
        year=check_date.year,
        month=check_date.month,
        day=check_date.day,
        hour=12,
        tzinfo=ZoneInfo(tz_name)
    )
    return dt.utcoffset().total_seconds() / 3600


def get_timezone_info(check_date: date, tz_name: str) -> dict:
    """
    Retorna informações completas do timezone para uma data específica.
    
    Parâmetros:
        check_date (date): data a ser verificada.
        tz_name (str): nome do fuso horário.
        
    Retorna:
        dict: informações do timezone
    """
    dt = datetime(
        year=check_date.year,
        month=check_date.month,
        day=check_date.day,
        hour=12,
        tzinfo=ZoneInfo(tz_name)
    )
    
    utc_offset = dt.utcoffset().total_seconds() / 3600
    dst_offset = dt.dst().total_seconds() / 3600 if dt.dst() else 0
    is_dst = bool(dt.dst())
    
    return {
        "timezone_name": tz_name,
        "utc_offset": utc_offset,
        "dst_offset": dst_offset,
        "is_dst_active": is_dst,
        "standard_offset": utc_offset - dst_offset,
        "date_checked": check_date.isoformat(),
        "datetime_with_tz": dt.isoformat()
    }


if __name__ == "__main__":
    # Exemplos de uso
    examples = [
        date(1931, 10, 3),
        date(1931, 10, 2),
        date(1964, 2, 29),
        date(1964, 3, 1),
        date(2018, 11, 4),
        date(2019, 2, 17),
        date(2019, 2, 18),
        date(2020, 5, 10),
        date.today(),
    ]

    for d in examples:
        status = "ativo" if is_daylight_saving_active(d) else "não ativo"
        print(f"Em {d.strftime('%d/%m/%Y')}, o horário de verão está {status}.")