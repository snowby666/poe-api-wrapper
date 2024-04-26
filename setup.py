from setuptools import setup, find_packages
from pathlib import Path

base_path = Path(__file__).parent
long_description = (base_path / "README.md").read_text(encoding='utf-8')

VERSION = '1.4.1'
DESCRIPTION = 'A simple, lightweight and efficient API wrapper for Poe.com'
LONG_DESCRIPTION = '👾 A Python API wrapper for Poe.com. With this, you will have free access to ChatGPT, Claude, Llama, Gemini, Google-PaLM and more! 🚀'

setup(
    name="poe-api-wrapper",
    version=VERSION,
    author="snowby666",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=['cloudscraper', 'websocket-client',
                      'requests_toolbelt', 'loguru', 'rich==13.3.4', 'nest_asyncio'],
    extras_require={
        'async': ['httpx==0.24.0'],
        'proxy': ['ballyregan; python_version>="3.9"'],
        'tests': ['tox'],
    },
    keywords=['python', 'poe', 'quora', 'chatgpt', 'claude', 'poe-api', 'api'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent"
    ],
    url="https://github.com/snowby666/poe-api-wrapper",

    entry_points={
        "console_scripts": [
            "poe = poe_api_wrapper.cli:main",
        ],
    },
)
