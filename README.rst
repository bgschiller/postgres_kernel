A simple Jupyter kernel for PostgreSQL

I don't know how to set this up to be pip-installable, but maybe you can help with that?

To use, run one of:

.. code:: shell

    jupyter notebook
    # In the notebook interface, select PostgreSQL from the 'New' menu
    jupyter qtconsole --kernel postgres
    jupyter console --kernel postgres

For details of how this works, see Jupyter's docs on `wrapper kernels
<http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html>`_.
This is heavily based on `takluyver/bash_kernel
<https://github.com/takluyver/bash_kernel>`_. Just look at our git log :)

.. image:: images/console.png

.. image:: images/notebook.png

Todo
----

- Get rid of this ShimWarning, "You should import from ipykernel or jupyter_client instead."
- How do I make this pip-installable?

Related
-------

- Catherine Devlin has an ipython magic that seems very full featured: `catherinedevlin/ipython-sql <https://github.com/catherinedevlin/ipython-sql>`_

- As noted, this is based on `takluyver/bash_kernel <https://github.com/takluyver/bash_kernel>`_
