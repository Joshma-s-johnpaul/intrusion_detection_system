FROM python:3.9-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y openjdk-11-jdk wget gcc g++
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
RUN wget -P /app/ https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.1/flink-sql-connector-kafka-1.17.1.jar
COPY requirements.txt .
RUN pip install --upgrade pip "setuptools<70.0.0" wheel
RUN pip install --default-timeout=1000 -r requirements.txt
COPY . .
CMD ["python", "flink_processor.py"]