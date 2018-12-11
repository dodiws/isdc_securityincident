================
securityincident
================

Dashboard and api securityincident modules.
Optional Module for ASDC

Quick start
-----------

1. Add "securityincident" to your DASHBOARD_PAGE_MODULES setting like this::

   DASHBOARD_PAGE_MODULES = [
       ...
       'securityincident',
   ]

   If necessary add "securityincident" in (check comment for description): 
       QUICKOVERVIEW_MODULES, 
       MAP_APPS_TO_DB_CUSTOM

   For development in virtualenv add SECURITYINCIDENT_PROJECT_DIR path to VENV_NAME/bin/activate:
       export PYTHONPATH=${PYTHONPATH}:\
       ${HOME}/SECURITYINCIDENT_PROJECT_DIR

2. To create the securityincident tables:

   python manage.py makemigrations
   python manage.py migrate securityincident --database geodb
