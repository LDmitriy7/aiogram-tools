from setuptools import setup

setup(
    packages=['aiogram_tools'],
    python_requires='>=3.9',
    setup_requires=['pbr'], pbr=True,

    install_requires=[
        'aiogram>=2.11.2',
    ],
)
