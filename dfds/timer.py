import sys
import time

def run_timer():
    print("Stopwatch started. Press Ctrl+C to stop.")
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            sys.stdout.write(f"\rElapsed: {elapsed:.2f} seconds")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print(f"\nStopwatch stopped. Elapsed: {elapsed:.2f} seconds.")