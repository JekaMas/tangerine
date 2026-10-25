// One range on the existing stored recording. No synthesis, encoding or scoring.
export function createPassageReplay(audio) {
  let range = null, starting = false, expectedSeek = null;
  const cancel = () => { range = null; expectedSeek = null; };
  const time = () => {
    if (range && audio.currentTime >= range.end) { cancel(); audio.pause(); }
  };
  const seek = () => {
    if (expectedSeek != null && Math.abs(audio.currentTime - expectedSeek) < .05) { expectedSeek = null; return; }
    cancel();
  };
  const play = () => { if (!starting) cancel(); };
  audio.addEventListener('timeupdate', time);
  audio.addEventListener('seeking', seek);
  audio.addEventListener('play', play);
  audio.addEventListener('pause', cancel);
  audio.addEventListener('ended', cancel);
  audio.addEventListener('error', cancel);
  return {
    async replay(interval) {
      cancel();
      range = {end: interval.end_ms / 1000};
      expectedSeek = interval.start_ms / 1000;
      starting = true;
      audio.currentTime = expectedSeek;
      try { await audio.play(); } catch (error) { cancel(); throw error; }
      finally { starting = false; }
    },
    cancel,
    dispose() {
      cancel();
      for (const [event, listener] of [['timeupdate',time],['seeking',seek],['play',play],['pause',cancel],['ended',cancel],['error',cancel]]) audio.removeEventListener(event,listener);
    },
  };
}

export function passageTime(ms) {
  const seconds = ms / 1000;
  return `${Math.floor(seconds / 60)}:${(seconds % 60).toFixed(2).padStart(5,'0')}`;
}
