import sys
import threading
import re
import yfinance as yf
from contextlib import contextmanager

from app.crud.missing_data import insert_missing_data

# Thread-safe capture of stderr
@contextmanager
def capture_stderr_threadsafe():
    buffer = []

    original_write = sys.stderr.write
    lock = threading.Lock()

    def write_override(s):
        with lock:
            buffer.append(s)
        return original_write(s)

    sys.stderr.write = write_override
    try:
        yield buffer
    finally:
        sys.stderr.write = original_write

def safe_download(symbols, db=None, **kwargs):
    failed = []

    with capture_stderr_threadsafe() as output:
        df = yf.download(symbols, **kwargs)

    # Join the captured output into lines
    log_contents = "".join(output)

    for line in log_contents.splitlines():
        if "possibly delisted" in line:
            pattern = re.compile(
                r"\['(?P<symbol>[^']+)'\]:\s*YFPricesMissingError\('(?P<reason>[^;]+);.*?\(\d+d\s+(?P<start>\d{4}-\d{2}-\d{2}) -> (?P<end>\d{4}-\d{2}-\d{2})\)"
            )
            match = pattern.search(line)
            if match:
                symbol = match.group("symbol")
                start = match.group("start")
                end = match.group("end")
                reason = match.group("reason")
                failed.append((symbol, start, end, reason))

                if db is not None:
                    try:
                        insert_missing_data(db, symbol, start, end, reason)
                    except Exception as e:
                        print(e)

    if failed:
        print("=== Captured missing/failed symbols ===")
        for f in failed:
            print(f)

    return df
