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
RUN pip install -e .

WORKDIR /crams-apps/crams_log
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_contact
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_notification
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_compute
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_storage
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_collection
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_allocation
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_provision
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_member
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_resource_usage
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_reports
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_software
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_review
RUN python setup.py sdist
RUN pip install -e .

WORKDIR /crams-apps/crams_demo
RUN python setup.py sdist

RUN pip install -e .


WORKDIR /crams-apps/crams_api

RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt

RUN pip freeze .


