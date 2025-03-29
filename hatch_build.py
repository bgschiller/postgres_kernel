from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):

    def initialize(self, version, build_data):
        print("Message from the custom build hook")
