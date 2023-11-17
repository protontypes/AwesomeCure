"""A Poetry Plugin for an application that uses the `open_sustain_tech` library."""

from dataclasses import dataclass, field
from typing import List
import __future__
import base64
import urllib
from urllib.parse import urlparse
from open_sustain_tech.awesomecure import awesome2py

import yaml
import simple_parsing
from simple_parsing import ArgumentParser
from simple_parsing.helpers import list_field

from cleo.commands.command import Command
from cleo.events.console_events import COMMAND
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from github import Github, StatsContributor
from os import getenv, path
from dotenv import load_dotenv
from poetry.console.application import Application
from poetry.console.commands.env_command import EnvCommand
from poetry.plugins.application_plugin import ApplicationPlugin
from open_sustain_tech.__main__ import OSSOptionParser
from open_sustain_tech.config import OSSOptionParserConfig

@dataclass
class OpenSustainTech(Command):
    """
    The `OpenSustainTech()` class is a subclass of the `Command()` class from the `cleo` library.
    It has a `handle()` method that is used to handle the command when the user executes it.
    The `factory()` function is a simple function that creates and returns an instance of the 
    `OpenSustainTech()` class.
    This function is used as a "factory" for creating `OpenSustainTech()` instances.
    """
    name = "open_sustain_tech"
    
    def configure(self):
        self.cfg = OSSOptionParserConfig()
    
    def handle(self) -> int:
        config_path = self.option("cfg")
        
        # Load the configuration from the YAML file
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
            
        # Use the configuration values
        cfg = simple_parsing.parse(config_class=OSSOptionParserConfig, args=args, add_config_path_arg=True)
        print(f"Parsing {cfg.readme_file} with {cfg.workers} workers ...")
        
        # self.line("Open Sustain Tech")
        readme_content = OSSOptionParser()
        readme_file = self.option("readme_file")
        readme_content.parse(readme_file)
        return 0
    
def factory():
    return OpenSustainTech()

@dataclass
class Options:
    """The `Options()` class is a dataclass (thanks to the `@dataclass` decorator) that 
    contains options for the command-line parser.
    It uses the `simple_parsing` library to define the options and their default values.
    ."""
    # Utiliser la fonction `field()` pour spécifier une valeur par défaut
    # et une fonction `factory()` pou un attribut mutable
    
    open_sustain_tech: factory = field(default_factory=factory)
    readme_content: List[str] = list_field(default_factory=list)
    """This list has default value of ["default_1", "default_2"]"""
    
# Create and configure the `ArguementParser()` object to use the options defined int the `Options()` class
# The command-line arguments are then parsed and stored in the `args` variable.
parser = ArgumentParser()
parser.add_argument("--readme_file", type=str, default="README.md")

# Add options to the analyser
parser.add_arguments(Options, dest="options")

# Analyser les arguments de la ligne de commande
args = parser.parse_args()

readme_list: Options = args.readme_list

print(readme_list)

expected = "Options(readme_content=['default_1', 'default_2'])"

# Usage of the arguments
print("Open Sustain Tech", args.open_sustain_tech)
print("options:", args.options)

@dataclass
class OSSOptionPlugin(ApplicationPlugin):
    """
    Finally, the `OSSOptionPlugin()` class is defined.
    This class is a subclass of `ApplicationPlugin()` from the `poetry` library.
    It has an `activate()` method that is used to register the `open_sustain_tech` command
    with the application.
    It also has a `commands` property that returns a list of available commands,
    in this case, an instance of `OpenSustainTech()` class.
    """
    def activate(self, application):
        application.command_loader.register_factory("open_sustain_tech", factory)
        
    @property
    def commands(self):
        return [factory()]
    
    def activate(self, application: Application):
        application.event_dispatcher.add_listener(
            COMMAND, self.load_dotenv
        )
        
    def load_dotenv(
        self,
        event: ConsoleCommandEvent,
        event_name: str,
        dispatcher: EventDispatcher
    ) -> None:
        command = event.command
        if not isinstance(command, EnvCommand):
            return
        
        io = event.io
        
        if io.is_debug():
            io.write_line(
                "<debug>Loading environment variables.</debug>"
            )
            
        load_dotenv()
        g = Github(getenv("GITHUB_API_KEY"))
        awesome_url = "https://github.com/protontypes/open-sustainable-technology"
        awesome_path = urlparse(awesome_url).path.strip("/")
        filename = "README.md"
        
        awesome_repo = g.get_repo(awesome_path)
        awesome_content_encoded = awesome_repo.get_contents(
            urllib.parse.quote(filename)
        ).content
        awesome_content = base64.b64decode(awesome_content_encoded)
        
        filehandle = open(".awesome.md", "w")
        filehandle.write(awesome_content.decode("utf-8"))
        filehandle.close()
        repo_dict = awesome2py.AwesomeList(".awesome.md")

        # for repo_dict in awesome_repo.get_readme():
        #     print(f"Configuration Awesome README file: {repo_dict}")
        
        print(repo_dict)