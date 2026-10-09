.. _installation:

Installation
============

.. contents::
    :local:
    :depth: 1

Install from Conda
------------------

.. warning::

   TODO: Prepare Conda package.

Install from GitHub
-------------------

Check out code from the Duck GitHub repo and start the installation:

.. code-block:: console

   $ git clone https://github.com/cehbrecht/duck.git
   $ cd duck

Create Conda environment named `duck`:

.. code-block:: console

   $ conda env create -f environment.yml
   $ conda activate duck

Install Duck app:

.. code-block:: console

  $ pip install -e .
  OR
  make install

For development you can use this command:

.. code-block:: console

  $ pip install -e .[dev]
  OR
  $ make develop

Start Duck PyWPS service
------------------------

After successful installation you can start the service using the ``duck`` command-line.

.. code-block:: console

   $ duck --help # show help
   $ duck start  # start service with default configuration

   OR

   $ duck start --daemon # start service as daemon
   loading configuration
   forked process id: 42

The deployed WPS service is by default available on:

http://localhost:5000/wps?service=WPS&version=1.0.0&request=GetCapabilities.

.. NOTE:: Remember the process ID (PID) so you can stop the service with ``kill PID``.

You can find which process uses a given port using the following command (here for port 5000):

.. code-block:: console

   $ netstat -nlp | grep :5000


Check the log files for errors:

.. code-block:: console

   $ tail -f  pywps.log

... or do it the lazy way
+++++++++++++++++++++++++

You can also use the ``Makefile`` to start and stop the service:

.. code-block:: console

  $ make start
  $ make status
  $ tail -f pywps.log
  $ make stop


Run Duck as Docker container
----------------------------

You can also run Duck as a Docker container.

.. warning::

  TODO: Describe Docker container support.

Use Ansible to deploy Duck on your System
-----------------------------------------

Use the `Ansible playbook`_ for PyWPS to deploy Duck on your system.
The Linux x86_64 deployment environment is locked in ``linux-64.spec``, replacing
``spec-list.txt``. It includes the Conda runtime dependencies and the playbook's
Gunicorn, gevent, psycopg2 2.9.12, DRMAA 0.7.9, dill and test packages.

Set these inventory variables, including any service-specific overrides:

.. code-block:: yaml

   conda_env_use_spec: true
   conda_env_spec_file: linux-64.spec

Run a full environment deployment so the new packages are installed, rather than
only updating application code. To install manually on Linux x86_64:

.. code-block:: console

   $ conda create -n duck --file linux-64.spec
   $ conda activate duck
   $ python -m pip install .

PyWPS is installed by pip, along with the CRAI application and pretrained models,
through ``requirements.txt``. These packages are not in the Conda spec.
``environment.yml`` also installs PyWPS through its pip section. This avoids a
Conda GDAL/PROJ conflict between Python 3.10's geospatial builds and the playbook's
new PostgreSQL libraries; PyWPS's pip dependencies provide binary wheels instead.

The CRAI Git dependencies' upstream branches are not frozen by the spec. Both
currently require setuptools 59.5.0, so that pin is retained. Its Conda builds support Python
up to 3.10, which determines the Python version for this environment.

The environment uses Python 3.10, PyWPS 4.7 and CPU-only PyTorch 2.5 with
Torchvision 0.20. Duck explicitly selects CPU inference. The PyTorch upper bound
preserves the checkpoint-loading behavior used by CRAI. NumPy stays on 1.x.
For other platforms, use ``environment.yml`` before installing Duck with pip.

.. _Ansible playbook: http://ansible-wps-playbook.readthedocs.io/en/latest/index.html
