# Написать вспомогательные инструменты:
# 1. Декоратор (log_execution_time):
#     * Универсальный декоратор (принимает аргументы включения логов), который замеряет время выполнения функций
#     парсинга и логирует результат.
# 2. Контекстный менеджер (AuditSession):
#     * Управляет жизненным циклом сессии: фиксирует время старта, выводит приветствие в консоль, а в блоке
#     finally (даже при возникновении ошибок) сохраняет итоговый словарь отчета в файл reports/audit_report.json с
#     помощью pathlib.

import json
import time
from functools import wraps
from contextlib import contextmanager
from pathlib import Path


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
def AuditSession():
    print(f"[MONITOR] Start script work")
    start_time = (time.ctime(), time.time())
    result = {}
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
                    "error": str(error)
        
 } 
        # For dev............................................
        raise error

        
                    

    finally:
        print(result)
        report = {
                    "status": "success",
                    "session_info": {
                        "start_time": start_time[0],
                        "end_time": time.ctime(),
                        "duration_seconds": round(time.time() - start_time[1], 4)
                    },
                    "statistics": {
                        "total_files_processed": result["total_files_processed"],
                        "total_lines_scanned": result["total_lines_scanned"],
                        "total_errors_found": result["total_errors_found"]
                    },
                    "error_types": result["error_types"],
                    "details": result["details"]
                }
        audit_report_path = Path(__file__).resolve().parent / "reports/audit_report.json"
        try:
            with open(audit_report_path, "w", encoding="utf-8") as audit_report:
                json.dump(report, audit_report, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, json.JSONDecodeError, FileNotFoundError, FileExistsError) as error:
            print("The critical error happened, file didn't save")
        else:
            print(f"[MONITOR] Script ended work. with time <{round((start_time[1] - time.time()), 4)}>s")


