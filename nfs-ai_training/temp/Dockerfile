FROM ubuntu:24.04

RUN set -xe && echo '#!/bin/sh' > /usr/sbin/policy-rc.d  && echo 'exit 101' >> /usr/sbin/policy-rc.d  && chmod +x /usr/sbin/policy-rc.d   && dpkg-divert --local --rename --add /sbin/initctl  && cp -a /usr/sbin/policy-rc.d /sbin/initctl  && sed -i 's/^exit.*/exit 0/' /sbin/initctl   && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup   && echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean  && echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean  && echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean   && echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages   && echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes   && echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests
RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container
CMD ["/bin/bash"]
LABEL version=1.0
LABEL net.alagas.author="Soragan Ong <soragan@alagas.net>"

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm

RUN apt update && \
    apt install -y --no-install-recommends \
        apt-utils \
        pkg-config \
        python3-pip \
        #python3-full \
        python3-venv \
        python3-dev \
        libmysqlclient-dev \
        build-essential \
        libldap2-dev \
        libsasl2-dev \
        libffi-dev && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/app

RUN apt -y update #&& apt -y dist-upgrade
RUN apt install -y docker.io
RUN apt install -y libltdl7

RUN pip install wheel --timeout 120 --retries 5
RUN pip install mysqlclient --timeout 120 --retries 5
RUN pip install gunicorn --timeout 120 --retries 5
RUN pip install pyjwt --timeout 120 --retries 5
RUN pip install django==6.0.7 --timeout 120 --retries 5 #--trusted-host chq-k8sm.appcn.chn -i http://chq-k8sm.appcn.chn:30005/repository/a-pypi-group/simple
RUN pip install django-auth-ldap --timeout 120 --retries 5 #==4.3.0 # buildkit
RUN pip install pymysql --timeout 120 --retries 5 #--trusted-host chq-k8sm.appcn.chn -i http://chq-k8sm.appcn.chn:30005/repository/a-pypi-group/simple
RUN pip install django-simpleui --timeout 120 --retries 5 #--trusted-host chq-k8sm.appcn.chn -i http://chq-k8sm.appcn.chn:30005/repository/a-pypi-group/simple
RUN pip install django-import-export --timeout 120 --retries 5 #==3.3.6 #--trusted-host chq-k8sm.appcn.chn -i http://chq-k8sm.appcn.chn:30005/repository/a-pypi-group/simple
RUN pip install celery --timeout 120 --retries 5 #--trusted-host chq-k8sm.appcn.chn -i http://chq-k8sm.appcn.chn:30005/repository/a-pypi-group/simple
RUN pip install channels --timeout 120 --retries 5
RUN pip install docker --timeout 120 --retries 5
RUN pip install daphne --timeout 120 --retries 5
RUN pip install PyYAML kubernetes --timeout 120 --retries 5
RUN pip install whitenoise --timeout 120 --retries 5

RUN mkdir -p /cit
WORKDIR /cit
CMD /opt/venv/bin/python manage.py runserver 0.0.0.0:8000
EXPOSE 8000

