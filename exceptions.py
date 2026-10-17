# Задача 1: Иерархия исключений (exceptions.py)
# Создать собственные классы ошибок, наследуемые от базового Exception:
# * LogSentinelError — главный базовый класс для всех ошибок утилиты.
# * FileReadError — вызывается при проблемах с чтением файла (файл не найден, нет прав). Должен содержать
# атрибут пути к файлу.
# * LogFormatError — вызывается при критической ошибке разбора строки.



class LogSentinelError(Exception):
    pass
    


class FileReadError(LogSentinelError):
    def __init__(self, path):
        self.path = path
        super().__init__(f"[ERROR]File not readed in path {path}")

class LogFormatError(Exception):
    def __init__(self, line_num: int):
        print(f"[ERROR]Critical error of parsing the line {line_num}")
        super().__init__()

class FileParseError(Exception):
    def __init__(self):
        print(f"[ERROR] Script can't parse a log file")
        super().__init__()