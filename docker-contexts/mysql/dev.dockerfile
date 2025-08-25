#==================
FROM mysql:8.0

# Set timezone (UTC by default)
ENV TZ=${TZ:-UTC}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ###### ADD SCRIPT SQL
ADD init.sql /docker-entrypoint-initdb.d/init.sql

# Copy config file
# COPY my.cnf /etc/mysql/conf.d/
# RUN chmod 644 /etc/mysql/conf.d/my.cnf