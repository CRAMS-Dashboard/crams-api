FROM ubuntu:20.04

LABEL maintainer="Simon Yu <xiaoming.yu@monash.edu>"

ENV DEBIAN_FRONTEND=noninteractive

ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8



RUN apt-get update --fix-missing

# add required dependencies
RUN apt-get install -y build-essential  apt-utils vim vim-tiny wget curl less git man
RUN apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev \
                       libgdbm-dev libc6-dev
RUN apt-get install -y libbluetooth-dev tk-dev gnupg libffi-dev libffi7 sqlite3 libsqlite3-dev

RUN apt-get install -y synaptic xmlsec1

RUN apt-get install -y bzip2 libbz2-dev zlib1g-dev openssl cron \
                       libgdbm-compat-dev liblzma-dev libreadline-dev uuid-dev
RUN apt-get install -y libjpeg-dev libfreetype6-dev liblcms2-dev libtiff-dev tcl-dev \
                       texlive libxml2 libxml2-dev libsodium-dev libcurl4-openssl-dev \
                       ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# gpg key
ENV GPG_KEY E3FF2839C048B25C084DEBE9B26995E310250568
# PYTHON Version
ENV PYTHON_VERSION 3.8.11

# disable ipv6
RUN set -ex \
	\
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
	&& export GNUPGHOME="$(mktemp -d)" && echo "disable-ipv6" >> ${GNUPGHOME}/dirmngr.conf \
	&& gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$GPG_KEY" \
	&& gpg --batch --verify python.tar.xz.asc python.tar.xz \
	&& { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
	&& rm -rf "$GNUPGHOME" python.tar.xz.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	\
	&& cd /usr/src/python \
	&& gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
	&& ./configure \
		--build="$gnuArch" \
		--enable-loadable-sqlite-extensions \
		--enable-optimizations \
		--enable-option-checking=fatal \
		--enable-shared \
		--with-system-expat \
		--with-system-ffi \
		--without-ensurepip \
	&& make -j "$(nproc)" \
	&& make install \
	&& ldconfig \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python \
	\
	&& python3 --version

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 20.1.1
# https://github.com/pypa/get-pip
ENV PYTHON_GET_PIP_URL https://github.com/pypa/get-pip/raw/eff16c878c7fd6b688b9b4c4267695cf1a0bf01b/get-pip.py
ENV PYTHON_GET_PIP_SHA256 b3153ec0cf7b7bbf9556932aa37e4981c35dc2a2c501d70d91d2795aa532be79

RUN set -ex; \
	\
	wget -O get-pip.py "$PYTHON_GET_PIP_URL"; \
	echo "$PYTHON_GET_PIP_SHA256 *get-pip.py" | sha256sum --check --strict -; \
	\
	python get-pip.py \
		--disable-pip-version-check \
		--no-cache-dir \
		"pip==$PYTHON_PIP_VERSION" \
	; \
	pip --version; \
	\
	find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' +; \
	rm -f get-pip.py

CMD ["python3"]
