from setuptools import setup


setup(
    name="gluster-tester",
    version="0.1",
    packages=["glustertester"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "gluster-tester = glustertester.main:main"
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Gluster Developers",
    author_email="gluster-devel@gluster.org",
    description="Gluster Testing tools",
    license="GPLv2",
    keywords="gluster, tool, tests",
    url="https://github.com/aravindavk/gluster-tester",
    long_description="""
    Gluster Testing tools
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
