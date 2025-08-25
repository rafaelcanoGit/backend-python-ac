# Usar la imagen oficial de Redis 7.4 Alpine como base
FROM redis:7.4-alpine

# (Opcional) Copiar un archivo de configuración personalizado si lo tienes
# COPY redis.conf /usr/local/etc/redis/redis.conf

# (Opcional) Exponer el puerto 6379
# EXPOSE 6379

# (Opcional) Ejecutar Redis con un archivo de configuración personalizado
# CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

# Por defecto, la imagen ya ejecuta redis-server con configuración por defecto