#!/bin/bash
source  ~/.pyenv/versions/crams_py38/bin/activate

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

cd ../crams_racmon
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
pip uninstall -y merc_common
pip install ../merc_common/dist/merc_common-1.0.0.tar.gz
pip uninstall -y crams_log
pip install ../crams_log/dist/crams_log-1.0.0.tar.gz
pip uninstall -y crams_contact
pip install ../crams_contact/dist/crams_contact-1.0.0.tar.gz
pip uninstall -y crams_notification
pip install ../crams_notification/dist/crams_notification-1.0.0.tar.gz
pip uninstall -y crams_compute
pip install ../crams_compute/dist/crams_compute-1.0.0.tar.gz
pip uninstall -y crams_storage
pip install ../crams_storage/dist/crams_storage-1.0.0.tar.gz
pip uninstall -y crams_collection
pip install ../crams_collection/dist/crams_collection-1.0.0.tar.gz
pip uninstall -y crams_allocation
pip install ../crams_allocation/dist/crams_allocation-1.0.0.tar.gz
pip uninstall -y crams_provision
pip install ../crams_provision/dist/crams_provision-1.0.0.tar.gz
pip uninstall -y crams_member
pip install ../crams_member/dist/crams_member-1.0.0.tar.gz
pip uninstall -y crams_resource_usage
pip install ../crams_resource_usage/dist/crams_resource_usage-1.0.0.tar.gz
pip uninstall -y crams_reports
pip install ../crams_reports/dist/crams_reports-1.0.0.tar.gz
pip uninstall -y crams_racmon
pip install ../crams_racmon/dist/crams_racmon-1.0.0.tar.gz

pip install -r ../crams_api/requirements.txt
pip install -r ../crams_api/test-requirements.txt