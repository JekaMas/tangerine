package source

import (
	"bufio"
	"fmt"
	"io"
	"unicode/utf16"
	"unicode/utf8"
)

// Decode only the incoming stream. Accepted raw bytes are stored separately;
// neither resume nor readback repeats this admission.
type nativeTextReader struct {
	r        *bufio.Reader
	encoding string
	first    bool
	pending  []byte
}

func textReader(r io.Reader, encoding string) (io.Reader, error) {
	switch encoding {
	case "", "utf-8", "utf-8-sig", "utf-16le", "utf-16be":
	default:
		return nil, fmt.Errorf("unsupported documented encoding")
	}
	return &nativeTextReader{r: bufio.NewReaderSize(r, 65536), encoding: encoding, first: true}, nil
}
func (n *nativeTextReader) unit() (uint16, error) {
	var b [2]byte
	_, e := io.ReadFull(n.r, b[:])
	if e != nil {
		return 0, e
	}
	if n.encoding == "utf-16be" {
		return uint16(b[0])<<8 | uint16(b[1]), nil
	}
	return uint16(b[0]) | uint16(b[1])<<8, nil
}
func (n *nativeTextReader) Read(p []byte) (int, error) {
	if len(p) == 0 {
		return 0, nil
	}
	if len(n.pending) > 0 {
		count := copy(p, n.pending)
		n.pending = n.pending[count:]
		return count, nil
	}
	if n.encoding != "utf-16le" && n.encoding != "utf-16be" {
		// Return a complete block; retain a partial trailing rune for the next read.
		b, e := n.r.Peek(32768)
		if len(b) == 0 {
			return 0, e
		}
		size := len(b)
		if size > len(p) {
			size = len(p)
		}
		for i := 0; i < size; {
			r, w := utf8.DecodeRune(b[i:size])
			if r == utf8.RuneError && w == 1 {
				if !utf8.FullRune(b[i:size]) && (size < len(b) || len(b) == 32768) {
					size = i
					break
				}
				return 0, fmt.Errorf("invalid UTF-8")
			}
			i += w
		}
		if size == 0 {
			r, z, e := n.r.ReadRune()
			if e != nil {
				return 0, e
			}
			if r == utf8.RuneError && z == 1 {
				return 0, fmt.Errorf("invalid UTF-8")
			}
			n.pending = utf8.AppendRune(nil, r)
			return n.Read(p)
		}
		if !utf8.Valid(b[:size]) {
			return 0, fmt.Errorf("invalid UTF-8")
		}
		return n.r.Read(p[:size])
	}
	u, e := n.unit()
	if e != nil {
		if e == io.ErrUnexpectedEOF {
			e = fmt.Errorf("odd UTF-16 byte count")
		}
		return 0, e
	}
	if n.first {
		n.first = false
		if u == 0xfeff {
			return n.Read(p)
		}
	}
	r := rune(u)
	if u >= 0xd800 && u <= 0xdbff {
		v, e := n.unit()
		if e != nil || v < 0xdc00 || v > 0xdfff {
			return 0, fmt.Errorf("unpaired UTF-16 surrogate")
		}
		r = utf16.DecodeRune(r, rune(v))
	} else if u >= 0xdc00 && u <= 0xdfff {
		return 0, fmt.Errorf("unpaired UTF-16 surrogate")
	}
	n.pending = utf8.AppendRune(nil, r)
	return n.Read(p)
}
