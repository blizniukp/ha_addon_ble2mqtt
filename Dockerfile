ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apt-get update \
    && apt-get install -y \
    	python3 \
    	python3-dev \
        build-essential \
	&& curl --silent --show-error --retry 5 \
        "https://bootstrap.pypa.io/get-pip.py" \
        | python3 \
	&& pip3 install --no-cache-dir \
		paho-mqtt==1.4.0 \
	&& apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY data/run.sh /
COPY data/run.py /
RUN chmod a+x /run.sh

WORKDIR /
CMD [ "/run.sh" ]