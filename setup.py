import setuptools

# from automaps import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automaps",
    version="0.9.1",
    author="Roland Lukesch",
    author_email="roland.lukesch@its-viennaregion.at",
    description="Making maps with streamlit and QGIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/its-vienna-region/digilab/automatisierte-karten",
    install_requires=[
        "Jinja2>=3.0.1",
        "pandas>=1.2.4",
        "psycopg2>=2.8.4",
        "streamlit>=0.80.0",
        "SQLAlchemy>=1.4.7",
        "Pillow>=8.3.1",
        "pyzmq>=22.0.3",
    ],
    packages=setuptools.find_packages(),  # ["automaps", "automaps.client", "automaps.generators", "automaps.server", "automaps.scripts"],
    python_requires=">=3.8",
    package_data={
        "automaps":
            ["data/demo/*",
             "data/demo/.streamlit/*"]
    },
    entry_points="""
        [console_scripts]
        automaps=automaps.scripts.project:cli
    """
)
