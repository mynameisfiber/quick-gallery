from setuptools import setup, find_packages  # type: ignore

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="quick-gallery",
    version="0.1.0",
    author="Micha Gorelick",
    author_email="mynameisfiber@gmail.com",
    url="https://github.com/mynameisfiber/quick-gallery/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        "dev": [
            "flake8",
            "black",
            "isort",
            "pyright",
            "bump2version",
        ]
    },
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "quick-gallery = quick_gallery.cli:main",
        ],
    },
)

