import sys
from pathlib import Path
import asyncio
import parsers


def main():
    path = Path(__file__).resolve().parent / "logs/app.log"
    result = asyncio.run(parsers.StandardLogParser(path).parse_file())
    print(*result)

if __name__ == "__main__":
    main()