# 1. Абстрактный класс BaseParser (используя abc.ABC и @abstractmethod):
#     * Должен содержать защищенные или приватные атрибуты состояния (например, счетчик обработанных строк и
#     найденных ошибок).
#     * Обязательный абстрактный метод parse_line(self, line: str) -> dict.
#     * Свойства (@property) для получения текущей статистики парсера.
# 2. Конкретные парсеры (минимум два):
#     * StandardLogParser — разбирает стандартные строковые логи (ожидает дату, уровень вроде INFO/ERROR и текст).
#     * GenericFallbackParser — универсальный парсер, который ищет ошибки по ключевым словам (ERROR, CRITICAL,
#     Exception, Failed) для файлов с неизвестной структурой.

import exceptions
import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path


# There is abstract base class for parsers
class BaseParser(ABC):
    def __init__(self):
        self.error_types = set()
        self._line_count = 0
        self._errors_count = 0

    @abstractmethod
    def parse_line(self, line: str) -> dict:
        pass

    @property
    def line_count(self):
        return self._line_count

    @line_count.setter
    def line_count(self, value: int):
        try:
            if type(value) is int or type(value) is float:
                if value >= 0:
                    self._line_count = value
                else:
                    raise ValueError("Value not valid")
            else:
                raise TypeError("Value not a number")
        except (ValueError, TypeError) as err:
            print("Error, try another value", err)
            raise err
    
    @property
    def errors_count(self):
        return self._errors_count

    @errors_count.setter
    def errors_count(self, value: int):
            try:
                if type(value) is int or type(value) is float:
                    if value >= 0:
                        self._errors_count = value
                    else:
                        raise ValueError("Value not valid")
                else:
                    raise TypeError("Value not a number")
            except (ValueError, TypeError) as err:
                print("Error, try another value", err)

    def take_report(self):
        return (self.error_types, self.errors_count, self.line_count)
          

# Class for standart log parse from module logging (Python) 
# Log example: [2026-10-16 12:00:01,123 - [INFO] - main_module - Сообщение]
class StandardLogParser(BaseParser):

    async def parse_line(self, line) -> dict:
        if not type(line) is str:
            taked_line = line
            line = next(line)
        parsed_line = [line[0:23]]
        parsed_line.extend(line[26:].split("-"))
        try:
            if len(parsed_line) != 4:
                raise exceptions.LogFormatError(self.line_count)
            if any(parsed_line[1][1:][:len(parsed_line[1][1:]) - 2].lower() in kw for kw in ["error", "warning", "critical", "exception", "failed"]):
                processed_line = {
                                    "timestamp": parsed_line[0],
                                    "level": parsed_line[1][1:][:len(parsed_line[1][1:]) - 2],
                                    "module": parsed_line[2],
                                    "message": parsed_line[3],
                                }
                self.error_types.add(processed_line["level"])
                self.line_count += 1
                self.errors_count += 1
                return processed_line
            self.line_count += 1
            return None
            
        except exceptions.LogFormatError as err:
            self.errors_count += 1
            return err


# Class for all types of logs parse use keywords (ERROR, CRITICAL, EXCEPTION, FAILED, WARNING) for files with unknown structure
class GenericFallbackParser(BaseParser):

    async def parse_line(self, line: str) -> dict:
            if not type(line) is str:
                taked_line = line
                line = next(line)
            if any(kw in parsed_line.lower() for kw in ["error", "warning", "critical", "exception", "failed"]):
                processed_line = {
                                    "message": parsed_line,
                                }
                self.line_count += 1
                self.errors_count += 1
                return processed_line
            self.line_count += 1
            return None
                
    
__all_parsers__ = (StandardLogParser, GenericFallbackParser)

#if parser doesn't work, then go to next parser from list
def pick_parser(line: str):
    for parser in __all_parsers__:
        try:
            test_parser_obj = parser()
            test_parser_obj.parse_line(line)
            return parser
        except exceptions.LogFormatError as parse_error:
            pass
    raise exceptions.FileParseError
