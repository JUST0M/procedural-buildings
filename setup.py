import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="procedural-buildings",
    version="1.0.1",
    author="Tom Mason",
    author_email="tommasonuk@yahoo.co.uk",
    description="Tools for the procedural modelling of buildings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JUST0M/procedural-buildings",
    packages=setuptools.find_packages(),
    package_dir={'procedural_buildings': 'procedural_buildings'},
    package_data={'procedural_buildings': ['primitives/*.obj']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "sympy",
        "sly",
    ],
)
