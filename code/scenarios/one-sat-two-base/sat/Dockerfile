FROM node:18

WORKDIR /app
COPY package.json .
RUN npm install
COPY index.js .

STOPSIGNAL SIGTERM
CMD [ "node", "." ]

