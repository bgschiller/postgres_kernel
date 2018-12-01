# A simple Jupyter kernel for PostgreSQL

Install with `pip install postgres_kernel`

To use, run one of:

```bash
jupyter notebook
# In the notebook interface, select PostgreSQL from the 'New' menu
jupyter qtconsole --kernel postgres
jupyter console --kernel postgres
```

## How to use:

There are a couple of specially formatted comments for controlling the connection string and autocommit mode.

```sql
-- connection: postgres://brian:password@localhost:5432/dbname
-- autocommit: true
-- (or false)
```

For details of how this works, see Jupyter's docs on [wrapper kernels](http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html).
This is heavily based on [takluyver/bash_kernel](https://github.com/takluyver/bash_kernel). Just look at our git log :)

![](images/console.png)

![](images/notebook.png)


Related
-------

- Catherine Devlin has an ipython magic that seems very full featured: [catherinedevlin/ipython-sql](https://github.com/catherinedevlin/ipython-sql)

- As noted, this is based on [takluyver/bash_kernel](https://github.com/takluyver/bash_kernel)
