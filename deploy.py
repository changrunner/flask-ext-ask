"""Deploy the package to pypi.org"""

# Standard libs
from glob import glob
from pathlib import Path
from shutil import rmtree
from subprocess import Popen, PIPE
from typing import Dict, List, Optional

# Third party libs
import yaml
import toml


class Deploy:
    """Class to assist with the deployment of the pypi package."""

    def __init__(self) -> None:
        """Initialize class variables."""
        self._deploy_config_file_name = 'deploy_config.yaml'
        self._deploy_config = Deploy._get_deploy_config(deploy_config_file_name=self._deploy_config_file_name)
        self.test_errors: Optional[List[str]] = None

    @property
    def package_version(self) -> str:
        """Version of the package getter."""
        return self._deploy_config['package_version']

    @package_version.setter
    def package_version(self, value) -> None:
        """Version of the package setter."""
        self._deploy_config['package_version'] = value

    @property
    def project_name(self) -> str:
        """Name of the project or package."""
        return self._deploy_config['project']['project_name']

    @property
    def author(self) -> str:
        """Author of the package."""
        return self._deploy_config['project']['author']

    @property
    def author_email(self) -> str:
        """Email address of the author of the package."""
        return self._deploy_config['project']['author_email']

    @property
    def description(self) -> str:
        """Package short description"""
        return self._deploy_config['project']['description']

    @property
    def long_description(self) -> str:
        """Package long description."""
        return Path('README.md').read_text(encoding='utf-8')

    @property
    def requirements(self) -> List:
        """Package requirements from the pipfile."""
        with open(file='pipfile', mode='r', encoding='utf-8') as file:
            configuration_file = toml.load(file)
        return [f'{key}{value}' for key, value in configuration_file['packages'].items()]

    @property
    def url(self) -> str:
        """Package git url."""
        return self._deploy_config['project']['url']

    def increment_package_build_version_no(self) -> None:
        """Increment the build version of the package."""
        current_version = self.package_version.split('.')
        major_version = current_version[0]
        minor_version = current_version[1]
        build_no = str(int(current_version[2]) + 1)
        self.package_version = f'{major_version}.{minor_version}.{build_no}'
        self._save_deploy_config()

    def _save_deploy_config(self) -> None:
        """Save the package config to yaml."""
        with open(file=self._deploy_config_file_name, mode='w', encoding='utf-8') as file_handler:
            yaml.dump(data=self._deploy_config, stream=file_handler)

    @staticmethod
    def _get_deploy_config(deploy_config_file_name: str) -> Dict:
        """Get the package config from the deploy_config.yaml."""
        with open(file=deploy_config_file_name, mode='r', encoding='utf-8') as file_handler:
            deploy_config = yaml.load(stream=file_handler, Loader=yaml.SafeLoader)
        return deploy_config

    @staticmethod
    def clean_build_directories() -> None:
        """Remove all build directories."""
        rmtree('dist', ignore_errors=True)
        rmtree('build', ignore_errors=True)
        for file_name in glob('*.egg-info'):
            rmtree(file_name, ignore_errors=True)

    def run_tests(self) -> bool:
        """Run Unit Tests"""
        with Popen(['pytest'], stdout=PIPE) as p_open:
            out, _ = p_open.communicate()

            self.test_errors = out.decode("utf-8").split('\r\n')

            if "passed" in self.test_errors[len(self.test_errors)-2]:
                return True
            return False

    def print_test_errors(self) -> None:
        """Print the errors encountered during unit tests"""
        print("Test Failed")
        for line in self.test_errors or []:
            print(line)

    @staticmethod
    def build_package() -> None:
        """Build the package."""
        with Popen(['pipenv', 'run', 'python', 'setup.py', 'sdist', 'bdist_wheel']) as p_open:
            p_open.communicate()

    @staticmethod
    def upload_package() -> None:
        """Upload the package to the test.pypi.org."""
        with Popen(['pipenv', 'run', 'python', '-m', 'twine', 'upload', '--skip-existing', '--repository',
                    'testpypi', 'dist/*']) as p_open:
            p_open.communicate()


def main() -> None:
    """Deployment pipeline of the package."""
    deploy = Deploy()
    Deploy.clean_build_directories()

    deploy.increment_package_build_version_no()
    if deploy.run_tests():
        Deploy.build_package()
        Deploy.upload_package()
    else:
        deploy.print_test_errors()


if __name__ == '__main__':
    main()
