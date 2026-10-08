# Language procedure and limits

This package uses the SimpleEnglish Strict guidance. The source revision appears in `source-lock.json`.
The reviewer read the skill, rule catalog, vocabulary guidance, word swaps, use cases, and dictionary instructions.
The reviewer also read lines 1 to 260 of the mechanical linter code. The repository does not contain the official STE dictionary.

## Prose rules

Use no more than 20 words in an instruction sentence. Use no more than 25 words in a descriptive sentence.
Use one instruction per sentence. Put the condition before the instruction.
Use active voice and simple tenses. Use complete sentences with the necessary articles.
Use one technical term for one meaning. Define the term before its first necessary use.
Do not use a semicolon or an em dash to join clauses. Do not replace facts with claims of importance.

Use `MUST` and `MUST NOT` for normative requirements. These terms preserve the force of the original requirement.
The OpenSpec headings and scenario markers are syntax, not prose. Keep them unchanged.

## Protected content

Do not change identifiers, paths, commands, enum values, numerical limits, or formulas during translation.
Do not rewrite a learner error into correct English. Do not simplify IPA or normalize a quoted teacher answer.
Keep external titles, source locators, and exact evidence bytes.
The translation register identifies these exclusions. They are necessary to preserve meaning and provenance.

Comments, descriptions, procedures, prompt instructions, and audit explanations are prose. Apply the language rules to those fields.
A technical identifier is not permission to exclude the explanatory sentence around it.
A glossary entry permits one defined technical meaning. It does not approve every ordinary use of that word.

## Mechanical check

`scripts/review_v6.py` examines the actual documents and selected prose fields.
It reports sentence length, prohibited modals, contractions, semicolons, and em dashes.
It also reports unreviewed language exceptions. It does not prove correct vocabulary sense, active voice, or semantic equivalence.
The checker does not create test recordings or synthetic teacher answers.

## Dictionary check

The official dictionary is not present in this environment. Do not mark dictionary compliance as passed.
The owner can obtain the official Issue 9 document from the ASD request page.
Use the SimpleEnglish repository instructions in `tools/ste-dictionary/README.md` on that permitted local copy.
Do not distribute the dictionary or extracted word lists without the necessary permission.

After the dictionary check, a qualified reviewer must examine word sense and technical-term use.
The current status remains `dictionary_review_required`. No tool result grants a compliance certificate.
