# coding: utf-8
import io
from pathlib import Path
import zipfile
import venv
import subprocess

from fastapi import FastAPI, UploadFile, File


app = FastAPI()


@app.post("/upload_src/{env_name}")
async def upload_src(env_name: str, file: UploadFile = File(...)):

    # read the zip archive
    content = await file.read()

    # extract in temp folder
    p = Path("envs") / env_name
    p.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(content), 'r') as zip:
        zip.extractall(path=p / "src")

    # create a venv with pip
    venv.EnvBuilder(with_pip=True).create(p / "venv")

    # install requirements
    req = p / "src" / "requirements.txt"
    if req.is_file():
        # replace Script/pip.exe by bin/pip on linux
        process = subprocess.Popen([p / "venv" / "Scripts" / "pip.exe", "install", "-r", req])  
        process.wait()

    return f"env {env_name} created"


@app.get("/run_env")
async def run_env(env_name: str, script_name: str):
    p = Path("envs") / env_name
    # replace Script/python.exe by bin/python on linux
    process = subprocess.Popen([p / "venv" / "Scripts" / "python.exe", script_name], stdout=subprocess.PIPE)
    output, _ = process.communicate()

    return output
