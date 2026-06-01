"""
Setup script for TaskPilot-CLI
"""

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="taskpilot-cli",
    version="1.0.0",
    author="TaskPilot Team",
    author_email="hello@taskpilot.dev",
    description="🎯 Lightweight Terminal AI Task Management Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/TaskPilot-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Productivity :: Task Management",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "taskpilot=taskpilot.__main__:main",
            "tp=taskpilot.__main__:main",
        ],
    },
    keywords=[
        "task management",
        "pomodoro",
        "productivity",
        "cli",
        "terminal",
        "ai",
        "todo",
        "time tracking",
    ],
    project_urls={
        "Bug Reports": "https://github.com/gitstq/TaskPilot-CLI/issues",
        "Source": "https://github.com/gitstq/TaskPilot-CLI",
        "Documentation": "https://github.com/gitstq/TaskPilot-CLI#readme",
    },
)
