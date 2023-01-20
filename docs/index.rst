|Code style: black|

.. figure:: https://github.com/nutanix/calm-dsl/workflows/Setup%20&%20build%20calm-dsl/badge.svg
   :alt: Build

   Build

calm-dsl
========

NCM Self-Service
----------------

Calm orchestrates and automates the provisioning of app-centric IT
infrastructure resources for hybrid and multi-cloud environments. End
users can self-service IT resources from pre-configured blueprints,
which IT administrators govern with user access, cost controls, and
security. Calm Marketplace transforms complex provisioning tickets into
a simple 1-click request and connects with most ITSM tools for
provisioning and automation tasks.

About Calm DSL
--------------

Calm DSL describes a simpler Python3 based DSL for writing Calm
blueprints. As Calm uses Services, Packages, Substrates, Deployments and
Application Profiles as building blocks for a Blueprint, these entities
can be defined as python classes. Their attributes can be specified as
class attributes and actions on those entities (procedural runbooks) can
be defined neatly as class methods. Calm blueprint DSL can also accept
appropriate native data formats such as YAML and JSON, allowing the
reuse and leveraging that work into the larger application lifecycle
context of a Calm blueprint.

Why Python3 as DSL ?
~~~~~~~~~~~~~~~~~~~~

Language design is black art, and building upon a well-established
language is design-wise a big win. The language has also solved many
issues like scoping, modules, if-else, inheritance, etc. Well
established languages have great tooling support: IDEs, syntax checkers,
third-party modules, coding practices, better readability, editing,
syntax highlighting, code completion, versioning, collaboration, etc.
They see much more community improvements as well. Python specifically
comes with a very good REPL (read–eval–print-loop). Having an
interactive prompt to play around and slowly build objects is an
order-of-magnitude improvement in developer productivity. Python is very
easy language to learn and use; and most of the ITOps/DevOps community
already use Python for scripting.

Dev Setup
---------

MacOS: - Install
`Xcode <https://apps.apple.com/us/app/xcode/id497799835>`__ - Install
homebrew:
``/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"``.
- Install python3, git and openssl:
``brew install git python3 openssl``. - Install virtualenv:
``pip install virtualenv`` - Add path to flags:
``export LDFLAGS="-L$(brew --prefix openssl)/lib"`` &
``export CFLAGS="-I$(brew --prefix openssl)/include"``. - Clone this
repo and run: ``make dev`` from top directory. - Getting into
virtualenv: ``source venv/bin/activate``. - Getting out of virtualenv:
``deactivate``.

Centos: - ``make _init_centos`` to setup your CentOS 7 VM for
development. This will install python3 and docker.

Use: - ``make dev`` to create/use python3 virtualenv in ``$TOPDIR/venv``
and setup dev environment. Activate it by calling
``source venv/bin/activate``. Use ``deactivate`` to deactivate
virtualenv. - ``make test`` to run quick tests. ``make test-all`` to run
all tests. - ``make dist`` to generate a ``calm.dsl`` python
distribution. - ``make docker`` to build docker container. (Assumes
docker client is setup on your machine) - ``make run`` to run container.
- ``make clean`` to reset.

Initializing Calm DSL
---------------------

From the top directory, run the command ``calm init dsl``. Enter the
following details, - Prism Central IP - Port (Hit Enter to select the
default value - 9440) - Username (Hit Enter to select the default value
- admin) - Password - Projects (Hit Enter to select the default value -
default)

Once ``calm init dsl`` command is run, you can check the status of the
server by running ``calm get server status``. Check if Calm is enabled
and Calm version is >=2.9.7

Docker
------

-  Latest image: ``docker pull ntnx/calm-dsl``
-  Run: ``docker run -it ntnx/calm-dsl``

Calm DSL Context
----------------

Context info includes server, project and log configuration for dsl
operations. - Flow: Context info is taken from config file passed inline
with cli command or environment data or default config file stored
mentioned in ``~/.calm/init.ini``. - Environment variables for server
configuration: ``CALM_DSL_PC_IP``, ``CALM_DSL_PC_PORT``,
``CALM_DSL_PC_USERNAME``, ``CALM_DSL_PC_PASSWORD``. - Environment
variable for project configuration: ``CALM_DSL_DEFAULT_PROJECT``. -
Environment variable for log configuration: ``CALM_DSL_LOG_LEVEL``. -
Environment variables for init configuration:
``CALM_DSL_CONFIG_FILE_LOCATION``, ``CALM_DSL_LOCAL_DIR_LOCATION``,
``CALM_DSL_DB_LOCATION``. - Config file parameter:
``calm --config/-c <config_file_location> ...`` - Show config in
context: ``calm show config``.

Getting Started for Developers
------------------------------

-  `Blueprints <docs/Blueprints>`__
-  `Applications <docs/Application>`__
-  `Brownfield Application <#>`__
-  `Runbooks <#>`__
-  `Task Library <#>`__
-  `Decompiling blueprints (.json -> .py) <#>`__

Getting started for Admins
--------------------------

-  `Roles <#>`__
-  `Directory Services <#>`__
-  `Users <#>`__
-  `User-groups <#>`__
-  `Projects <#>`__
-  `Environments <#>`__
-  `Access Control Policies <#>`__

Documentation
-------------

-  `Calm Terminology <docs/01-Calm-Terminology/>`__
-  `DSL Blueprint Architecture <docs/02-DSL-Blueprint-Architecture/>`__
-  `DSL Lab <docs/03-Quickstart/>`__

Video Links
-----------

-  `Workstation Setup <https://youtu.be/uIZmHQhioZg>`__
-  `Blueprint & App management <https://youtu.be/jb-ZllhaROs>`__
-  `Calm DSL Blueprint Architecture <https://youtu.be/Y-6eq91rtSw>`__

`Blogs <https://www.nutanix.dev/calm-dsl/>`__
---------------------------------------------

-  `Introducing the Nutanix Calm
   DSL <https://www.nutanix.dev/2020/03/17/introducing-the-nutanix-calm-dsl/>`__
-  `Creating Custom
   Blueprint <https://www.nutanix.dev/2020/03/30/nutanix-calm-dsl-creating-custom-blueprint/>`__
-  `Generating VM
   Specs <https://www.nutanix.dev/2020/04/06/nutanix-calm-dsl-generating-vm-specs/>`__
-  `Run Custom
   Actions <https://www.nutanix.dev/2020/04/17/nutanix-calm-dsl-run-custom-actions/>`__
-  `Remote Container Development (Part
   1) <https://www.nutanix.dev/2020/04/24/nutanix-calm-dsl-remote-container-development-part-1/>`__
-  `From UI to Code – Calm DSL and Blueprint
   Decompile <https://www.nutanix.dev/2020/07/20/from-ui-to-code-calm-dsl-and-blueprint-decompile/>`__

Demos
-----

-  `Zero-touch CI/CD - VDI Template Creation with Nutanix Calm
   DSL <https://youtu.be/5k_K7idGxsI>`__
-  `Integrating with Azure DevOps CI/CD
   pipeline <https://youtu.be/496bvlIi4pk>`__

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
