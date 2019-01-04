from setuptools import setup, find_packages

VERSION = "0.1.0"

INSTALL_REQUIREMENTS = ["ruamel.yaml",
                        "jupyter", 'pyparsing', 'ipywidgets', 'traitlets'
                        ]

CLASSIFIERS = ["Programming Language :: Python :: 3",
               "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
               "Operating System :: OS Independent",
               "Development Status :: 2 - Pre-Alpha",
               "Intended Audience :: Developers",
               "Intended Audience :: Science/Research",
               "Topic :: Scientific/Engineering",
               ]

TEAM = "Daniel Rose"

with open("README.md", "r") as fh:
    DESCRIPTION = fh.read()

setup(name='knowviz',
      version=VERSION,
      description='Knowledge visualization tool for quantities and models that connect quantities.',
      long_description=DESCRIPTION,
      author=TEAM,
      author_email='drose@cbs.mpg.de',
      license='GPL v3',
      packages=find_packages(),
      zip_safe=False,
      python_requires='>=3.6',
      install_requires=INSTALL_REQUIREMENTS,
      classifiers=CLASSIFIERS)
