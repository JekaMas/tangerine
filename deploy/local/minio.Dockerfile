FROM golang:1.26.5-bookworm@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd AS build
ENV GOTOOLCHAIN=local GOWORK=off
RUN curl --fail --location --output /src.tar.gz https://codeload.github.com/minio/minio/tar.gz/7aac2a2c5b7c882e68c1ce017d8256be2feea27f && echo '71794c2df26aad0cc99e8421c58b7aa2dd55969f979b0e7d1e931042e9fabcd6  /src.tar.gz' | sha256sum --check -
RUN mkdir /src && tar -xzf /src.tar.gz --strip-components=1 -C /src
WORKDIR /src
RUN CGO_ENABLED=0 go build -mod=readonly -trimpath -o /minio .
COPY deploy/local/probe.go /probe.go
RUN CGO_ENABLED=0 go build -trimpath -o /probe /probe.go

FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=build /minio /usr/local/bin/minio
COPY --from=build /probe /usr/local/bin/probe
EXPOSE 9000
ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data", "--address", ":9000", "--console-address", ":9001"]
