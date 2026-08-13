import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Explicitly bundle all URDF files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        # Bundle any 3D CAD meshes
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*.stl')),
        # Bundle launch files if you add them later
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sneha',
    maintainer_email='sneha@chatake.innoworks',
    description='URDF package for the ARGUS cognitive autonomous escort robot.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)