package app

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"io"
	"tangerine.local/api/internal/contracts"
)

// StorageCommand is an internal CLI for maintenance and native tests. It exposes
// no HTTP route, accepts no credential values and calls the real shared owners.
func (s *Storage) StorageCommand(ctx context.Context, input io.Reader, output io.Writer) error {
	var r struct {
		Action    string           `json:"action"`
		ID        string           `json:"id"`
		Documents []DocumentWrite  `json:"documents"`
		Asset     AssetRequest     `json:"asset"`
		Operation OperationRequest `json:"operation"`
		Data      string           `json:"data_base64"`
		Owner     *DocumentWrite   `json:"owner"`
		Raw       string           `json:"raw_json"`
	}
	decoder := json.NewDecoder(io.LimitReader(input, 32*1024*1024))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&r); err != nil {
		return err
	}
	var result any
	var err error
	switch r.Action {
	case "write":
		result, err = s.WriteDocuments(ctx, r.Documents)
	case "read":
		result, err = s.ReadDocument(ctx, r.ID)
	case "operation":
		result, err = s.ReserveOperation(ctx, r.Operation)
	case "reserve":
		result, err = s.ReserveAsset(ctx, r.Asset)
	case "upload":
		var b []byte
		b, err = base64.StdEncoding.DecodeString(r.Data)
		if err == nil {
			result, err = s.UploadAsset(ctx, r.ID, b)
		}
	case "upload-stream":
		var data []byte
		data, err = base64.StdEncoding.DecodeString(r.Data)
		if err == nil {
			result, err = s.UploadReader(ctx, r.ID, bytes.NewReader(data))
		}
	case "recover":
		result, err = s.RecoverAsset(ctx, r.ID)
	case "begin-upload":
		result, err = s.BeginAssetUpload(ctx, r.ID)
	case "verify":
		result, err = s.VerifyAsset(ctx, r.ID)
	case "link":
		result, err = s.LinkAsset(ctx, r.ID, r.Owner)
	case "asset-read":
		var b []byte
		b, err = s.ReadAsset(ctx, r.ID)
		if err == nil {
			result = map[string]any{"data_base64": base64.StdEncoding.EncodeToString(b), "sha256": contracts.Digest(b)}
		}
	case "orphans":
		result, err = s.OrphanPreview(ctx)
	case "canonical":
		var b []byte
		b, err = contracts.Canonical([]byte(r.Raw))
		if err == nil {
			result = map[string]any{"canonical": string(b), "sha256": contracts.Digest(b)}
		}
	default:
		err = ErrConflict
	}
	response := map[string]any{"ok": err == nil}
	if err != nil {
		response["error"] = assetError(err)
	} else {
		response["result"] = result
	}
	return json.NewEncoder(output).Encode(response)
}
