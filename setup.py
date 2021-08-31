import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automaps",
    version="0.2",
    author="Roland Lukesch",
    author_email="roland.lukesch@its-viennaregion.at",
    description="Making map with streamlit and QGIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/its-vienna-region/digilab/automatisierte-karten",
    install_requires=[
        "Jinja2>=3.0.1",
        "pandas>=1.2.4",
        "psycopg2>=2.8.4",
        "streamlit>=0.80.0",
        "SQLAlchemy>=1.4.7",
        "pyzmq>=22.0.3",
    ],
    packages=["automaps", "automaps.client", "automaps.generators", "automaps.server"],
    python_requires=">=3.8",
)
