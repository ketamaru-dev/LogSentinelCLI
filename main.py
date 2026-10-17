# Задача 4: Асинхронный движок и CLI (main.py)
# Реализовать точку входа и логику обработки:
# 1. Написать асинхронный генератор для построчного чтения файлов логов (async def read_file_lines(filepath)),
# чтобы не перегружать оперативную память большими файлами.
# 2. С помощью sys считывать аргументы командной строки (например, путь к папке с логами).
# 3. Используя pathlib.Path, находить все .log файлы в целевой директории.
# 4. Организовать параллельный запуск обработки файлов через asyncio.gather.
# 5. Использовать коллекции (set для уникальных типов ошибок, dict для статистики) для агрегации данных.
# 5. Критерии приемки (Definition of Done)
# * Код запускается без ошибок через терминал.
# * Все компоненты покрыты аннотациями типов (typing).
# * При передаче битого файла или отсутствующего файла утилита не падает с системным Traceback, а корректно
# обрабатывает ошибку через кастомные исключения.
# * Итоговый JSON-отчет успешно генерируется в папке reports/.


import asyncio
import aiofiles
import sys
import parsers
import json

from pathlib import Path
from exceptions import FileParseError, FileReadError
from utils import log_execution_time, AuditSession


# Async generator for reading log file
async def read_file_lines(filepath):
    try:
        async with aiofiles.open(filepath, "r", encoding="utf-8") as file:
            async for line in file:
                yield line
    except (FileNotFoundError, FileExistsError, IsADirectoryError) as error:
        raise FileReadError


# @log_execution_time
async def check_log(log_file):
    try:
        parser = parsers.pick_parser(anext(read_file_lines(log_file)))
    except (FileParseError, FileReadError) as parse_error:
        return {
            "status": 1,
            "information": parse_error 
        }
    
    main_parser = parser()
    all_errors_logs: list = await asyncio.gather(*[main_parser.parse_line(line) async for line in read_file_lines(log_file)])
    all_errors_logs = [log for log in all_errors_logs if not log is None]
    parser_report: tuple = main_parser.take_report()

    return {
        "status": 0,
        "information" : {
            "log_file_name": log_file.name,
            "processed": parser_report[2],              # int
            "errors": parser_report[1],                 # int
            "all_error_types": list(parser_report[0]),        # set
            "bad_log_list": all_errors_logs,            # list logs
        }
    }


# Take paths from directory
def all_logs_file(logs_path):
    return [file for file in logs_path.iterdir()]

def save_logs_report(information: dict, path = (Path(__file__).resolve().parent / "reports/")):
        for log in information: 
            try:  
                with open(path / f"{log["information"]["log_file_name"]}", "w", encoding="utf-8") as file:
                    json.dump(log, file, indent=4, ensure_ascii=False)
            except (FileNotFoundError, json.JSONDecodeError) as error:
                print("[Error] Cleared logs didn't save!")

# Pack all log's reports to one document
def report_packing(information_list: dict):
    save_logs_report(information_list)
    details = {
        log["information"]["log_file_name"]:{
                                            "processed":log["information"]["processed"],
                                            "errors": log["information"]["errors"]
                                            } for log in information_list}
    
    result = {
        "total_files_processed": len(information_list),
        "total_lines_scanned": sum([pos["information"]["processed"] for pos in information_list]),
        "total_errors_found": sum([pos["information"]["errors"] for pos in information_list]),
        "error_types": list(set().union(*[set(pos["information"]["all_error_types"]) for pos in information_list])),
        "details": details
    }
    return result


async def start():
    # Take the path to logs (base same directory)
    with AuditSession() as res:
        if len(sys.argv) == 1:
            logs_path = Path(__file__).resolve().parent / "logs/"
        elif len(sys.argv) == 2:
            logs_path = Path(sys.argv[1])
        else:
            print("Error, wrong arguments (support only logs path in argumet)")
            sys.exit(1)

        # Take list of all logs files in directory
        logs_list = all_logs_file(logs_path)
        information_list = await asyncio.gather(*(check_log(path_log) for path_log in logs_list))
        inf = report_packing(information_list)
        res.update(inf)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
