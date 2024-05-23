import argparse
from functools import cached_property


class ArgsParseManager:

    @cached_property
    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-json_payload", type=str, help="json payload")
        return parser

    def parse_args(self, *args):
        return self.parser.parse_args(*args)
