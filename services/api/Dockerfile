FROM golang:1.26.5-bookworm@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd AS build
WORKDIR /src
ENV GOWORK=off GOTOOLCHAIN=local
COPY services/api/go.mod services/api/go.sum ./
RUN go mod download
COPY services/api/ ./
ARG HOST_OS=linux
ARG HOST_ARCH=arm64
RUN CGO_ENABLED=0 go build -mod=readonly -trimpath -o /tangerine ./cmd/tangerine
RUN CGO_ENABLED=0 GOOS=$HOST_OS GOARCH=$HOST_ARCH go build -mod=readonly -trimpath -o /public-probe ./cmd/tangerine

FROM postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=build /tangerine /usr/local/bin/tangerine
COPY --from=build /public-probe /usr/local/bin/public-probe
LABEL org.opencontainers.image.version="0.1.0-foundation"
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/tangerine"]
CMD ["serve"]
