"""Check the running API and its bundled models without training or AWS calls."""

import argparse
from pathlib import Path
import pickle
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd


def check(base_url: str) -> None:
    deadline = time.monotonic() + 60
    while True:
        try:
            with urlopen(f"{base_url}/docs", timeout=3) as response:
                if response.status == 200:
                    break
        except (URLError, TimeoutError, ConnectionError):
            if time.monotonic() >= deadline:
                raise RuntimeError("The API did not start within 60 seconds")
            time.sleep(1)

    # These are this project's own, trusted serving artifacts.
    with Path("final_models/preprocessor.pkl").open("rb") as stream:
        preprocessor = pickle.load(stream)
    columns = list(preprocessor.feature_names_in_)
    sample = pd.DataFrame([[1] * len(columns)], columns=columns)

    boundary = "networksecurity-container-check"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="sample.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
        f"{sample.to_csv(index=False)}\r\n"
        f"--{boundary}--\r\n"
    ).encode()
    request = Request(
        f"{base_url}/predict",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        html = response.read().decode()
        if response.status != 200 or "predicted_column" not in html:
            raise RuntimeError("The prediction route did not render its result")
    print("OK: /docs and CSV /predict, using the bundled models and HTML template")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    check(args.base_url.rstrip("/"))
