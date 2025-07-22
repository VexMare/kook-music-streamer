from setuptools import setup, find_packages

setup(
    name='kook-music-streamer',  # 新包名
    version='0.1.0',
    description='A Python SDK for KOOK music streaming bot',
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='EDream',
    author_email='chixiaotao@foxmail.com',
    url='https://github.com/NightmaresNightmares/kook-music-streamer',
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)