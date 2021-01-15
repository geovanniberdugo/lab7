.. 7lab documentation master file, created by
   sphinx-quickstart on Wed Mar 29 16:41:10 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

7Lab
=====

Requerimientos
--------------

* Python 3
* Django 1.8
* PostgreSQL

.. toctree::
   :maxdepth: 2
   :caption: Alimentos:

   alimentos/models
   alimentos/forms
   alimentos/views

.. toctree::
   :maxdepth: 2
   :caption: Bebidas Alcoholicas:

   bebidas_alcoholicas/models
   bebidas_alcoholicas/forms
   bebidas_alcoholicas/views

.. toctree::
   :maxdepth: 2
   :caption: Equipos:

   equipos/models
   equipos/forms
   equipos/views
   equipos/utils

.. toctree::
   :maxdepth: 2
   :caption: Trazabilidad:

   trazabilidad/models
   trazabilidad/forms
   trazabilidad/views
   trazabilidad/manager
   trazabilidad/utils
   trazabilidad/funciones
   trazabilidad/resources

.. toctree::
   :maxdepth: 2
   :caption: Administracion:

   administracion/models
   administracion/forms
   administracion/views

.. toctree::
   :maxdepth: 2
   :caption: Common:

   common/models
   common/managers
   common/decorators



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
