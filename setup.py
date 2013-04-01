
from distutils.core import setup

setup(name='SuMo',
      version='1.1',
      description='The smart public cloud monitoring tool',
      author='Kokkinos Panagiotis , Kretsis Aristotelis , Poluzois Soumplis',
      author_email='kokkinop@gmail.com , aakretsis@gmail.com , polibios@gmail.com',
      url='https://github.com/sumo-tool/sumo',
      packages=['sumo','sumo.cloudData','sumo.cloudForce','sumo.cloudKeeping','sumo.core','sumo.simCloudData'],
      package_data={'sumo.cloudData': ['data/json/*.json']},

     )

