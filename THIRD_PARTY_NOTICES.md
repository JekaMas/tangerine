# Third-party components and data

Tangerine's original software is Apache-2.0. Dependency source, package metadata,
model LICENSE files and corpus terms remain authoritative for their components.
Dockerfiles and lock files pin the actual downloaded releases; they are part of
this source distribution. These notices are attribution and source pointers,
not a claim that all separately distributed components share one license.

| Component | Retained source / license information |
|---|---|
| Next.js, React and Node runtime | services/web/package-lock.json and services/web/Dockerfile; upstream package LICENSE files and installed package metadata |
| Source Sans 3 | Bundled local font in services/web/public/fonts; SIL Open Font License 1.1 retained in OFL.txt; https://github.com/adobe-fonts/source-sans and https://github.com/google/fonts/tree/main/ofl/sourcesans3 |
| Go application dependencies | services/api/go.mod and go.sum; upstream module LICENSE files |
| PostgreSQL | Pinned postgres image in deploy/local/compose.yaml; https://www.postgresql.org/about/licence/ |
| MinIO | Source-built from the exact upstream commit in deploy/local/minio.Dockerfile; GNU AGPLv3; https://github.com/minio/minio/tree/7aac2a2c5b7c882e68c1ce017d8256be2feea27f |
| Python, FFmpeg, eSpeak NG and OS packages | services/speech/Dockerfile; installed /usr/share/doc copyright/license files and FFmpeg build configuration |
| Praat / praat-parselmouth | praat-parselmouth0.4.7 / Praat6.1.38, GPLv3; https://github.com/YannickJadoul/Parselmouth; exact source-distribution hashes in speech lock files |
| Kokoro / Misaki | Pinned packages and explicit model setup; https://github.com/hexgrad/kokoro and https://github.com/hexgrad/misaki; upstream model-card/license metadata at the setup manifest repo/revision |
| Qwen3-TTS | Explicit pinned model setup; https://github.com/QwenLM/Qwen3-TTS; upstream license/model-card metadata for the actual selected repo/revision |
| Qwen2.5-Omni | Explicit pinned model setup; https://github.com/QwenLM/Qwen2.5-Omni; the optional3B model uses the Qwen Research License with non-commercial terms;7B retains its own model license |
| faster-whisper / CTranslate2 | Pinned diagnostic lock files; https://github.com/SYSTRAN/faster-whisper and https://github.com/OpenNMT/CTranslate2; actual downloaded Whisper model metadata and license |
| MLflow | Pinned optional3.17.0 image/build configuration; https://github.com/mlflow/mlflow/tree/v3.17.0 |

Speech Python dependencies include PyTorch, Transformers, NumPy and SoundFile;
the complete transitive package identities and hashes are in
services/speech/requirements*.lock. License text/metadata remains in each
installed distribution rather than being replaced by this abbreviated table.
New model setup retains available upstream LICENSE files and manifests. Some accepted earlier caches have no standalone LICENSE file; their manifest repo/revision identifies the upstream model card and terms. Corpora retain
all native notices, use terms and provenance in private source imports; see
specification/v2/docs/sources/. Restricted corpora and model weights are not
bundled in the GitHub source archive. Provider-generated media follows the
selected service's terms, separate from the application license.
