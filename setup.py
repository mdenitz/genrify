import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="genrify",                     # This is the name of the package
    version="0.0.1",                        # The initial release version
    author="Matthew Denitz",                     # Full name of the author
    description="Tool to apply genre metadata to mp3 files",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["genrify"],             # Name of the python package
    package_dir={'':'genrify/src'},     # Directory of the source code of the package
    install_requires=['spotipy','music_tag']                     # Install other dependencies if any
)
