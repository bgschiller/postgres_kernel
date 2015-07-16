A simple IPython kernel for PostgreSQL

This requires IPython 3.

To use it, install with ``pip install postgres_kernel``, and then run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select PostgreSQL from the 'New' menu
    ipython qtconsole --kernel postgres
    ipython console --kernel postgres

For details of how this works, see IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_, and
Pexpect's docs on the `replwrap module
<http://pexpect.readthedocs.org/en/latest/api/replwrap.html>`_

This is heavily based on `takluyver/bash_kernel
<https://github.com/takluyver/bash_kernel>`_. Just look at our git log :)
