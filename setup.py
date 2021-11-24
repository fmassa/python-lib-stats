from setuptools import setup, find_packages

setup(
    name="pylibstats",
    description="Find usage statistics (imports, function calls, attribute access) for Python code-bases",
    url="https://github.com/fmassa/python-lib-stats",
    version='0.0.1',
    author='Francisco Massa',
    author_email='fmassa@fb.com',
    license="BSD",
    python_requires=">=3.6",
    packages=find_packages(exclude=("tests",)),
)
