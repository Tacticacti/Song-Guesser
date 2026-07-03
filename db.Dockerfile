# The stock postgres image includes gosu only to step down from root to the
# postgres user on startup. We start as the postgres user directly (see
# docker-compose.yml), so gosu is never executed — and its Go build is flagged
# for CVE-2025-68121, so remove the binary entirely.
FROM postgres:17-alpine
RUN rm /usr/local/bin/gosu
