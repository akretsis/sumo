
.. _index:

=======================================
SuMo: Smart Cloud Monitoring toolkit
=======================================

Smart Cloud Monitoring toolkit, has been developed to contain the necessary mechanisms for collecting monitoring data 
from `Amazon Web Services (AWS) <http://aws.amazon.com/  />`_ and analyzing them. 

SuMo makes easy for anyone, a researcher or an administrator, to monitor the owned instances, run the proposed mechanisms [] or implement new more intelligent ones. SuMo is open-source and available through github SuMo-tool: https://github.com/SuMo-tool. To the best of our knowledge it is the only open-source cloud monitoring toolkit for public clouds and in particular for AWS.


Sumo: Architecture
----------------------------

SuMo is composed of three main components/modules: cloudData, cloudKeeping and cloudForce. cloudData is responsible for collecting monitoring data, cloudKeeping contains a set of key performance indicators (KPI), while cloudForce 
incorporates a set of analytic and optimization algorithms.

.. figure::  images/sumo.png
   :align:   center

   SuMo – Smart cloud Monitoring basic modules


* **SuMo Modules**

  * cloudData : Collecting Monitoring Data  -- (:doc:`API Reference <cloudData>`)
  * cloudKeeping : Key performance Indicators -- (:doc:`API Reference <cloudKeeping>`)
  * cloudForce : Analytic and Optimization Algorithms  -- (:doc:`API Reference <cloudForce>`)
  * simCloudData: Create simulated instances -- (:doc:`API Reference <simCloudData>`)


Additional Resources
--------------------



.. toctree::
   :hidden:

   cloudData
   cloudKeeping
   cloudForce
   simCloudData
 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

