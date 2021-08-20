FROM crmas_python as crams_python_base

RUN apt-get update --fix-missing
# no extra lib required as already covered in nec_python section
RUN apt-get install -y --no-install-recommends mysql-client libmysqlclient-dev

# set default environment variables
# Python won’t try to write .pyc files which we do not want.
ENV PYTHONDONTWRITEBYTECODE 1
# This ensures our console output looks familiar and is not buffered by Docker, which we don’t want.
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
# set project environment variables
# grab these via Python's os.environ
# these are 100% optional here
# create and set working directory
RUN mkdir /crams-apps
WORKDIR /crams-apps

#Upgrade pip
RUN pip install pip -U

# setup nec user and group
RUN groupadd --gid 10001 crams && \
    useradd -g crams --uid 10001 --shell /usr/sbin/nologin --create-home --home-dir /crams crams

# Add current directory code to working directory

ADD . /crams-apps/
RUN chown crams:crams -Rf /crams-apps

WORKDIR /crams-apps/merc_common
RUN python setup.py sdist

WORKDIR /crams-apps/crams_log
RUN python setup.py sdist

WORKDIR /crams-apps/crams_contact
RUN python setup.py sdist

WORKDIR /crams-apps/crams_notification
RUN python setup.py sdist

WORKDIR /crams-apps/crams_compute
RUN python setup.py sdist

WORKDIR /crams-apps/crams_storage
RUN python setup.py sdist

WORKDIR /crams-apps/crams_collection
RUN python setup.py sdist

WORKDIR /crams-apps/crams_demo
RUN python setup.py sdist

WORKDIR /crams-apps/crams_allocation
RUN python setup.py sdist

WORKDIR /crams-apps/crams_provision
RUN python setup.py sdist

WORKDIR /crams-apps/crams_member
RUN python setup.py sdist

WORKDIR /crams-apps/crams_resource_usage
RUN python setup.py sdist

WORKDIR /crams-apps/crams_reports
RUN python setup.py sdist

WORKDIR /crams-apps/crams_api

RUN pip install ../merc_common/dist/merc_common-1.0.0.tar.gz
RUN pip install ../crams_log/dist/crams_log-1.0.0.tar.gz
RUN pip install ../crams_contact/dist/crams_contact-1.0.0.tar.gz
RUN pip install ../crams_notification/dist/crams_notification-1.0.0.tar.gz
RUN pip install ../crams_compute/dist/crams_compute-1.0.0.tar.gz
RUN pip install ../crams_storage/dist/crams_storage-1.0.0.tar.gz
RUN pip install ../crams_collection/dist/crams_collection-1.0.0.tar.gz
RUN pip install ../crams_demo/dist/crams_demo-1.0.0.tar.gz
RUN pip install ../crams_allocation/dist/crams_allocation-1.0.0.tar.gz
RUN pip install ../crams_provision/dist/crams_provision-1.0.0.tar.gz
RUN pip install ../crams_member/dist/crams_member-1.0.0.tar.gz
RUN pip install ../crams_resource_usage/dist/crams_resource_usage-1.0.0.tar.gz
RUN pip install ../crams_reports/dist/crams_reports-1.0.0.tar.gz


RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt

RUN pip freeze .


