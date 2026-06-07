FROM quay.io/debezium/connect:2.4

USER root
# Cài đặt công cụ unzip
RUN microdnf -y install unzip

USER kafka
# Sử dụng API chính thức của Confluent Hub để lấy file (thay vì dùng link CDN tĩnh dễ lỗi mạng)
RUN curl -sS -L "https://api.hub.confluent.io/api/plugins/confluentinc/kafka-connect-jdbc/versions/10.7.4/archive" -o /tmp/jdbc.zip \
    && unzip -q /tmp/jdbc.zip -d /kafka/connect/ \