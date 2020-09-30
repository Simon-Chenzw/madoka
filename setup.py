from setuptools import setup, find_packages

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(
    # package
    name="madoka",
    version="1.0.0",
    packages=find_packages(),
    entry_points={},
    # requires
    python_requires='>=3.8',
    install_requires=[
        'rich>=7.0',
        'aiohttp>=3.6',
        'websockets>=8.0',
        'requests>=2.18',
    ],
    # description
    description="A bot framework based on mirai-api-http",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU Lesser General Public License v3 (LGPLv3)",
    classifiers=[],
    # about
    author="Simon_Chen",
    author_email="1020359403@qq.com",
    url="https://github.com/Simon-Chenzw/madoka",
)
