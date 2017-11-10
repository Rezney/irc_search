FROM fedora:26
MAINTAINER mreznik@redhat.com

RUN dnf update -y && dnf install -y \
    vim \
    openssl-devel \
    libffi-devel \
    nginx \
    python3-devel \
    python3-pip \
    sqlite \
    systemd

RUN rm -fv /usr/lib/systemd/system/sysinit.target.wants/*; \
rm -fv /lib/systemd/system/multi-user.target.wants/*; \
rm -fv /etc/systemd/system/*.wants/*; \
rm -fv /lib/systemd/system/local-fs.target.wants/*; \
rm -fv /lib/systemd/system/sockets.target.wants/*udev*; \
rm -fv /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -fv /lib/systemd/system/basic.target.wants/*; \
rm -fv /lib/systemd/system/anaconda.target.wants/*;

COPY . /app
RUN mkdir /static
WORKDIR /app/django
RUN pip3 install -r requirements.txt

RUN ln -s /app/conf/nginx.conf /etc/nginx/conf.d/irc_search.conf
RUN cp /app/conf/irc_search.service /etc/systemd/system/irc_search.service
RUN sed -i '/default_server/d' /etc/nginx/nginx.conf 

RUN systemctl enable nginx
RUN systemctl enable irc_search

RUN python3 -c 'import random; import string; print("".join([random.SystemRandom().choice("{}{}{}".format(string.ascii_letters, string.digits, string.punctuation)) for i in range(50)]))' > secretkey
RUN chmod 400 secretkey
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic

CMD ["/sbin/init"]
