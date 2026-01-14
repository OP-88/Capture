from setuptools import setup, find_packages

setup(
    name="capture",
    version="1.0.5",
    packages=find_packages(),
    scripts=["run.py"],
    install_requires=[
        "PyQt6>=6.6.0",
        "PyQt6-Qt6>=6.6.0",
        "opencv-python-headless>=4.8.0",
        "Pillow>=10.1.0",
        "SQLAlchemy>=2.0.23",
        "pytesseract>=0.3.10",
        "python-magic>=0.4.27",
        "python-dateutil>=2.8.2",
    ],
)
