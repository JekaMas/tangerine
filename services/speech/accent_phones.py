"""English phone/tone projection for the Melo English vocabulary, without I/O."""
import re,unicodedata

IPA={'tʃ':'ch','dʒ':'jh','eɪ':'ey','aɪ':'ay','ɔɪ':'oy','aʊ':'aw','oʊ':'ow','əʊ':'ow','ɪə':'ih','eə':'eh','ʊə':'uh','ɜː':'er','ɝ':'er','ɚ':'er','iː':'iy','uː':'uw','ɑː':'aa','ɔː':'ao','ɪ':'ih','i':'iy','ʊ':'uh','u':'uw','ɛ':'eh','e':'eh','æ':'ae','ɑ':'aa','ɒ':'aa','ɔ':'ao','ʌ':'ah','ə':'ah','ɜ':'er','p':'p','b':'b','t':'t','d':'d','k':'k','ɡ':'g','g':'g','f':'f','v':'V','θ':'th','ð':'dh','s':'s','z':'z','ʃ':'sh','ʒ':'zh','h':'hh','m':'m','n':'n','ŋ':'ng','l':'l','ɫ':'l','r':'r','ɹ':'r','ɾ':'t','j':'y','w':'w'}
VOWELS={'aa','ae','ah','ao','aw','ay','eh','er','ey','ih','iy','ow','oy','uh','uw'}

def ipa_phones(text):
 text=unicodedata.normalize('NFC',text).replace('͡','');result=[];stress=1;i=0
 while i<len(text):
  c=text[i]
  if c in ' /[]()':i+=1;continue
  if c in 'ˈˌ':stress=2 if c=='ˈ' else 3;i+=1;continue
  if c in '.,!?-':result.append((c,0));i+=1;continue
  key=next((s for s in sorted(IPA,key=len,reverse=True) if text.startswith(s,i)),None)
  if key is None:raise ValueError('CAPABILITY_UNAVAILABLE')
  ph=IPA[key];result.append((ph,stress if ph in VOWELS else 0))
  if ph in VOWELS:stress=1
  i+=len(key)
  # Length/nasalization are not silently discarded: they need their own
  # duration controller or an explicitly representable reference phone.
  if i<len(text) and text[i]=='ː' and key in ('ɑ','ɔ','i','u'):i+=1
 return result

def arpa_phones(values):
 result=[]
 for value in values:
  match=re.fullmatch(r'([A-Z]+)([012]?)',value)
  if not match:continue
  symbol=match[1].lower();symbol='V' if symbol=='v' else symbol
  result.append((symbol,int(match[2])+1 if match[2] else 0))
 return result

def route_voice(voice):
 if voice in ('af_heart','am_adam'):return 'local_kokoro','en-US',None
 if voice in ('bf_emma','bm_george'):return 'local_kokoro','en-GB',None
 if voice=='melo_en_au':return 'local_melo','en-AU',3
 if voice=='melo_en_in':return 'local_melo','en-IN',2
 raise ValueError('VOICE_UNAVAILABLE')
