# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/097_Docs_Dependencies.ipynb.

# %% auto 0
__all__ = ['logger', 'npm_required_major_version', 'node_version', 'node_fname_suffix', 'node_fname', 'node_fname_extension',
           'node_url', 'local_path', 'tgz_path', 'node_path']

# %% ../../nbs/097_Docs_Dependencies.ipynb 2
import asyncio
import os
import platform
import shutil
import subprocess  # nosec Issue: [B404:blacklist]
import tarfile
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from .helpers import in_notebook
from .logger import get_logger

if in_notebook():
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

# %% ../../nbs/097_Docs_Dependencies.ipynb 4
logger = get_logger(__name__)

# %% ../../nbs/097_Docs_Dependencies.ipynb 5
npm_required_major_version = 9


def _check_npm(required_major_version: int = npm_required_major_version) -> None:
    """
    Check if npm is installed and its major version is compatible with the required version.

    Args:
        required_major_version: Required major version of npm. Defaults to 9.

    Raises:
        RuntimeError: If npm is not found or its major version is lower than the required version.
    """
    if shutil.which("npm") is not None:
        cmd = "npm --version"
        proc = subprocess.run(  # nosec [B602:subprocess_popen_with_shell_equals_true]
            cmd,
            shell=True,
            check=True,
            capture_output=True,
        )
        major_version = int(proc.stdout.decode("UTF-8").split(".")[0])
        if major_version < required_major_version:
            raise RuntimeError(
                f"Found installed npm major version: {major_version}, required npx major version: {required_major_version}. To use documentation features of FastKafka, please update npm"
            )
    else:
        raise RuntimeError(
            f"npm not found, to use documentation generation features of FastKafka, you must have npm >= {required_major_version} installed"
        )

# %% ../../nbs/097_Docs_Dependencies.ipynb 10
node_version = "v18.15.0"
node_fname_suffix = "win-x64" if platform.system() == "Windows" else "linux-x64"
node_fname = f"node-{node_version}-{node_fname_suffix}"
node_fname_extension = ".zip" if platform.system() == "Windows" else ".tar.xz"
node_url = f"https://nodejs.org/dist/{node_version}/{node_fname}{node_fname_extension}"
local_path = (
    Path(os.path.expanduser("~")).parent / "Public"
    if platform.system() == "Windows"
    else Path(os.path.expanduser("~")) / ".local"
)
tgz_path = local_path / f"{node_fname}{node_fname_extension}"
node_path = local_path / f"{node_fname}"


def _check_npm_with_local(node_path: Path = node_path) -> None:
    """
    Check if npm is installed and its major version is compatible with the required version.
    If npm is not found but a local installation of NodeJS is available, add the NodeJS binary path to the system's PATH environment variable.

    Args:
        node_path: Path to the local installation of NodeJS. Defaults to node_path.

    Raises:
        RuntimeError: If npm is not found and a local installation of NodeJS is not available.
    """
    try:
        _check_npm()
    except RuntimeError as e:
        if (node_path).exists():
            logger.info("Found local installation of NodeJS.")
            node_binary_path = (
                f";{node_path}"
                if platform.system() == "Windows"
                else f":{node_path / 'bin'}"
            )
            os.environ["PATH"] = os.environ["PATH"] + node_binary_path
            _check_npm()
        else:
            raise e

# %% ../../nbs/097_Docs_Dependencies.ipynb 13
def _install_node(
    *,
    node_url: str = node_url,
    local_path: Path = local_path,
    tgz_path: Path = tgz_path,
) -> None:
    """
    Install NodeJS by downloading the NodeJS distribution archive, extracting it, and adding the NodeJS binary path to the system's PATH environment variable.

    Args:
        node_url: URL of the NodeJS distribution archive to download. Defaults to node_url.
        local_path: Path to store the downloaded distribution archive. Defaults to local_path.
        tgz_path: Path of the downloaded distribution archive. Defaults to tgz_path.
    """
    try:
        import requests
    except Exception as e:
        msg = "Please install docs version of fastkafka using 'pip install fastkafka[docs]' command"
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info("Installing NodeJS...")
    local_path.mkdir(exist_ok=True, parents=True)
    response = requests.get(
        node_url,
        stream=True,
        timeout=60,
    )
    try:
        total = response.raw.length_remaining // 128
    except Exception:
        total = None

    with open(tgz_path, "wb") as f:
        for data in tqdm(response.iter_content(chunk_size=128), total=total):
            f.write(data)

    if platform.system() == "Windows":
        with zipfile.ZipFile(tgz_path, "r") as zip_ref:
            zip_ref.extractall(
                local_path
            )  # nosec: B202 tarfile_unsafe_members - tarfile.extractall used without any validation. Please check and discard dangerous members.
    else:
        with tarfile.open(tgz_path) as tar:
            for tarinfo in tar:
                tar.extract(tarinfo, local_path)

    os.environ["PATH"] = (
        os.environ["PATH"] + f";{node_path}"
        if platform.system() == "Windows"
        else f":{node_path}/bin"
    )
    logger.info(f"Node installed in {node_path}.")

# %% ../../nbs/097_Docs_Dependencies.ipynb 16
async def _install_docs_npm_deps() -> None:
    """
    Install the required npm dependencies for generating the documentation using AsyncAPI generator.
    """
    with TemporaryDirectory() as d:
        cmd = (
            "npx -y -p @asyncapi/generator ag https://raw.githubusercontent.com/asyncapi/asyncapi/master/examples/simple.yml @asyncapi/html-template -o "
            + d
        )

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            logger.info("AsyncAPI generator installed")
        else:
            logger.error("AsyncAPI generator NOT installed!")
            logger.info(
                f"stdout of '$ {cmd}'{stdout.decode('UTF-8')} \n return_code={proc.returncode}"
            )
            logger.info(
                f"stderr of '$ {cmd}'{stderr.decode('UTF-8')} \n return_code={proc.returncode}"
            )
            raise ValueError(
                f"""AsyncAPI generator NOT installed, used '$ {cmd}'
----------------------------------------
stdout:
{stdout.decode("UTF-8")}
----------------------------------------
stderr:
{stderr.decode("UTF-8")}
----------------------------------------
return_code={proc.returncode}"""
            )