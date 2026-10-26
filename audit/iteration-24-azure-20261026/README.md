# Azure F0 comparison and resume

This developer comparison preserves the original four car-insurance turns from
preparation `9dbf8c95-51a3-4c0f-9395-b3a77a824d22`. `material.json` is an unchanged
copy of the saved common material. It is versioned so the tests also work in a
fresh checkout. It does not replace the user's saved exercise.

`compare.py` prepares a reference variant and a variant with the four saved IPA
mutations. The existing production `backends.render` owns billing admission,
SSML compilation, actual transport, audio normalization and the native receipt.
The helper owns only the frozen comparison, per-turn persistence and assembly.
`player.py` serves the two complete WAVs and public comparison text on loopback.
It has no synthesis endpoint. Tests use the existing local speech image.

## Access prerequisite

Microsoft sign-in is waiting for the user's passkey/security-window step in the
opened Azure tab. Finish that step first. Then inspect the **actual** selected
Speech resource: its location, SKU `F0`, key, available voices and remaining free
allowance. A profile labelled `F0` does not establish an account entitlement.
No usable Azure key/region/resource was found in this installation on October 26.
That observation does not establish that the user has no resource elsewhere.

Do not start a trial, add payment details, link billing, select `S0` or switch
providers. If Microsoft requires any of those actions, stop and retain the access
blocker. No paid exception is authorized. Save the observed resource metadata as
`data/iteration-24-azure-20261026/resource.json` and keep the key only in ignored
private configuration/environment. Never include it in reports, commands or
screenshots. Inspect the account's actual access before synthesis.

## Run with qualified access

With the actual key already available as `AZURE_SPEECH_KEY` in the existing
ignored `.env`, use the already installed speech image; no install is required:

```sh
docker run --rm --env-file .env \
  -v "$PWD:/repo:ro" \
  -v "$PWD/data/iteration-24-azure-20261026:/evidence" \
  -w /repo tangerine-local-speech:local \
  python -B audit/iteration-24-azure-20261026/compare.py \
  --resource /evidence/resource.json --out /evidence/live
```

This command makes up to eight necessary requests: four turns per variant. It
does not try another provider or purchase quota. A failed request stops the
command. Completed native responses and WAV pieces remain saved. Resume using
the same command and output directory: the frozen `plan.json` is reused, saved
WAVs are trusted, and a saved accepted response can restore a missing WAV without
another provider call. A changed voice/resource/target plan belongs in a new
output directory. This is ordinary persistence, with no repeated stored-data
consistency audit.

The native request journal retains the exact SSML, nonsecret endpoint, response
and failure observations; it records only whether the credential header was
present. The key value is not recorded. The journal and native responses remain
in ignored data. Assembly preserves turn order and adds the original 300 ms gap
after each turn, including the final turn.

```sh
python3 -B audit/iteration-24-azure-20261026/player.py \
  --output data/iteration-24-azure-20261026/live
```

Open the printed loopback URL. Its port is assigned by the OS to avoid disturbing
the existing comparison servers. Listen to both complete recordings, inspect
each selected target and retain actual playback/target observations. The accent,
voice and IPA labels describe requests; they do not prove what the audio contains.
Do not use the constructed `controlled/` PCM fixtures as Azure voice evidence.

## Exact completion selection

```sh
python3 -B .agents/workflow/scripts/requirement_tests.py --root . \
  --change implement-teacher-error-trainer run \
  --properties FIN-AZURE.P1,FIN-VERIFY.I24 \
  --require-clean --output data/iteration-24-azure-20261026/clean.json
```

It currently reports incomplete: the actual Azure pair and full playback review
are skipped with their access/media reasons. An exit-zero unittest command with
those skips is not iteration acceptance. Keep I24 tasks unchecked until the
real recordings, target observations and UI review satisfy the selected scope.
