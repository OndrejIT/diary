FROM docker.io/python:3.8-alpine

COPY . /opt/diary

# Timezone
RUN \
	export TIMEZONE=Europe/Prague && \
	apk add -U tzdata && \
	cp /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
	echo "${TIMEZONE}" > /etc/timezone

# Packages
RUN	apk add postgresql

# Build tools
RUN \
	apk add --virtual build-deps \
	curl \
	postgresql-dev \
	gcc \
	musl-dev \
	libc-dev \
	linux-headers

# Add mime.types
RUN curl -s https://raw.githubusercontent.com/radek-senfeld/mime-types/master/mime.types -o /etc/mime.types

# Python stuff
RUN pip install -r /opt/diary/requirements.txt --no-cache-dir

# Cleaning up
RUN apk del build-deps && rm -rf /var/cache/apk/*

WORKDIR /opt/diary

EXPOSE 8080 8080

USER nobody

ENTRYPOINT ["uwsgi", "--ini"]
