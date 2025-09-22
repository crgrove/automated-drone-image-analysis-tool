#!/usr/bin/env python

import re
import os
from subprocess import check_call

from setuptools import setup, find_packages, Command
from setuptools.command.sdist import sdist


cmdclass = {}


# PySide6 build tools
import json
import glob
import subprocess
from pathlib import Path

has_build_ui = True


with open('app/__init__.py') as f:
    _version = re.search(r'__version__\s+=\s+\'(.*)\'', f.read()).group(1)


if has_build_ui:
    class build_res(Command):
        """Build UI and resources using PySide6 tools."""

        description = 'Build UI and resources'
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            # Load configuration from pyuic.json
            with open('pyuic.json', 'r') as f:
                config = json.load(f)
            
            # Process UI files
            for file_pattern, output_dir in config['files']:
                if file_pattern.endswith('.ui'):
                    # Convert UI files to Python
                    ui_files = glob.glob(file_pattern)
                    for ui_file in ui_files:
                        self.convert_ui_file(ui_file, output_dir)
                elif file_pattern.endswith('.qrc'):
                    # Convert QRC files to Python
                    qrc_files = glob.glob(file_pattern)
                    for qrc_file in qrc_files:
                        self.convert_qrc_file(qrc_file, output_dir)

        def convert_ui_file(self, ui_file, output_dir):
            """Convert a UI file to Python using pyside6-uic."""
            try:
                # Ensure output directory exists
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Generate output filename
                ui_name = Path(ui_file).stem
                output_file = Path(output_dir) / f"{ui_name}_ui.py"
                
                # Run pyside6-uic
                cmd = [
                    'pyside6-uic',
                    '--from-imports',
                    ui_file,
                    '-o',
                    str(output_file)
                ]
                
                print(f"Converting {ui_file} -> {output_file}")
                subprocess.run(cmd, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Error converting {ui_file}: {e}")
            except Exception as e:
                print(f"Error processing {ui_file}: {e}")

        def convert_qrc_file(self, qrc_file, output_dir):
            """Convert a QRC file to Python using pyside6-rcc."""
            try:
                # Ensure output directory exists
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Generate output filename
                qrc_name = Path(qrc_file).stem
                output_file = Path(output_dir) / f"{qrc_name}_rc.py"
                
                # Run pyside6-rcc
                cmd = [
                    'pyside6-rcc',
                    qrc_file,
                    '-o',
                    str(output_file)
                ]
                
                print(f"Converting {qrc_file} -> {output_file}")
                subprocess.run(cmd, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Error converting {qrc_file}: {e}")
            except Exception as e:
                print(f"Error processing {qrc_file}: {e}")

    cmdclass['build_res'] = build_res


class custom_sdist(sdist):
    """Custom sdist command."""

    def run(self):
        self.run_command('build_res')
        sdist.run(self)


cmdclass['sdist'] = custom_sdist


class bdist_app(Command):
    """Custom command to build the application. """

    description = 'Build the application'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if has_build_ui:
            self.run_command('build_res')
        else:
            print("Warning: pyqt-distutils not found, skipping UI resource build")
        check_call(['pyinstaller', '-y', 'app.spec'])


cmdclass['bdist_app'] = bdist_app


setup(name='app',
      version=_version,
      packages=find_packages(),
      description='Automated Drone Image Analysis Tool',
      author='Charlie Grove',
      author_email='charlie.grove@texsar.org',
      license=' AGPL-3.0',
      url='https://www.texsar.org',
      entry_points={
          'gui_scripts': ['app=app.__main__:main'],
      },
      cmdclass=cmdclass)
