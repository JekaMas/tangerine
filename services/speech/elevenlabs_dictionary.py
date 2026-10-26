"""ElevenLabs pronunciation planning and wire format; no audio/storage ownership."""
import base64
import copy
import json
import os
import urllib.parse
import uuid
import xml.etree.ElementTree as ET

PHONE_MODELS = {'eleven_flash_v2', 'eleven_v3', 'eleven_v4'}


def credentials(profile):
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        raise ValueError('MISSING_CREDENTIALS')
    return (profile.get('endpoint') or 'https://api.elevenlabs.io').rstrip('/'), key


def create(profile, text, ipa, locale, send):
    """Admit a new provider locator once, then keep it in the saved piece plan."""
    root = ET.Element('lexicon', {'version': '1.0',
                                 'xmlns': 'http://www.w3.org/2005/01/pronunciation-lexicon',
                                 'alphabet': 'ipa', 'xml:lang': locale})
    lexeme = ET.SubElement(root, 'lexeme')
    ET.SubElement(lexeme, 'grapheme').text = text
    ET.SubElement(lexeme, 'phoneme').text = ipa
    pls = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    boundary = 'tangerine-' + uuid.uuid4().hex
    name = 'Tangerine ' + text
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="name"\r\n\r\n{name}\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="pronunciation.pls"\r\n'
            'Content-Type: application/pls+xml\r\n\r\n').encode() + pls + f'\r\n--{boundary}--\r\n'.encode()
    base, key = credentials(profile)
    url = base + '/v1/pronunciation-dictionaries/add-from-file'
    raw, status = send(url, body, {'xi-api-key': key, 'Content-Type': 'multipart/form-data; boundary=' + boundary}, 260)
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or any(not isinstance(value.get(k), str) or not value[k].strip()
                                              for k in ('id', 'version_id')):
            raise ValueError('PROVIDER_FAILED')
    except (ValueError, TypeError, UnicodeError):
        raise ValueError('PROVIDER_FAILED') from None
    return {'locator': {'pronunciation_dictionary_id': value['id'], 'version_id': value['version_id']},
            'pls_base64': base64.b64encode(pls).decode(), 'url': url, 'http_status': status,
            'response': value}


def plan(profile, render_plan, text_plan, send):
    """Keep target occurrences in their own pieces so word rules cannot leak."""
    from acoustic_plan import scopes
    partition = [(t, scopes(t)) for t in render_plan['turns']]
    # Check requested capabilities before creating any external dictionaries.
    for _, segments in partition:
        for _, _, _, edits in segments:
            for edit in edits:
                p = edit['parameters']
                if edit['controller'] in ('vot_edit', 'vowel_duration') or edit['controller'] != 'phone_pair' and p.get('phone_start') is not None:
                    raise ValueError('CAPABILITY_UNAVAILABLE')
                if edit['controller'] == 'phone_pair' and profile['model'] not in PHONE_MODELS:
                    raise ValueError('CAPABILITY_UNAVAILABLE')
    pieces = []
    for turn, segments in partition:
        for surface, a, b, edits in segments:
            source = copy.deepcopy(turn)
            source.pop('acoustic_edits', None)
            source['operations'] = [{'kind': 'text', 'text': surface}]
            packet = text_plan(profile, {'turns': [source]})
            if edits and len(packet['pieces']) != 1:
                raise ValueError('INPUT_CAPACITY_EXCEEDED')
            cursor = a
            for piece in packet['pieces']:
                end = cursor + sum(len(op['text']) for op in piece['operations'])
                piece['surface_scope'] = {'start': cursor, 'end': end}
                cursor = end
                piece['gap_after_ms'] = turn['gap_after_ms'] if b == sum(len(op['text']) for op in turn['operations']) and piece is packet['pieces'][-1] else 0
                if edits:
                    piece['acoustic_edits'] = edits
                    pair = next((e for e in edits if e['controller'] == 'phone_pair'), None)
                    if pair:
                        bindings = {name: create(profile, surface, pair['parameters'][name + '_ipa'], turn['locale'], send)
                                    for name in ('reference', 'mutated')}
                        piece['pronunciation_dictionary_bindings'] = bindings
                        piece['pronunciation_dictionary_locators'] = [bindings['reference']['locator']]
                pieces.append(piece)
    return {'pieces': pieces, 'model_context': {'adapter': 'elevenlabs-dictionary-v1', 'model': profile['model']}}


def request(profile, turn):
    """Compile the selected transport from the trusted, saved piece binding."""
    base, key = credentials(profile)
    if any(op['kind'] not in ('text', 'phoneme') for op in turn['operations']):
        raise ValueError('CAPABILITY_UNAVAILABLE')
    text = ''.join(op['text'] for op in turn['operations'])
    model = profile['model']
    if model in ('eleven_v3', 'eleven_v4'):
        payload = {'inputs': [{'text': text, 'voice_id': turn['voice_id']}], 'model_id': model}
        url = base + '/v1/text-to-dialogue?output_format=mp3_44100_128'
    else:
        payload = {'text': text, 'model_id': model,
                   'voice_settings': {k: v for k, v in profile.get('voice_settings', {}).items() if v is not None}}
        url = base + '/v1/text-to-speech/' + urllib.parse.quote(turn['voice_id'], safe='') + '?output_format=mp3_44100_128'
    if turn.get('pronunciation_dictionary_locators'):
        payload['pronunciation_dictionary_locators'] = turn['pronunciation_dictionary_locators']
    elif any(op['kind'] == 'phoneme' for op in turn['operations']):
        raise ValueError('CAPABILITY_UNAVAILABLE')
    return url, json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), {'xi-api-key': key, 'Content-Type': 'application/json'}
