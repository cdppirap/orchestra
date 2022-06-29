====
REST
====

Start the REST server : 

.. code-block:: console

    $ python -m orchestra.rest

The configuration can be found in the `orchestra.configuration` module, of particular interest are 
the `rest_host` and `rest_port` values.

Endpoints
---------

List of endpoints exposed by the REST API : 

- `/modules` : retrieve a list of modules and assiciated metadata
- `/modules/<int:module_id>` : specific module metadata
- `/modules/<int:module_id>/run [args]` : request executing specified model with arguments supplied by user
- `/tasks` : retrieve list of tasks and associated metadata
- `/tasks/<int:task_id>` : specific task metadata (status, errors, output, ...)
- `/tasks/<int:task_id>/output` : download task output
- `/tasks/<int:task_id>/kill` : kill task


