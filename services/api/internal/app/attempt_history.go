package app

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"github.com/google/uuid"
	"strings"
	"time"
)

// History uses original database creation time plus ID; answer updates cannot reorder it.
func (s *Storage) AttemptHistory(ctx context.Context, limit int, cursor string) ([]any, string, error) {
	return s.AttemptHistoryForCase(ctx, limit, cursor, "")
}

// Optional review selection follows the currently selected result key while
// keeping the original heard case and answer immutable in the returned row.
func (s *Storage) AttemptHistoryForCase(ctx context.Context, limit int, cursor, selectedCase string) ([]any, string, error) {
	if limit < 1 || limit > 100 {
		return nil, "", ErrInput
	}
	at, id := "", ""
	if cursor != "" {
		raw, e := base64.RawURLEncoding.DecodeString(cursor)
		if e != nil {
			return nil, "", ErrInput
		}
		parts := strings.Split(string(raw), "|")
		if len(parts) != 2 {
			return nil, "", ErrInput
		}
		at, id = parts[0], parts[1]
		if _, e = time.Parse(time.RFC3339Nano, at); e != nil {
			return nil, "", ErrInput
		}
		if _, e = uuid.Parse(id); e != nil {
			return nil, "", ErrInput
		}
	}
	rows, e := s.DB.Query(ctx, `SELECT d.payload,c.result_id,to_char(original.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"') FROM entity_head h JOIN document d ON d.id=h.document_id JOIN attempt_context c ON c.attempt_id=h.id JOIN document original ON original.id=h.id LEFT JOIN document result ON result.id=c.result_id WHERE h.kind='attempt' AND ($4='' OR coalesce(result.payload#>>'{score,case_version_id}',d.payload->>'case_version_id')=$4) AND ($1='' OR (original.created_at,h.id)<(nullif($1,'')::timestamptz,$2)) ORDER BY original.created_at DESC,h.id DESC LIMIT $3`, at, id, limit+1, selectedCase)
	if e != nil {
		return nil, "", e
	}
	defer rows.Close()
	items := []any{}
	next := ""
	for rows.Next() {
		var raw []byte
		var result *string
		var created string
		if e = rows.Scan(&raw, &result, &created); e != nil {
			return nil, "", e
		}
		var a map[string]any
		_ = json.Unmarshal(raw, &a)
		if len(items) == limit {
			last := items[len(items)-1].(map[string]any)
			next = last["_cursor"].(string)
			break
		}
		var resultID any
		if result != nil {
			resultID = *result
		}
		items = append(items, map[string]any{"id": a["attempt_id"], "case_version_id": a["case_version_id"], "state": a["state"], "started_at": a["started_at"], "submitted_at": a["submitted_at"], "result_id": resultID, "_cursor": base64.RawURLEncoding.EncodeToString([]byte(created + "|" + a["attempt_id"].(string)))})
	}
	if e = rows.Err(); e != nil {
		return nil, "", e
	}
	for _, v := range items {
		delete(v.(map[string]any), "_cursor")
	}
	return items, next, nil
}
