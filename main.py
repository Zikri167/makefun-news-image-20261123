import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = draw.render()
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
