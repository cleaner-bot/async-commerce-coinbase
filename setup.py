from setuptools import setup, find_namespace_packages  # type: ignore
from pathlib import Path

from async_commerce_coinbase import __version__

setup(
    name="async_commerce_coinbase",
    version=__version__,
    url="https://github.com/cleaner-bot/async-commerce-coinbase",
    author="Leo Developer",
    author_email="git@leodev.xyz",
    description="async coinbase commerce api",
    install_requires=Path("requirements.txt").read_text().splitlines(),
    packages=find_namespace_packages(include=["async_commerce_coinbase*"]),
    package_data={"async_commerce_coinbase": ["py.typed"]},
)
