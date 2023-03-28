import time


class TimeIt:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"TimeIt \"{self.name}\": {time.time()-self.start_time:.3}s")


if __name__ == "__main__":
    with TimeIt("sleep"):
        for i in range(14):
            time.sleep(0.1)