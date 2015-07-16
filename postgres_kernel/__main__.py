from IPython.kernel.zmq.kernelapp import IPKernelApp
from .kernel import PostgresKernel
IPKernelApp.launch_instance(kernel_class=PostgresKernel)
