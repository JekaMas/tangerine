import {createPassageReplay} from '../listen/passageReplay.js';

const unavailable='This recording is unavailable right now. Retry playback; your source files are retained.';

// One owner for all saved source recordings. Reload only the same admitted
// asset, retain its range/position, and never synthesize or re-import on failure.
export function createSourcePlayback(audio,{
  publish=()=>{},log=value=>console.warn('Tangerine source playback',value),
  schedule=(fn,ms)=>setTimeout(fn,ms),unschedule=id=>clearTimeout(id),
}={}) {
  const passage=createPassageReplay(audio);
  let active=true,intent=null,attempts=0,timer=null,recovering=false,ticket=0,expectedSeek=null;
  const cancelTimer=()=>{if(timer!=null)unschedule(timer);timer=null};
  const clear=()=>publish({error:'',loading:false});
  async function start(current) {
    try {
      if(!intent)return;
      expectedSeek=intent.time;
      if(intent.interval)await passage.replay({...intent.interval,start_ms:intent.time*1000});
      else {audio.currentTime=intent.time;await audio.play()}
    } catch(error) {
      // A media error has its own single retry owner below. load()/replacement
      // can abort an obsolete play promise; neither is a second failure.
      if(!active||current!==ticket||audio.error||error?.name==='AbortError')return;
      recovering=false;
      log({outcome:'play_unavailable',kind:error?.name});
      publish({loading:false,error:error?.name==='NotAllowedError'?'Select Play to resume this recording.':unavailable});
    }
  }
  function failed() {
    if(!active||timer!=null||audio.error?.code===1)return;
    if(intent&&Number.isFinite(audio.currentTime)&&audio.currentTime>intent.time)intent.time=audio.currentTime;
    passage.cancel();attempts++;
    log({outcome:'media_unavailable',code:audio.error?.code??null,attempt:attempts});
    if(attempts>=3){recovering=false;publish({loading:false,error:unavailable});return}
    recovering=true;publish({loading:true,error:''});
    const current=ticket;
    timer=schedule(()=>{
      timer=null;if(!active||current!==ticket)return;
      audio.load();void start(current);
    },attempts===1?160:480);
  }
  function play(){if(!intent)intent={time:audio.currentTime};clear()}
  function playing(){attempts=0;recovering=false;cancelTimer();clear()}
  function pause(){if(!recovering&&!audio.error&&audio.paused){intent=null;expectedSeek=null;ticket++;cancelTimer()}}
  function seek(){
    if(expectedSeek!=null&&Math.abs(audio.currentTime-expectedSeek)<.05)return;
    // Ordinary seeking cancels the finite range in passageReplay as well.
    intent={time:audio.currentTime};expectedSeek=null;
  }
  function seeked(){if(!audio.seeking)expectedSeek=null}
  function ready(){if(!intent){attempts=0;recovering=false;clear()}}
  const listeners=[['error',failed],['play',play],['playing',playing],['pause',pause],['seeking',seek],['seeked',seeked],['loadeddata',ready]];
  for(const [event,listener] of listeners)audio.addEventListener(event,listener);
  return {
    replay(interval){
      cancelTimer();ticket++;attempts=0;recovering=false;
      intent={interval,time:interval.start_ms/1000};clear();
      // A terminal media error needs load() before another play can succeed.
      if(audio.error){recovering=true;audio.load()}
      return start(ticket);
    },
    retry(){
      cancelTimer();ticket++;attempts=0;recovering=true;clear();
      audio.load();return start(ticket);
    },
    dispose(){
      active=false;ticket++;cancelTimer();
      for(const [event,listener] of listeners)audio.removeEventListener(event,listener);
      passage.dispose();audio.pause();
    },
  };
}
