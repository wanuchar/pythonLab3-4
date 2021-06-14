FROM nginxinc/nginx-unprivileged:1-alpine


RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

USER root

RUN mkdir -p /education/web/media
RUN mkdir -p /education/web/static
RUN chmod 755 /education/web/static
RUN chmod 755 /education/web/media

USER nginx