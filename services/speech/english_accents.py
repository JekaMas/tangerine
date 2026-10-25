"""Explicit local voice routing; no provider/configuration fallback."""
import copy
from accent_phones import route_voice

def voice_profile(profile,voice):
 provider,locale,_=route_voice(voice)
 p=copy.deepcopy(profile);p['provider']=provider;p['adapter_version']='kokoro-controlled-v1' if provider=='local_kokoro' else 'melo-controlled-v1';p['model']='hexgrad/Kokoro-82M' if provider=='local_kokoro' else 'myshell-ai/MeloTTS-English'
 p['voices']=[v for v in p['voices'] if v['id']==voice and v['locale']==locale]
 if not p['voices']:raise ValueError('VOICE_UNAVAILABLE')
 return p

def plan(profile,render_plan,text_plan):
 pieces=[];models={}
 for turn in render_plan['turns']:
  p=voice_profile(profile,turn['voice_id']);packet=text_plan(p,{'turns':[turn]});pieces.extend(packet['pieces']);models[p['provider']]=packet['model_context']
 return {'pieces':pieces,'model_context':{'models':models}}
