package provider

import (
	"context"
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"io"
	"math/big"
	"net/http"
	"net/url"
	"strings"
)

type discovery struct {
	Issuer     string `json:"issuer"`
	JWKS       string `json:"jwks_uri"`
	Revocation string `json:"revocation_endpoint"`
}

func (m *Manager) getJSON(ctx context.Context, endpoint string, dst any) error {
	req, e := http.NewRequestWithContext(ctx, "GET", endpoint, nil)
	if e != nil {
		return fail("PROVIDER_FAILURE")
	}
	res, e := m.Client.Do(req)
	if e != nil {
		return fail("PROVIDER_FAILURE")
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return fail("PROVIDER_FAILURE")
	}
	return json.NewDecoder(io.LimitReader(res.Body, 1024*1024)).Decode(dst)
}
func (m *Manager) discovery(ctx context.Context) (discovery, error) {
	var d discovery
	e := m.getJSON(ctx, m.Protocol.Discovery, &d)
	if e != nil {
		return d, e
	}
	base, _ := url.Parse(m.Protocol.Discovery)
	for _, s := range []string{d.Issuer, d.JWKS, d.Revocation} {
		if s == "" {
			continue
		}
		u, e := url.Parse(s)
		if e != nil || u.Scheme != base.Scheme || u.Host != base.Host || u.User != nil {
			return d, fail("CONSTRAINT_CONFLICT")
		}
	}
	if d.Issuer == "" || d.JWKS == "" {
		return d, fail("PROVIDER_FAILURE")
	}
	return d, nil
}
func (m *Manager) validateID(ctx context.Context, token, client, nonce string) (string, string, error) {
	p := strings.Split(token, ".")
	if len(p) != 3 {
		return "", "", fail("CONSTRAINT_CONFLICT")
	}
	var h struct{ Alg, Kid string }
	b, e := base64.RawURLEncoding.DecodeString(p[0])
	if e != nil || json.Unmarshal(b, &h) != nil || h.Alg != "RS256" || h.Kid == "" {
		return "", "", fail("CONSTRAINT_CONFLICT")
	}
	d, e := m.discovery(ctx)
	if e != nil {
		return "", "", e
	}
	var keys struct {
		Keys []struct{ Kty, Kid, Alg, Use, N, E string }
	}
	if e = m.getJSON(ctx, d.JWKS, &keys); e != nil {
		return "", "", e
	}
	var key *rsa.PublicKey
	for _, k := range keys.Keys {
		if k.Kid == h.Kid && k.Kty == "RSA" && (k.Alg == "" || k.Alg == "RS256") && (k.Use == "" || k.Use == "sig") {
			n, en := base64.RawURLEncoding.DecodeString(k.N)
			exp, ee := base64.RawURLEncoding.DecodeString(k.E)
			if en != nil || ee != nil || len(exp) > 4 || len(exp) == 0 || len(n) < 256 || key != nil {
				return "", "", fail("CONSTRAINT_CONFLICT")
			}
			number := 0
			for _, v := range exp {
				number = number*256 + int(v)
			}
			if number < 3 {
				return "", "", fail("CONSTRAINT_CONFLICT")
			}
			key = &rsa.PublicKey{N: new(big.Int).SetBytes(n), E: number}
		}
	}
	sig, e := base64.RawURLEncoding.DecodeString(p[2])
	hash := sha256.Sum256([]byte(p[0] + "." + p[1]))
	if key == nil || e != nil || rsa.VerifyPKCS1v15(key, crypto.SHA256, hash[:], sig) != nil {
		return "", "", fail("CONSTRAINT_CONFLICT")
	}
	var c struct {
		Issuer    string          `json:"iss"`
		Audience  json.RawMessage `json:"aud"`
		Subject   string          `json:"sub"`
		Email     string          `json:"email"`
		Nonce     string          `json:"nonce"`
		Expires   int64           `json:"exp"`
		NotBefore int64           `json:"nbf"`
	}
	b, e = base64.RawURLEncoding.DecodeString(p[1])
	if e != nil || json.Unmarshal(b, &c) != nil {
		return "", "", fail("CONSTRAINT_CONFLICT")
	}
	var aud string
	var list []string
	valid := json.Unmarshal(c.Audience, &aud) == nil && aud == client
	if !valid && json.Unmarshal(c.Audience, &list) == nil {
		for _, x := range list {
			valid = valid || x == client
		}
	}
	if !valid || c.Issuer != d.Issuer || c.Subject == "" || c.Expires <= m.Now().Unix() || c.NotBefore > m.Now().Unix() || (nonce != "" && c.Nonce != nonce) {
		return "", "", fail("CONSTRAINT_CONFLICT")
	}
	return c.Subject, c.Email, nil
}
