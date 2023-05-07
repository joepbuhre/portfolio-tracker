FROM node:16-slim as builder

WORKDIR /builder

COPY ./frontend ./

RUN npm ci
RUN npm run build

FROM python:latest as target

WORKDIR /app

COPY --from=builder /builder/dist/ /app/frontend

WORKDIR /app/backend

COPY ./backend ./

RUN pip install -r requirements.txt

CMD ['waitress-serve --listen=127.0.0.1:5000 app:app']