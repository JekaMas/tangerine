package source

import (
	"encoding/binary"
	"fmt"
	"io"
)

// WaveInfo observes the newly submitted source clock; it does not resample or
// infer acoustic content. Stored metadata is reused without reopening the audio.
func WaveInfo(r io.ReadSeeker) (map[string]any, error) {
	total, e := r.Seek(0, io.SeekEnd)
	if e != nil {
		return nil, e
	}
	if _, e := r.Seek(0, 0); e != nil {
		return nil, e
	}
	var h [12]byte
	if _, e := io.ReadFull(r, h[:]); e != nil {
		return nil, e
	}
	if string(h[:4]) != "RIFF" || string(h[8:]) != "WAVE" {
		return nil, fmt.Errorf("not PCM WAVE")
	}
	var channels, bits uint16
	var rate uint32
	var frames uint64
	found := false
	for {
		var c [8]byte
		if _, e := io.ReadFull(r, c[:]); e != nil {
			if e == io.EOF {
				break
			}
			return nil, e
		}
		size := int64(binary.LittleEndian.Uint32(c[4:]))
		at, e := r.Seek(0, io.SeekCurrent)
		if e != nil {
			return nil, e
		}
		if size > total-at {
			return nil, io.ErrUnexpectedEOF
		}
		switch string(c[:4]) {
		case "fmt ":
			if size < 16 {
				return nil, fmt.Errorf("invalid WAVE fmt")
			}
			var b [16]byte
			if _, e := io.ReadFull(r, b[:]); e != nil {
				return nil, e
			}
			if binary.LittleEndian.Uint16(b[:2]) != 1 {
				return nil, fmt.Errorf("unsupported source WAVE encoding retained raw")
			}
			channels = binary.LittleEndian.Uint16(b[2:])
			rate = binary.LittleEndian.Uint32(b[4:])
			bits = binary.LittleEndian.Uint16(b[14:])
			if _, e := r.Seek(size-16, io.SeekCurrent); e != nil {
				return nil, e
			}
		case "data":
			if channels == 0 || bits == 0 || rate == 0 {
				return nil, fmt.Errorf("missing source WAVE format")
			}
			block := uint64(channels) * uint64(bits) / 8
			if block == 0 || uint64(size)%block != 0 {
				return nil, fmt.Errorf("invalid WAVE block count")
			}
			frames = uint64(size) / block
			found = true
			if _, e := r.Seek(size, io.SeekCurrent); e != nil {
				return nil, e
			}
		default:
			if _, e := r.Seek(size, io.SeekCurrent); e != nil {
				return nil, e
			}
		}
		if size%2 != 0 {
			if _, e := r.Seek(1, io.SeekCurrent); e != nil {
				return nil, e
			}
		}
	}
	if !found || frames == 0 {
		return nil, fmt.Errorf("missing/empty source WAVE data")
	}
	return map[string]any{"sample_rate_hz": rate, "channels": channels, "bits_per_sample": bits, "sample_count": frames}, nil
}
