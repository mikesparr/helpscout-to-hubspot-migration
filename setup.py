from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='helpscout_to_hubspot',
      version='0.1',
      description='Migration tool for helpdesk systems',
      url='http://github.com/mikesparr/helpscout-to-hubspot-migration',
      author='Mike Sparr',
      author_email='mike@goomzee.com',
      license='MIT',
      packages=['helpscout_to_hubspot'],
      install_requires=[
          'envparse',
          'requests'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
