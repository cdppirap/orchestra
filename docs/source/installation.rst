============
Installation
============

To install `orchestra` you need to have the `docker` daemon installed. Make sure the current user
is added to the `docker` group with : 

.. code-block:: console

    $ sudo usermod -a -G docker <username>
    # run before launching orchestra
    $ newgrp docker

Clone the project from Github and you're done : 

.. code-block:: console

    $ git clone https://github.com/cdppirap/orchestra.git
