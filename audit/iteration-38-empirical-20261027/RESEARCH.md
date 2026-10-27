# Native-source meanings and reporting boundaries

Research checked 2026-10-27. No corpus records were sent to an external service.
Existing acquisition and import records supply exact release identities. The
following primary documents resolve meaning; no new annotation toolkit was run.

- [ERRANT owner documentation](https://github.com/chrisjbryant/errant) and
  [original ERRANT paper](https://aclanthology.org/P17-1074/): original/corrected
  pairs can produce classified edits. Reports retain the supplied BEA native tags;
  they do not run a new ERRANT version or mistake its broad tags for the entire
  Tangerine taxonomy. M/U/R mean missing/unnecessary/replacement. A determiner
  tag alone cannot distinguish every article or other determiner subtype.
- [Official L2-ARCTIC description](https://psi.engr.tamu.edu/l2-arctic-corpus/):
  manual phone annotations identify substitutions, deletions and additions. The
  manual subset includes selected difficult material; it is not a random sample
  of all learner speech. Read prompts and the Suitcase task stay separate.
- [Official CMU phone inventory](https://github.com/cmusphinx/cmudict/blob/master/cmudict.phones):
  a limited consonant/vowel class mapping supports explicitly named phone
  substitutions, consonant omissions and insertions. Unknown, approximate and
  cross-class contrasts stay unassigned. No generic vowel-omission category is
  invented. These rules do not independently verify sounds or judge an accent.

## Engineering interpretation, version native-context-1

Nine narrow writing rules map agreement, noun number, prepositions, word order
and article edits with explicit article context. Broad lexical, tense, spelling
or determiner tags remain native when a unique existing category is not justified.
Five phone rules map only the supported contrasts above. All rules and localized
event identities are saved in the immutable input. A positive mapping does not
establish complete absence annotation for that project category.

Native source frequency denominators are original eligible error events,
fully annotated source windows and their supplied native word-token counts.
Native relationships use distinct events in the same source window. Mapped
category proportions have their own smaller denominator. Correct-use opportunity
rates remain unknown without explicit opportunity observations.

JFLEG alternatives, SpeechOcean ratings and dialogue/task/ASR material support
coverage and examples, not invented localized errors. Available releases,
component/aggregate views and related DRAL versions are reported separately.
The software licence does not replace each dataset's recorded terms.
