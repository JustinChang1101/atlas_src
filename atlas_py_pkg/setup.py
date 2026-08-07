from setuptools import find_packages, setup

package_name = 'atlas_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='justin',
    maintainer_email='justin@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'dm_motor_node_1 = atlas_py_pkg.dm_motor_node_1_motor:main',
            'dm_motor_node_3 = atlas_py_pkg.dm_motor_node_3_motors:main',
        ],
    },
)
