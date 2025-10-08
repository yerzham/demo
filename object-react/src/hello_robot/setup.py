from setuptools import setup

package_name = 'hello_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='booster',
    maintainer_email='booster@lindy.ai',
    description='Simple ROS2 test package for Lindy deployment',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hello_node = hello_robot.hello_node:main',
            'status_node = hello_robot.status_node:main',
        ],
    },
)

