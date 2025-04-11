from setuptools import find_packages, setup

setup(
    name="shared_helpers",
    version="0.4.0",
    packages=find_packages(where="shared_helpers"),
    package_dir={"": "shared_helpers"},
    include_package_data=True,
    python_requires=">=3.12",
)
