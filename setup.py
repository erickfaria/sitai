from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="sitai",
    version="0.1.0",
    author="Grupo de Pesquisa Arqueológica da Amazônia",
    author_email="email@example.com",
    description="Sistema de Catalogação de Escavações Arqueológicas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/sitai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sitai=sitai.app:main",
        ],
    },
)
