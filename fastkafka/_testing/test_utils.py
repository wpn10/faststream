# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/002_Test_Utils.ipynb.

# %% auto 0
__all__ = ['logger', 'nb_safe_seed', 'true_after', 'mock_AIOKafkaProducer_send', 'run_script_and_cancel', 'display_docs']

# %% ../../nbs/002_Test_Utils.ipynb 1
import asyncio
import contextlib
import functools
import glob
import hashlib
import multiprocessing
import os
import random
import shlex
import shutil
import signal
import socket
import subprocess  # nosec
import tarfile
import textwrap
import time
import unittest
import unittest.mock
from collections import namedtuple
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import *
from unittest.mock import AsyncMock, MagicMock
from IPython.display import IFrame

import asyncer
import nest_asyncio
import posix_ipc

# [B404:blacklist] Consider possible security implications associated with the subprocess module.
import requests
import typer
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from confluent_kafka.admin import AdminClient, NewTopic
from fastcore.foundation import patch
from fastcore.meta import delegates
from pydantic import BaseModel, Field
from tqdm import tqdm

from .._components._subprocess import terminate_asyncio_process

from fastkafka._components.helpers import (
    _import_from_string,
    combine_params,
    filter_using_signature,
    use_parameters_of,
    change_dir,
)
from .._components.logger import get_logger, supress_timestamps
from .._application.app import FastKafka
from fastkafka.helpers import (
    consumes_messages,
    in_notebook,
    produce_messages,
    tqdm,
    trange,
)

# %% ../../nbs/002_Test_Utils.ipynb 2
if in_notebook():
    from tqdm.notebook import tqdm, trange
else:
    from tqdm import tqdm, trange

# %% ../../nbs/002_Test_Utils.ipynb 5
logger = get_logger(__name__)

# %% ../../nbs/002_Test_Utils.ipynb 7
def nb_safe_seed(s: str) -> Callable[[int], int]:
    """Gets a unique seed function for a notebook

    Params:
        s: name of the notebook used to initialize the seed function

    Returns:
        A unique seed function
    """
    init_seed = int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % (10**8)

    def _get_seed(x: int = 0, *, init_seed: int = init_seed) -> int:
        return init_seed + x

    return _get_seed

# %% ../../nbs/002_Test_Utils.ipynb 9
def true_after(seconds: float) -> Callable[[], bool]:
    """Function returning True after a given number of seconds"""
    t = datetime.now()

    def _true_after(seconds: float = seconds, t: datetime = t) -> bool:
        return (datetime.now() - t) > timedelta(seconds=seconds)

    return _true_after

# %% ../../nbs/002_Test_Utils.ipynb 11
@contextmanager
def mock_AIOKafkaProducer_send() -> Generator[unittest.mock.Mock, None, None]:
    """Mocks **send** method of **AIOKafkaProducer**"""
    with unittest.mock.patch("__main__.AIOKafkaProducer.send") as mock:

        async def _f() -> None:
            pass

        mock.return_value = asyncio.create_task(_f())

        yield mock

# %% ../../nbs/002_Test_Utils.ipynb 12
async def run_script_and_cancel(
    script: str,
    *,
    script_file: Optional[str] = None,
    cmd: Optional[str] = None,
    cancel_after: int = 10,
    app_name: str = "app",
    kafka_app_name: str = "kafka_app",
    generate_docs: bool = False,
) -> Tuple[int, bytes]:
    """Run script and cancel after predefined time

    Args:
        script: a python source code to be executed in a separate subprocess
        script_file: name of the script where script source will be saved
        cmd: command to execute. If None, it will be set to 'python3 -m {Path(script_file).stem}'
        cancel_after: number of seconds before sending SIGTERM signal

    Returns:
        A tuple containing exit code and combined stdout and stderr as a binary string
    """
    if script_file is None:
        script_file = "script.py"

    if cmd is None:
        cmd = f"python3 -m {Path(script_file).stem}"

    with TemporaryDirectory() as d:
        consumer_script = Path(d) / script_file

        with open(consumer_script, "w") as file:
            file.write(script)

        if generate_docs:
            logger.info(
                f"Generating docs for: {Path(script_file).stem}:{kafka_app_name}"
            )
            try:
                kafka_app: FastKafka = _import_from_string(
                    f"{Path(script_file).stem}:{kafka_app_name}"
                )
                await asyncer.asyncify(kafka_app.create_docs)()
            except Exception as e:
                logger.warning(
                    f"Generating docs failed for: {Path(script_file).stem}:{kafka_app_name}, ignoring it for now."
                )

        proc = subprocess.Popen(  # nosec: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
            shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=d
        )
        await asyncio.sleep(cancel_after)
        proc.terminate()
        output, _ = proc.communicate()

        return (proc.returncode, output)

# %% ../../nbs/002_Test_Utils.ipynb 17
async def display_docs(docs_path: str, port: int = 4000) -> None:
    with change_dir(docs_path):
        process = await asyncio.create_subprocess_exec(
            "python3",
            "-m",
            "http.server",
            f"{port}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            from google.colab.output import eval_js

            proxy = eval_js(f"google.colab.kernel.proxyPort({port})")
            logger.info("Google colab detected! Proxy adjusted.")
        except:
            proxy = f"http://localhost:{port}"
        finally:
            await asyncio.sleep(2)
            display(IFrame(f"{proxy}", 1000, 700))  # type: ignore
            await asyncio.sleep(2)
            await terminate_asyncio_process(process)