import setuptools

# from automaps import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automaps",
    version="0.9.3",
    author="Roland Lukesch",
    author_email="roland.lukesch@its-viennaregion.at",
    description="Making maps with streamlit and QGIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/its-vienna-region/digilab/automatisierte-karten",
    install_requires=[
        "click>=8.0.4",
        "hypothesis>=6.43.3",
        "Jinja2>=3.1.1",
        "pandas>=1.4.2",
        "psycopg2>=2.9.3",
        "pytest>=7.1.1",
        "streamlit>=1.8.1",
        "SQLAlchemy>=1.4.35",
        "Pillow>=9.1.0",
        "pyzmq>=22.3.0",
    ],
    packages=setuptools.find_packages(),  # ["automaps", "automaps.client", "automaps.generators", "automaps.server", "automaps.scripts"],
    python_requires=">=3.8",
    package_data={"automaps": ["data/demo/*", "data/demo/.streamlit/*"]},
    entry_points="""
        [console_scripts]
        automaps=automaps.scripts.project:cli
    """,
)
