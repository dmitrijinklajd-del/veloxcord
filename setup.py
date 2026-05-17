from setuptools import setup, find_packages

setup(
    name="veloxcord",
    version="1.0.0",
    description="A production-ready async Discord API wrapper for Python",
    author="VeloxCord Contributors",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=["aiohttp>=3.9.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
)
