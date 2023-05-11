FROM node:18

WORKDIR /app
COPY package.json .
RUN npm i
COPY index.js .

EXPOSE 3000
CMD [ "node", "." ]

