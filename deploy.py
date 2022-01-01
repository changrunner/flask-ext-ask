"""Deploy the package to pypi.org"""

# Standar libs
from subprocess import Popen, PIPE
from typing import Dict
from pathlib import Path
import shutil
import glob
import yaml
import toml


class Deploy:
    """"""

    def __init__(self):
        """"""
        self._deploy_config_file_name = 'deploy_config.yaml'
        self._deploy_config = Deploy._get_deploy_config(deploy_config_file_name=self._deploy_config_file_name)
        self.test_errors = None

    @property
    def package_version(self):
        """"""
        return self._deploy_config['package_version']

    @package_version.setter
    def package_version(self, value):
        """"""
        self._deploy_config['package_version'] = value

    @property
    def project_name(self):
        """"""
        return self._deploy_config['project']['project_name']

    @property
    def author(self):
        """"""
        return self._deploy_config['project']['author']

    @property
    def author_email(self):
        """"""
        return self._deploy_config['project']['author_email']

    @property
    def description(self):
        """"""
        return self._deploy_config['project']['description']

    @property
    def long_description(self):
        """"""
        return Path('README.md').read_text(encoding='utf-8')

    @property
    def requirements(self):
        """"""
        with open('pipfile') as file:
            configuration_file = toml.load(file)
        return [f'{key}{value}' for key, value in configuration_file['packages'].items()]

    @property
    def url(self):
        """"""
        return self._deploy_config['project']['url']

    def increment_package_build_version_no(self):
        """"""
        current_version = self.package_version.split('.')
        major_version = current_version[0]
        minor_version = current_version[1]
        build_no = str(int(current_version[2]) + 1)
        self.package_version = f'{major_version}.{minor_version}.{build_no}'
        self._save_deploy_config()

    def _save_deploy_config(self):
        """"""
        with open(self._deploy_config_file_name, mode='w') as file_handler:
            yaml.dump(data=self._deploy_config, stream=file_handler)

    @staticmethod
    def _get_deploy_config(deploy_config_file_name: str) -> Dict:
        """"""
        with open(deploy_config_file_name, mode='r') as file_handler:
            deploy_config = yaml.load(stream=file_handler, Loader=yaml.SafeLoader)
        return deploy_config

    @staticmethod
    def clean_build_directories():
        """"""
        shutil.rmtree('dist', ignore_errors=True)
        shutil.rmtree('build', ignore_errors=True)
        [shutil.rmtree(file_name, ignore_errors=True) for file_name in glob.glob('*.egg-info')]

    def run_tests(self) -> bool:
        """"""
        p = Popen(['pytest'], stdout=PIPE)
        out, err = p.communicate()

        self.test_errors = out.decode("utf-8") .split('\r\n')

        if "passed" in self.test_errors[len(self.test_errors)-2]:
            return True
        return False

    def print_test_errors(self) -> None:
        """"""
        print("Test Failed")
        for line in self.test_errors:
            print(line)

    @staticmethod
    def build_package():
        """"""
        p = Popen(['pipenv', 'run', 'python', 'setup.py', 'sdist', 'bdist_wheel'])
        p.communicate()

    @staticmethod
    def upload_package():
        """"""
        p = Popen(['pipenv', 'run', 'python', '-m', 'twine', 'upload', '--skip-existing', '--repository', 'testpypi', 'dist/*'])
        p.communicate()


def main():
    """"""
    deploy = Deploy()
    Deploy.clean_build_directories()

    deploy.increment_package_build_version_no()
    if deploy.run_tests():
        pass
        Deploy.build_package()
        Deploy.upload_package()
    else:
        deploy.print_test_errors()


if __name__ == '__main__':
    """"""
    main()

