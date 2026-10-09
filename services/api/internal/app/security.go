package app

import (
	"errors"
	"net/url"
)

func ValidateOrigin(origin string) error {
	u, err := url.Parse(origin)
	if err != nil || u.Scheme != "http" || u.Host != "localhost:3000" || u.User != nil || u.Path != "" || u.RawQuery != "" || u.Fragment != "" {
		return errors.New("APP_ORIGIN must be http://localhost:3000")
	}
	return nil
}
