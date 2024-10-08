from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="automata-building-management",
    version="1.0.3",  # Incremented version number
    author="A. Jewell Sr",
    author_email="AutomataControls@Protonmail.com",
    description="Automata Building Management & HVAC Controller - Advanced IoT-driven solution for commercial and industrial applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutomataControls/AutomataBuildingManagment-HvacController",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pillow",       # For handling images
        "requests",     # For making HTTP requests (if applicable)
        "numpy",        # For numerical computations (optional, if applicable)
        "matplotlib",   # For any plotting or visualization needs (optional)
    ],
    include_package_data=True,
    py_modules=['run_automata_install'],  # Include the run_automata_install module
    scripts=[
        'AutomataControllerInstall.sh',
        'increase_swap_size.sh',
        'install_node_red.sh',
        'set_background.sh',
        'set_internet_time_rpi4.sh',
        'InstallNodeRedPallete.sh',
        'Uninstall.sh',
    ],
    data_files=[
        ('', ['README.md', 'LICENSE', 'splash.png', 'NodeRedlogo.png']),
    ],
    entry_points={
        'console_scripts': [
            'automata-install=run_automata_install:main',  # Updated entry point
        ],
    },
)
