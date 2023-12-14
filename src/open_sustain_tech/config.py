import shlex
from dataclasses import dataclass

import simple_parsing
from open_sustain_tech.application_plugin import OpenSustainTech

@dataclass
class OSSOptionParserConfig:
    """One configuration for the OSSOptionParser."""
    worker: int = 8 # The number of workers for the parsing
    readme_file: str = OpenSustainTech(".awesome.md") # The file to parse
    
@dataclass
class EvalConfig:
    """Evaluation configuration"""
    
    n_batches: int = 8 # The number of batches to use for the evaluation
    checkpoint: str = "best.awesome" # The checkpoint to use for the evaluation
    
# def main(args=None) -> None:
#     cfg = simple_parsing.parse(config_class=OSSOptionParserConfig, args=args, add_config_path_arg=True)
#     print(f"Parsing {cfg.readme_file} with {cfg.worker} workers ...")
    
def main(args=None) -> None:
    parser = simple_parsing.ArgumentParser(add_config_path_arg=True)
    
    parser.add_arguments(OSSOptionParserConfig, dest="cfg")
    parser.add_arguments(EvalConfig, dest="eval")
    
    if isinstance(args, str):
        args = shlex.split(args)
    args = parser.parse_args(args)
    
    parse_config: OSSOptionParserConfig = args.cfg
    eval_config: EvalConfig = args.eval
    print(f"Parsing {parse_config.readme_file} with {parse_config.worker} workers ...")
    print(f"Evaluating '{eval_config.checkpoint}' with {eval_config.n_batches} batches ...")
        

main()
expected = """
Parsing README.md with 8 workers ...
Evaluating 'best.awesome' with 8 batches ...
"""

main("")
expected += """
Parsing README.md with 8 workers ...
Evaluating 'best.awesome' with 8 batches ...
"""

# TODO: When running Awesome Cure:
main("--config_path many_configs.yaml --readme_file .awesome.md")
expected += """
Parsing README.md with 42 workers ...
Evaluating 'best.awesome' with 100 batches ...
"""