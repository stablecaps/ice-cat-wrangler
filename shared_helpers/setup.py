from setuptools import find_packages, setup

setup(
    name="shared_helpers",
    version="0.3.0",
    packages=find_packages(where="shared_helpers"),
    package_dir={"": "shared_helpers"},
    include_package_data=True,
    python_requires=">=3.12",
)

# from setuptools import find_packages, setup

# setup(
#     name="shared_helpers",
#     version="0.3.0",
#     packages=find_packages(),
#     install_requires=[
#         "boto3>=1.20.0",
#     ],
#     description="Shared helper functions for ice-cat-wrangler",
#     author="Darkpandarts",
#     author_email="14529342+darkpandarts@users.noreply.github.com",
# )
