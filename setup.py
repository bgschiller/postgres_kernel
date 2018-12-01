from setuptools import setup
from setuptools.command.install import install
import json
import os
import sys

kernel_json = {
    "argv": [sys.executable, "-m", "postgres_kernel", "-f", "{connection_file}"],
    "display_name": "PostgreSQL",
    "language": "sql",
    "codemirror_mode": "sql"
}


class install_with_kernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        from jupyter_client.kernelspec import KernelSpecManager
        from tempfile import TemporaryDirectory
        kernel_spec = KernelSpecManager()
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            # TODO: Copy resources once they're specified

            kernel_spec.install_kernel_spec(td, 'postgres', user=self.user)

with open('README.rst') as f:
    readme = f.read()

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='postgres_kernel',
      version='0.2',
      description='A PostgreSQL kernel for IPython',
      long_description=readme,
      author='Brian Schiller',
      author_email='bgschiller@gmail.com',
      url='https://github.com/bgschiller/postgres_kernel',
      packages=['postgres_kernel'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['psycopg2>=2.6', 'tabulate>=0.7.5', 'jupyter-client'],
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Shells',
      ])
