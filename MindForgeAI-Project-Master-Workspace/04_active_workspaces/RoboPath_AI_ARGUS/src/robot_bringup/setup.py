import os
from setuptools import find_packages, setup

package_name = 'robot_bringup'


def package_files(directory):
    """Install launch files while retaining any nested launch directories."""
    data_files = []
    for path, directories, filenames in os.walk(directory):
        # Python bytecode is generated locally and must never be installed as
        # a launch asset.  It can otherwise leave dangling symlinks on an
        # incremental colcon build.
        directories[:] = [name for name in directories if name != '__pycache__']
        files = [os.path.join(path, filename) for filename in filenames
                 if not filename.endswith(('.pyc', '.pyo'))]
        if files:
            data_files.append((os.path.join('share', package_name, path), files))
    return data_files


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ] + package_files('launch') + package_files('worlds') + package_files('config'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='argus',
    maintainer_email='argus@todo.todo',
    description='ARGUS Robot Bringup',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
