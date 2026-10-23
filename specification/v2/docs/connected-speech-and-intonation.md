# Connected speech, rhythm and intonation

These features use the existing pronunciation leaves and saved acoustic controls; they add no category, public API, human review or corpus prerequisite. A generated item declares its audible/visible context, permitted pronunciation variants, requested contrast and correction in the saved answer key. Connected speech itself is often correct. A teacher answer identifying a permitted natural variant must not be counted as a missed error or false correction solely because it differs from careful speech.

| Requested feature | Existing category and control | Concrete contrast and accepted control |
| --- | --- | --- |
| Rhythm | `pronunciation.suprasegmental.rhythm`, scoped `pitch_duration` | Stretch a selected weak interval to 1.5 times its reference duration while preserving the remaining words. A different overall pace or accent is not automatically a rhythm error. |
| Blending / coalescence | `pronunciation.suprasegmental.assimilation`, full-phrase `phone_pair` | “Would you”: permitted /wʊd ju/ and /wʊdʒə/; deliberate faulty blend /wʊtʃə/ changes the voiced boundary to a voiceless affricate. Also cover /t+j/ → /tʃ/ in “don't you”; neither normal blending nor clear unblended speech is intrinsically wrong. |
| Contextual assimilation | Same assimilation leaf, full-phrase `phone_pair` | “ten bags”: /tɛn bæɡz/ and /tɛm bæɡz/ are permitted; /tɛŋ bæɡz/ is a constructed inappropriate place change in this context. The exact contrast and alternatives belong to the unit. |
| Linking / resyllabification | `pronunciation.suprasegmental.linking_resyllabification`, `phone_pair` | “turn it off”: smooth consonant-to-vowel transitions versus intrusive breaks in an explicit linking task. Acceptable careful non-linked speech is a control; loss of linking alone is not universally an error. |
| Weak forms | `pronunciation.suprasegmental.weak_form`, `phone_pair` | Neutral unstressed “to be”: /tə bi/ versus full emphatic /tuː bi/. A genuinely contrastive strong form is permitted in its own audible context. |
| Elision / reduction | `pronunciation.suprasegmental.elision_reduction`, `phone_pair` | “documents, not one document”: preserve the plural contrast. Ordinary /t/ elision retaining plural /s/ is a control; deleting the whole plural-bearing ending can lose the stated distinction. |
| Thought groups | `pronunciation.suprasegmental.thought_group_chunking`, `pause_insert` | An intrusive pause inside “the policy” versus an acceptable clause boundary. Pause location matters, not merely the presence of silence. |
| Question / statement meaning | `intonation_function`, scoped `pitch_duration` | The same words “You have car insurance.” / “You have car insurance?” can express a statement or confirmation question through different contours. Context/function and actual audio, not the punctuation character alone, determine the expected contrast. |
| Other contours | `intonation_contour`, scoped `pitch_duration` | Rising, falling, fall–rise and rise–fall are available. Ordinary information-seeking wh-questions often fall; polite/uncertain questions and statements can fall–rise. Alternative and tag questions require their own audible context. |

## Source-relative templates

For the two existing intonation leaves only, these named `pitch_points` shapes are resolved after source synthesis. Values are semitone offsets from the measured source median F0; fractions select ordered voiced-frame quantiles within the selected phrase/phone interval. Resolution maps those quantiles to actual source times, so the contour does not finish in a silent or unvoiced tail:

- Rise: `(0, 0), (1, +5)` (existing behavior).
- Fall: `(0, 0), (1, -5)`.
- Fall–rise: `(0, 0), (0.5, -3), (1, +3)`.
- Rise–fall: `(0, 0), (0.5, +3), (1, -3)`.

Resolution adds `12 log2(median_f0_hz / 100)` to each offset once, uses actual voiced-frame times for the named template knots, retains the existing absolute PitchTier representation and removes the relative taxonomy cue from the resolved step. Other explicitly absolute curves and other categories retain their existing semantics. Missing periodic evidence remains not measurable. These are controllable practice shapes, not fixed definitions of all English questions or all dialects. The exact target may select the final stressed word or a complete phrase; it must not rely on hidden generator facts.

A punctuation-only change or successful provider response does not establish an acoustic mutation. Native tests measure generated pitch direction and duration, while phonetic blending/assimilation requires actual audio observation. Automated audio judgments remain model opinions. No new runtime audit, automatic retry, fallback provider or publication gate is introduced.

## Providers and evidence

Controlled local Kokoro exposes the existing phone pairs, pitch/duration tiers and exact pauses. Azure's configured whole-phrase route supports its documented controls with the existing fine-timing limits. ElevenLabs dictionaries can request boundary-phone changes on compatible models; style tags/punctuation do not provide exact rhythm/F0 control. Gemini style metadata can request these features but does not guarantee them. Provider-specific tests and actual output determine the claim; category coverage never implies that every provider can render every instance.

The focused regression tests are `tests/test_connected_speech.py`. Actual local recordings, numerical observations, permitted-variant controls and any separately labelled auditory opinions are recorded in `audit/connected-speech-20261023/REPORT.md`. They do not replace the earlier full-dialogue recordings or fabricate universal perceptual accuracy.

Research basis: [British Council connected speech](https://www.teachingenglish.org.uk/professional-development/teachers/teaching-knowledge-database/c/connected-speech), [British Council /d/ + /j/ assimilation](https://africa.teachingenglish.org.uk/classroom/pronunciation/assimilation-d-and-j), [British Council connected-speech examples](https://www.britishcouncil.org/voices-magazine/pop-songs-connected-speech-fluent-english), and [Cambridge intonation](https://dictionary.cambridge.org/grammar/british-grammar/intonation). These sources explain the phenomena; they do not independently validate the generated recordings.
