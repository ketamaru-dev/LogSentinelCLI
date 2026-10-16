# Написать вспомогательные инструменты:
# 1. Декоратор (log_execution_time):
#     * Универсальный декоратор (принимает аргументы включения логов), который замеряет время выполнения функций
#     парсинга и логирует результат.
# 2. Контекстный менеджер (AuditSession):
#     * Управляет жизненным циклом сессии: фиксирует время старта, выводит приветствие в консоль, а в блоке
#     finally (даже при возникновении ошибок) сохраняет итоговый словарь отчета в файл reports/audit_report.json с
#     помощью pathlib.

from functools import wraps
from contextlib import contextmanager, Iterator
from pathlib import Path
import json
import time

def log_execution_time(enabled: bool = True):

    def decorator(func):
        if enabled: print("[EXC] Start Functions work")
        start_time = time.time()

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if enabled: print(f"[EXC] Function was end succsessfully. Work time: <{round(time.time() - start_time(), 4)}>s")
                return result
            except Exception as error:
                if enabled: print(f"[EXC] Function was end with ERROR {error}.\n Work time: <{round(time.time() - start_time(), 4)}>s")
        return wrapper
    return decorator

@contextmanager
def AuditSession() -> Iterator[None]:
    print(f"[MONITOR] Start script work")
    start_time = (time.ctime(), time.time())
    result = None
    try:
        yield result
    except Exception as error:
        end_time = (time.ctime(), time.time())
        report = {
                    "status": "failed",
                    "session_info": {
                        "start_time": start_time[0],
                        "end_time": end_time[0],
                        "duration_seconds": round(start_time[1] - end_time[1],2)
                    },
                    "error": error.info,
}   
    else:

        report = {
                    "status": "success",
                    "session_info": {
                        "start_time": start_time[0],
                        "end_time": end_time[0],
                        "duration_seconds": round(start_time[1] - end_time[1],2)
                    },
                    "statistics": {
                        "total_files_processed": report.files_counter,
                        "total_lines_scanned": report.lines_counter,
                        "total_errors_found": report.errors_counter
                    },
                    "error_types": report.errors_types,
                    "details": report.details
                    
}
    finally:
        audit_report_path = Path(__file__).resolve().parent / "reports/audit_report.json"
        with open(audit_report_path, "w", encoding="utf-8") as audit_report:
            json.dump(report, audit_report_path, ensure_ascii=False, indent=4)
            
        print(f"[MONITOR] Script ended work. All information wrote by path reports/audit_report.json.")