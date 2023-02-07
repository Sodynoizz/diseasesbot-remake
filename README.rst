DiseasesBot Project
====================
.. image:: https://discord.com/api/guilds/1021730173982347298/embed.png 
   :target: https://discord.gg/v5jBXfnX
   :alt: Discord server
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg?style=flat&logo=python&logoColor=white
   :width: 160
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/badge/Sodynoizz-ONLINE-success?style=flat&logo=discord
   :target: https://discord.com/channels/@me/884707218577063998
   :alt: My discord account

.. image:: /config/banner.jpg
   :alt: DiseasesBot banner
   
A bot which using Discord.py v2.0 library which is a modern, easy to use, feature-rich, and async ready API wrapper for Discord Written in Python to create about health information and others.

Installing
--------------------

**Python 3.8 or higher is required**

To install the Discord.py, you can just run the following command:

.. code:: sh

   # Linux/MacOS
   python3 -m pip install -U "discord.py"
   # Windows
   py -3 -m pip install -U discord.py

Otherwise to install all require libraries you should run the following command:

.. code:: sh

   # Linux/MacOS
   python3 -m pip install -r "requirements.txt"
   # Windows
   py -3 -m pip install -r requirements.txt

To clone my development project, do the following command:

.. code:: sh

   # Linux/MacOS
   $ git clone clone Sodynoizz/diseasesbot-remake
   $ python3 -m pip install -r requirements.txt
   # Windows
   $ git clone clone Sodynoizz/diseasesbot-remake
   $ py -3 -m pip install -r requirements.txt

Optional Packages
~~~~~~~~~~~~~~~~~

**These following packages are optional. They will support or speedup for the require packages.**

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice discord.py support for ``discord.py[voice]`` package)
* `aiodns <https://pypi.org/project/aiodns/>`__, `brotlipy <https://pypi.org/project/brotlipy/>`__, `cchardet <https://pypi.org/project/cchardet/>`__ (for aiohttp speedup)
* `orjson <https://pypi.org/project/orjson/>`__ (for json speedup)

Please note that while installing voice support on Linux, you must install the following packages via your preferred package manager (e.g. ``apt``, ``dnf``, etc) BEFORE running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.10-dev`` for Python 3.10)

Running your discord bot
--------------------

To run your bot, you should rename ``secret[config].py`` to ``secret.py``.
Then next, configure all variable in following table:

.. list-table::
   :header-rows: 1

   *  - Parameter Name
      - Description
   
   *  - ``database_name``
      - Provide your Postgresql's database name

   *  - ``database_password``
      - Provide your Postgresql's database password

   *  - ``database_user``
      - Provide your Postgresql's database user name
   
   *  - ``default_prefix``
      - Setup for your bot default prefix to use in prefixed-command
   
   *  - ``report_channel``
      - Provide server channel id to display report logs
   
   *  - ``contributor_id``
      - Provide contributor's id to gain access through discord permissions.

Parameter Notes
~~~~~~~~~~~~~~~~~
   * Do not change `covid_api` parameter value since it will make `covidstats` command crash.
   * The optional parameter is `initialize_extensions` paramter. You can able to ignore some cog files.

Example for optional parameter

.. code:: py

   # Default Parameter
   initial_extensions = ['cogs.error', 'cogs.health', 'cogs.report', 'cogs.moderation', 'cogs.utility']

   # You can change that 'initialize_extensions' value to:
   initial_extensions = ['cogs.error', 'cogs.report']

   # This will ignore 'cogs.moderation', 'cogs.health' and 'cogs.utility' files
   # So that the bot will run the others files left.

References
------------

- `Discord.py Documentation <https://docs.pycord.dev/en/master/index.html>`_
- `Official Discord.py Server <https://discord.gg/r3sSKJJ>`_
- `Discord API <https://discord.gg/discord-api>`_

Contributors
------------
- `Kiruchapas Thaworn <https://www.instagram.com/ozone_krp._/>`_
- `Chorasit Apilardmongkol <https://sodynoizz.github.io>`_
- `Pun Tresattayapan <https://www.instagram.com/puntre_is_bruh/>`_
- `Pattanasang Pinijpichitkul <https://www.instagram.com/ll_ph.pp_ll/>`_
- `Siraphop Klawplad <https://www.instagram.com/pskhaw_143/>`_  
