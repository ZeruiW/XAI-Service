FROM node:20-alpine3.17

WORKDIR /frontend-x

COPY . .

RUN yarn set version stable && \
    yarn install

CMD ["yarn", "dev"]

# ENTRYPOINT ["tail", "-f", "/dev/null"]
