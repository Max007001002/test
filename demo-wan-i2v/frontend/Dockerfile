FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN chmod +x ./start_script_frontend.sh

EXPOSE 3000

CMD ["sh", "/app/start_script_frontend.sh"]
