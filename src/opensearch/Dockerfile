# Declare a build argument for the version
ARG OPENSEARCH_IMAGE

# Use OpenSearch image as base
FROM ${OPENSEARCH_IMAGE}

# Install prometheus plugin (https://github.com/aiven/prometheus-exporter-plugin-for-opensearch)
USER root
RUN /usr/share/opensearch/bin/opensearch-plugin install https://github.com/aiven/prometheus-exporter-plugin-for-opensearch/releases/download/2.9.0.0/prometheus-exporter-2.9.0.0.zip

# Switch back to opensearch user
USER opensearch