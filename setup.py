import sys
import os
import setuptools

assert sys.version_info >= (3, 5, 0)

current_path = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(current_path)

with open("README.rst", "r") as fh:
    long_description = fh.read()

files = [os.path.join('fonts', item) for item in os.listdir('tkinter_fonts_viewer/fonts') if item.endswith('.json')]

setuptools.setup(
    name='tkinter_fonts_viewer',
    version='0.1.2',
    keywords="tkinter fonts font viewer",
    author="streanger",
    author_email="divisionexe@gmail.com",
    description="gui viewer for tkinter fonts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/streanger/tkinter-fonts-viewer",
    packages=['tkinter_fonts_viewer',],
    python_requires=">=3.5",
    license='MIT',
    install_requires=[''],
    include_package_data=True,
    package_data={
        'tkinter_fonts_viewer': files,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "fonts_viewer=tkinter_fonts_viewer:viewer",
        ]
    },
)
