from cleo.commands.command import Command
from poetry.plugins.application_plugin import ApplicationPlugin
from open_sustain_tech.__main__ import OSSOptionParser

class OpenSustainTech(Command):
    name = "oss-opt"
    
    def handle(self) -> int:
        # self.line("Open Sustain Tech")
        readme_content = OSSOptionParser()
        readme_file = self.input.get_arguments() # Get the command-line arguments
        readme_content.parse(readme_file)
        return 0
    
def factory():
    return OpenSustainTech()

class OSSOptionPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory("oss-opt", factory)
        
    @property
    def commands(self):
        return [factory()]