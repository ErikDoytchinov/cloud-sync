#!/usr/bin/env python3
"""
Welcome to Cloud Sync!
This script downloads a wheel file from a URL, installs it
and runs the cloud_sync module.

The goal of this script is to be kept at a MINIMUM in size, and
bundle only the necessary logic to run the cloud_sync module.
This is done for security reasons, to reduce the attack surface.
"""

# Only import stdlib stuff here!
# Also, no import of other modules. This is a self contained script.
import subprocess
import sys
import urllib.request
import ssl
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("loader")

WHEEL_URL = "http://host.docker.internal:8080/cloud_sync-0.1.0-py3-none-any.whl"


def main():
    wheel_file = "/dist/cloud_sync-0.1.0-py3-none-any.whl"
    logger.info(f"Downloading {WHEEL_URL} to {wheel_file}")
    mkdir_if_not_exists(wheel_file)
    download_wheel(wheel_file)
    logger.info(f"Installing {wheel_file}")
    pip_install(wheel_file)
    logger.info("Running cloud_sync")
    run_cloud_sync()
    logger.info("Done")


def mkdir_if_not_exists(path: str):
    dirs = os.path.dirname(path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def download_wheel(out_file: str):
    assert (
        WHEEL_URL.startswith("https://")
        or WHEEL_URL.startswith("http://host.docker.internal")
        or WHEEL_URL.startswith("http://localhost")
    ), "Only HTTPS or localhost allowed"

    # https://docs.python.org/3.8/library/ssl.html#ssl-security
    ssl_context = ssl.create_default_context()
    assert ssl_context.verify_mode == ssl.CERT_REQUIRED, "CERT_REQUIRED not set"
    assert ssl_context.check_hostname, "check_hostname not set"

    with urllib.request.urlopen(WHEEL_URL, timeout=20, context=ssl_context) as f:
        with open(out_file, "wb") as out:
            out.write(f.read())


def pip_install(package):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--upgrade", "pip"]
    )
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", package]
    )


def run_cloud_sync():
    subprocess.check_call([sys.executable, "-m", "cloud_sync.main"])


if __name__ == "__main__":
    main()
