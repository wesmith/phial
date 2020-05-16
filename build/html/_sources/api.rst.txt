***
API
***


Experiment
==========

In addition to the API functionality, the experiment module provides a
python script.  Run it with: ``python3 experiment.py``.
See :ref:`experiment-cmd-line`

.. automodule:: experiment
    :members:
    :undoc-members:
    :exclude-members: main, my_parser
    :inherited-members:

.. _experiment-cmd-line:

Running an experiment from the command line
-------------------------------------------


.. argparse::
   :ref: phial.experiment.my_parser
   :prog: experiment
          
Toolbox
=======

.. automodule:: toolbox
    :members:
    :undoc-members:
    :exclude-members: eval_node, node_pd
    :inherited-members:
       
