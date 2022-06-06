import re
from pathlib import Path

from setuptools import find_namespace_packages, setup  # type: ignore

about = (Path("async_commerce_coinbase") / "__about__.py").read_text()
version = re.search(r"__version__ = [\"']([\d.]+)[\"']", about).group(1)

setup(
    name="async_commerce_coinbase",
    version=version,
    url="https://github.com/cleaner-bot/async-commerce-coinbase",
    author="Leo Developer",
    author_email="git@leodev.xyz",
    description="async coinbase commerce api",
    install_requires=Path("requirements.txt").read_text().splitlines(),
    packages=find_namespace_packages(include=["async_commerce_coinbase*"]),
    package_data={"async_commerce_coinbase": ["py.typed"]},
)
