FROM golang:1.26.5-bookworm@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd AS build
WORKDIR /src
ENV GOWORK=off GOTOOLCHAIN=local
COPY services/api/go.mod services/api/go.sum ./
RUN go mod download
COPY services/api/ ./
RUN CGO_ENABLED=0 go build -mod=readonly -trimpath -o /tangerine ./cmd/tangerine

FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=build /tangerine /usr/local/bin/tangerine
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/tangerine"]
CMD ["serve"]
