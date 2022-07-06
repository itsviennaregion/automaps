import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automaps",
    version="1.0.6dev",
    author="Roland Lukesch",
    author_email="roland.lukesch@its-viennaregion.at",
    description="Automatically generate customized and ready to print maps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itsviennaregion/automaps",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "click>=8.0.4,<8.1",  # <8.1 added for compatibility with streamlit 1.9
        "Jinja2>=3.1.1",
        "pandas>=1.4.2",
        "psycopg2-binary>=2.9.3",
        "streamlit>=1.8.1",
        "SQLAlchemy>=1.4.35",
        "Pillow>=9.1.0",
        "protobuf>=3.20,<4",  # <4 added for compatibility with streamlit 1.9
        "pyzmq>=22.3.0",
        "traitlets>=5",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    package_data={"automaps": ["data/demo/*", "data/demo/.streamlit/*"]},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        automaps=automaps.scripts.project:cli
    """,
)
