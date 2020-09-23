import argparse
import re
import os
from typing import List, Tuple
from tqdm import tqdm

import helpers.io_ as io_
import helpers.system_interaction as sys_inter
import helpers.dbg as dbg
from helpers.timer import Timer

parser = argparse.ArgumentParser(description='calculate execution time of imports')
parser.add_argument('-directory',
                    type=str,
                    required=True,
                    help='absolute path to search directory, always requires absolute path')
parser.add_argument('-e',
                    '--env_path',
                    type=str,
                    help='absolute path to environment activate file')

args = parser.parse_args()


class ImportTimeChecker:
    """
    Class for measure execution time for imports

    """

    def __init__(self, root_dir_path, env_file_path=None):
        """
        :param dir_path: directory name to search python files
        :param env_file_path: path to env activate file
        """
        self.dir_path = root_dir_path
        self.env_file_path = env_file_path
        self.checked_modules = {}
        """ store all the modules with execution time (module: elapsed_time) """
        self.not_found_imports = []
        """ modules that cannot found """
        self.timer = Timer()
        """ instance of class for measure elapsed time """
        self.match_pattern = '(?m)^(?:from|import)\s+([a-zA-Z0-9_.]+(?:\s*,\s*\w+)*)'
        """ pattern for finding modules in file """

    def find_modules_from_file(self, file_name: str) -> List[str]:
        """
        Search modules in a given file

        :param file_name: filename where need to search modules
        :return: list of all found module name
        """
        text = io_.from_file(file_name)
        modules = re.findall(self.match_pattern, text)
        return modules

    def measure_time(self, module: str) -> float:
        """
        Measures execution time for a given module and save in self.checked_modules
        :param module: module name
        :return: elapsed time to execute import
        """
        if module not in self.checked_modules:
            try:
                cmd = f'export PYTHONPATH=$PYTHONPATH:{self.dir_path};'
                """ set python path in order python can find modules """

                if self.env_file_path:
                    cmd += f'source {self.env_file_path};'
                    """ activates environment"""

                cmd += f'python -c "import {module}"'
                """ execute python "import module" to measure """
                self.timer.resume()
                sys_inter.system(cmd)
                self.timer.stop()
            except RuntimeError:
                self.not_found_imports.append(module)

            elapsed_time = round(self.timer.get_elapsed(), 3)
            self.checked_modules[module] = elapsed_time
        return self.checked_modules[module]

    def measure_time_for_all_modules(self) -> None:
        """
        Traverse files and directory and find all modules and measure execution time
        :return: None
        """
        file_names = io_.find_files(self.dir_path, '*.py')
        for file_name in tqdm(file_names):
            # print(f'filename: {file_name}')
            modules = self.find_modules_from_file(file_name)
            for module in modules:
                self.measure_time(module)

    def _sort_by_time(self) -> None:
        """
        Sort time in ascending order in self.checked_modules
        :return: None
        """
        output = sorted(self.checked_modules.items(), key=lambda x: x[1])
        self.checked_modules = {module: time for module, time in output}

    def print_modules_time(self, sort=False) -> None:
        """
        Print all measured modules
        :param sort: defines whether sort output or not
        :return: None
        """
        if sort:
            self._sort_by_time()
        for module, elapsed_time in self.checked_modules.items():
            print(f'{module} {elapsed_time} s')

    def get_total_time(self) -> float:
        """
        Calculates total time spend for importing
        :return: float
        """
        total_time = 0
        for time in self.checked_modules.values():
            total_time += time
        return total_time

    def get_list(self) -> List[Tuple[str, float]]:
        """
        Return self.checled_modules in list format
        :return: list
        """
        output = [(module, elapsed_time) for module, elapsed_time
                  in self.checked_modules.items()]
        return output


if __name__ == '__main__':
    dir_path = args.directory
    dbg.dassert(os.path.isabs(dir_path), msg=f'{dir_path} is not a absolute path to directory')
    dbg.dassert_dir_exists(dir_path)

    env_path = args.env_path
    if env_path:
        dbg.dassert(os.path.isabs(dir_path), msg=f'{env_path} is not a absolute path to env activate file')
        dbg.dassert_exists(env_path)

    checker = ImportTimeChecker(dir_path, env_path)
    checker.measure_time_for_all_modules()
    checker.print_modules_time(sort=True)

    total_time = round(checker.get_total_time(), 3)
    print(f'Total time for importing: {total_time}')
    print(f'modules that cannot import: {checker.not_found_imports}')
