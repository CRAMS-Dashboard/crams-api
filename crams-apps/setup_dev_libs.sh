#!/bin/bash
source  ~/.pyenv/versions/crams_demo_py38/bin/activate

export PATH=/usr/local/mysql/bin:$PATH

cd crams_api
pip freeze

cd ../merc_common
python setup.py sdist

cd ../crams_log
python setup.py sdist

cd ../crams_contact
python setup.py sdist

cd ../crams_notification
python setup.py sdist

cd ../crams_compute
python setup.py sdist

cd ../crams_storage
python setup.py sdist

cd ../crams_collection
python setup.py sdist

cd ../crams_demo
python setup.py sdist

cd ../crams_allocation
python setup.py sdist

cd ../crams_provision
python setup.py sdist

cd ../crams_member
python setup.py sdist

cd ../crams_resource_usage
python setup.py sdist

cd ../crams_reports
python setup.py sdist


cd ../crams_api
pip install --upgrade pip

cd ../merc_common
pip uninstall -y merc-common
pip install -e .

cd ../crams_log
pip uninstall -y crams_log
pip install -e .

cd ../crams_contact
pip uninstall -y crams_contact
pip install -e .

cd ../crams_notification
pip uninstall -y crams_notification
pip install -e .

cd ../crams_compute
pip uninstall -y crams_compute
pip install -e .

cd ../crams_storage
pip uninstall -y crams_storage
pip install -e .

cd ../crams_collection
pip uninstall -y crams_collection
pip install -e .

cd ../crams_allocation
pip uninstall -y crams_allocation
pip install -e .

cd ../crams_provision
pip uninstall -y crams_provision
pip install -e .

cd ../crams_member
pip uninstall -y crams_member
pip install -e .

cd ../crams_resource_usage
pip uninstall -y crams_resource_usage
pip install -e .

cd ../crams_reports
pip uninstall -y crams_reports
pip install -e .

cd ../crams_demo
pip uninstall -y crams_demo
pip install -e .


cd ..
pip install -r crams_api/requirements.txt
pip install -r crams_api/test-requirements.txt