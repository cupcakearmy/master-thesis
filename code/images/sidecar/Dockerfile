FROM golang:1.20 as builder
WORKDIR /app
COPY . .
RUN go build

FROM ubuntu
RUN apt-get update && apt-get install -y dnsutils
WORKDIR /app
COPY --from=builder /app .
EXPOSE 42069
CMD /app/sidecar
