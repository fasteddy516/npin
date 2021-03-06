import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="rpi-npin",
    version="0.0.1",
    description="NeoPixel Indicator Library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/fasteddy516/npin",
    author="Edward Wright",
    author_email="fasteddy@thewrightspace.net",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["npin"],
    install_requires=[
        "Adafruit-Blinka",
        "adafruit-circuitpython-neopixel",
        "rpi-ws281x",
        "RPi.GPIO",
    ],
)
