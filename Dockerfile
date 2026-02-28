FROM nginx:alpine

COPY app/public /usr/share/nginx/html

EXPOSE 80