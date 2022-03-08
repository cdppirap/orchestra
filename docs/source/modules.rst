=======
Modules
=======

Module registration
-------------------
Register a module with : 

.. code-block:: console

    $ python -m orchestra --register <path/to/module/directory>
    # or
    $ python -m orchestra --register <http://github_project_url>

List modules
------------
List installed modules : 

.. code-block:: console

    $ python -m orchestra --list

Remove modules
--------------

.. code-block:: console

    $ python -m orchestra --remove <module_id> ... <module_id_n>
    # clear all with
    $ python -m orchestra --clear
