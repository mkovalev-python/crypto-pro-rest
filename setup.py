# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

p_version = "1.0.2"

with open("README.md") as f:
    long_description = f.read()

setup(
    name="crypto-pro-rest",
    version=p_version,
    author="Kovalev Maxim",
    author_email="mkovalevhse@yandex.ru",
    packages=find_packages(),
    url="https://github.com/mkovalev-python/crypto-pro-rest",
    download_url="https://github.com/mkovalev-python/crypto-pro-rest/tarball/v{0}".format(
        p_version
    ),
    license="GPL v3",
    description="A simple client/tool for Let's Encrypt or any ACME server that issues SSL certificates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "crypto-pro"
    ],
    install_requires=[
        "certifi==2021.5.30",
        "charset-normalizer==2.0.4",
        "idna==3.2",
        "requests==2.26.0",
        "urllib3==1.26.6"
    ],
)