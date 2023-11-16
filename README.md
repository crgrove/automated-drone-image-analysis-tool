Automated Drone Image Analysis Tool
=============================

The Automated Drone Image Analysis Tool (ADIAT) provides a platform through with algorithm can be used to programmatically identify areas of interest in a set of image  The primary use case for this tool is to aid in the analysis of images taken by UAVs during Search and Rescue Operations.

This tool was developed by Texas Search and Rescue (TEXSAR) as an open source project for the SAR community.

For more information about this project or to download the Windows Installer, please visit: https://www.texsar.org/automated-drone-image-analysis-tool/

Features
--------

- Leverages Color Detection capabilities provided by OpenCV (https://opencv.org/)
- UI build on QT_ Framework (https://www.qt.io/)
 

Getting started
---------------

First of all make sure you have pipenv installed and then initialize a
working development environment like this

    pipenv install --dev

Once all dependencies are installed, you should enter the environment shell like
this::

    pipenv shell

Once done, you can run the application
like this::

    python app

UI Resources
--------------------------

In order to ease the development process, the Qt Creator project ``app.pro`` is
provided. You can open it to edit the UI files or to manage resources.
UI files and resources can be built like this

    python setup.py build_res

Note that this command is automatically run before running ``sdist`` and
``bdist_app`` commands.

Compiled application
--------------------

You can generate a *compiled* application so that end-users do not need to
install anything. You can tweak some settings on the ``app.spec`` file. It can
be generated like this

    python setup.py bdist_app
    
 User Contributions
--------------------

If you are interesting in contributing to this project by either enhancing an existing capability or adding new features/algorithms please reach out to us at charlie.grove@texsar.org
