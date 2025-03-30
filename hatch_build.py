import shutil
from pathlib import Path
from ipykernel.kernelspec import make_ipkernel_cmd, write_kernel_spec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):

    def initialize(self, version, build_data):
        dest = Path(__file__).parent.resolve() / "data_kernelspec"
        overrides = {
            "argv": make_ipkernel_cmd(mod='postgres_kernel')
        }

        if dest.exists():
            shutil.rmtree(dest)

        write_kernel_spec(dest, overrides=overrides)
