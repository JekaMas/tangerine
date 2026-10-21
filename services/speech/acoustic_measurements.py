"""Native F0/formants and release/onset proposals. No transforms or inference."""
import math
import numpy as np
RATE=24000

def pitch_ac(sound):
    return sound.to_pitch_ac(time_step=.01,pitch_floor=60,pitch_ceiling=500,max_number_of_candidates=15,very_accurate=True,silence_threshold=.03,voicing_threshold=.45,octave_cost=.01,octave_jump_cost=.35,voiced_unvoiced_cost=.14)

class Unmeasurable(ValueError):
    def __init__(self,reason,observations=None):
        super().__init__("ACOUSTIC_NOT_MEASURABLE");self.reason=reason;self.observations=observations or {}

def features(values):
    import parselmouth
    if len(values)==0:return {"state":"not_measurable","reason":"empty_interval","median_f0_hz":None,"voiced_frames":0,"pitch_points":[],"formant_medians_hz":[None]*3,"sample_count":0,"praat_version":parselmouth.PRAAT_VERSION}
    sound = parselmouth.Sound(values, RATE)
    try:
        pitch = pitch_ac(sound)
        f0 = pitch.selected_array['frequency']; voiced = f0[f0 > 0]
        points = [{'fraction': float(t / sound.duration), 'semitones': float(12 * np.log2(f / 100))}
                  for t, f in zip(pitch.xs(), f0) if f > 0]
        median = float(np.median(voiced)) if len(voiced) else None
        eligible=f0>0;semitones=12*np.log2(voiced/100) if len(voiced) else np.array([])
        times=pitch.xs()[eligible]
        prosody={'f0_range_semitones':None,'f0_slope_semitones_per_second':None,'state':'not_measurable','reason':'fewer_than_20_voiced_frames'}
        if len(voiced)>=20 and np.var(times)>0:
            prosody={'f0_range_semitones':float(np.percentile(semitones,95)-np.percentile(semitones,5)),
                     'f0_slope_semitones_per_second':float(np.polyfit(times,semitones,1)[0]),'state':'measured','reason':None}
        formant = sound.to_formant_burg(time_step=.01)
        formants = []
        for n in (1, 2, 3):
            rows = [formant.get_value_at_time(n, t) for t in pitch.xs()]
            rows = [r for r in rows if math.isfinite(r)]
            formants.append(float(np.median(rows)) if rows else None)
        return {'state': 'measured' if len(voiced) else 'not_measurable', 'reason': None if len(voiced) else 'no_voiced_frames',
                'prosody':prosody,'median_f0_hz': median, 'voiced_frames': int(len(voiced)), 'pitch_points': points,
                'formant_medians_hz': formants, 'sample_count': len(values), 'praat_version': parselmouth.PRAAT_VERSION}
    except parselmouth.PraatError:
        return {'state': 'not_measurable', 'reason': 'interval_too_short', 'median_f0_hz': None,
                'voiced_frames': 0, 'pitch_points': [], 'formant_medians_hz': [None] * 3, 'sample_count': len(values), 'praat_version': parselmouth.PRAAT_VERSION}


def vot_landmarks(values, search_interval=None):
    """Retain deterministic burst/F0/pulse proposal, not a perceived phoneme."""
    import parselmouth
    from parselmouth.praat import call
    sound = parselmouth.Sound(values, RATE)
    try:
        pitch = pitch_ac(sound)
        f0 = pitch.selected_array['frequency']; times = pitch.xs()
        pulses = call([sound, pitch], 'To PointProcess (cc)')
        pulse_times = [call(pulses, 'Get time from index', n) for n in range(1, call(pulses, 'Get number of points') + 1)]
        onset = next((round(times[n] * RATE) for n in range(len(f0) - 2) if all(f0[n:n + 3] > 0) and sum(times[n] <= t <= times[n + 2] for t in pulse_times) >= 2), None)
        if onset is None: raise Unmeasurable('no_periodic_onset')
        # Sliding 10ms energies, restricted strictly before the periodic onset.
        win = 240
        energy = np.convolve(values * values, np.ones(win) / win, mode='valid')
        if onset <= win or len(energy) < onset: raise Unmeasurable('no_prevoicing_search_interval')
        delta = energy[win:onset] - energy[:onset - win]
        if search_interval is not None:
            lo,hi=search_interval
            indices=np.arange(win,onset)
            delta=np.where((indices>=lo)&(indices<hi),delta,-np.inf)
        if not len(delta) or not np.isfinite(delta.max()) or delta.max() <= 0: raise Unmeasurable('no_release_energy_rise')
        edge = int(np.argmax(delta)) + win
        lo, hi = max(0, edge - win), min(onset, edge + win)
        if search_interval is not None:lo,hi=max(lo,search_interval[0]),min(hi,search_interval[1])
        if lo>=hi:raise Unmeasurable('no_aligned_release_interval')
        burst = lo + int(np.argmax(np.abs(values[lo:hi])))
        # A steady vowel has cyclic energy rises too. A release needs an actual
        # transient above the following periodic edge envelope, allowing the
        # two-PCM-LSB uncertainty of a first difference.
        burst_end = burst + 120
        selected_f0 = f0[f0 > 0]
        period = RATE / float(np.median(selected_f0))
        periodic=values[onset:min(len(values),onset+round(3*period))]
        transient_edge=float(np.max(np.abs(np.diff(values[lo:hi])))) if hi-lo>1 else 0
        periodic_edge=float(np.max(np.abs(np.diff(periodic)))) if len(periodic)>1 else 0
        if transient_edge<=periodic_edge+2/32768:raise Unmeasurable('no_release_transient_above_periodic_signal')
        if not burst < burst_end < onset or onset - burst_end < period:
            raise Unmeasurable('insufficient_aspiration_interval', {'burst_sample': burst, 'burst_end_sample': burst_end, 'voicing_onset_sample': onset})
        return {'burst_sample': burst, 'burst_end_sample': burst_end, 'voicing_onset_sample': onset,
                'measured_vot_ms': (onset - burst) / 24, 'period_samples': period,
                'pulse_times_seconds': pulse_times, 'f0_times_seconds': times.tolist(), 'f0_hz': f0.tolist(),
                'transient_edge_amplitude':transient_edge,'periodic_edge_amplitude':periodic_edge,
                'method': 'release_energy_10ms_periodic_f0_pulses_v2'}
    except parselmouth.PraatError as e:
        raise Unmeasurable('vot_praat_unavailable') from e

