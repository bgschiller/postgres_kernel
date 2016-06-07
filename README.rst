A simple Jupyter kernel for PostgreSQL

This requires IPython 3.

To use it, install with ``pip install postgres_kernel``, and then run one of:

.. code:: shell

    jupyter notebook
    # In the notebook interface, select PostgreSQL from the 'New' menu
    jupyter qtconsole --kernel postgres
    jupyter console --kernel postgres

For details of how this works, see Jupyter's docs on `wrapper kernels
<http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html>`_.
This is heavily based on `takluyver/bash_kernel
<https://github.com/takluyver/bash_kernel>`_. Just look at our git log :)
