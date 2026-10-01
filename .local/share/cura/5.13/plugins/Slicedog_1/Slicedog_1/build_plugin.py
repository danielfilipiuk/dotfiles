import os
import subprocess
import shutil
import argparse
import urllib.request

LIBS_PATH = os.path.join("libs")

parser = argparse.ArgumentParser()
parser.add_argument("--target", required=True, choices=["windows", "linux"], help="Target platform")
args = parser.parse_args()

if os.path.exists(LIBS_PATH):
    shutil.rmtree(LIBS_PATH)
os.makedirs(LIBS_PATH, exist_ok=True)

packages = [
    "google-auth-oauthlib==1.2.2",
    "websockets==15.0.1"
]
subprocess.run(["pip", "install", *packages, "-t", LIBS_PATH])

if args.target == "windows":
    # TODO check if this is not necessary for linux

    TEMP_WHEEL_DIR = "temp_wheel"
    WSGIREF_DEST = os.path.join(LIBS_PATH, "wsgiref")

    os.makedirs(TEMP_WHEEL_DIR, exist_ok=True)

    url = "https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz"
    archive_path = os.path.join(TEMP_WHEEL_DIR, "python.tgz")

    urllib.request.urlretrieve(url, archive_path)

    import tarfile
    with tarfile.open(archive_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.name.startswith("Python-3.10.9/Lib/wsgiref/")]
        tar.extractall(path=TEMP_WHEEL_DIR, members=members)

    src = os.path.join(TEMP_WHEEL_DIR, "Python-3.10.9", "Lib", "wsgiref")
    shutil.copytree(src, WSGIREF_DEST)

    shutil.rmtree(TEMP_WHEEL_DIR)

print("Build complete for", args.target)