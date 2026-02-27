from setuptools import setup, find_packages

setup(
    name="smart-download-organizer",
    version="1.0.0",
    description="Automatically organize your Downloads folder with a modern GUI",
    author="Francisco Cardoso",
    author_email="francisco.cardoso19@hotmail.com",
    url="https://github.com/frakzzPUC/SmartDownloadOrganizer",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "watchdog>=3.0.0",
        "customtkinter>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "smart-organizer=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment :: File Managers",
        "Topic :: Utilities",
    ],
)
