FROM alpine

RUN apk add --no-cache docker
RUN apk add --no-cache git

CMD ["sh", "run.sh"]