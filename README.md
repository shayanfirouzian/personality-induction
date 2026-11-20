# The Parametric Soul: Personality Induction in LLMs

**Manuscript:** *The Parametric Soul: Advancing Psychological Realism in LLMs through Multi-Trait Personality Induction via Parametric Adaptation*  
**Journal submission:** Applied Soft Computing Journal  
**Manuscript number:** ASOC-D-26-15145  
**Authors:** Shayan Firouzian-Haji and Maryam Ramezani

## Scope

This repository accompanies the study of parametric personality induction in Llama-family language models. It contains the analysis-ready experimental records retained in the project archive, corrected profile checkpoint metadata, assessment prompts and scoring key, and scripts for reproducing the reported aggregate personality-score and classification analyses.

The final experiment covers eight binary profiles across **three** Five-Factor Model dimensions: Extraversion (E), Neuroticism (N), and Openness (O). Profile identifiers are ordered E-N-O; for example, `HLH` means high Extraversion, low Neuroticism, and high Openness. This is not a full five-domain profile induction.

## Repository map

```text
.
├── configs/                         # Reported DPO, surrogate-HPO, main-HPO and SFT settings
├── data/
│   ├── dpo/                         # DPO evaluation metrics
│   ├── hpo/                         # Surrogate and main HPO trial records and JSON logs
│   ├── personality_assessment/      # Questionnaire, prompts' response differences, scores and key
│   └── sft/                         # Eight profile training logs and run summary
├── derived/                         # Reproduced summary statistics and classification outputs
├── figures/                         # Static supplementary figures and archived interactive plots
├── prompts/                         # Exact baseline and deliberation prompt templates
├── scripts/                         # Scoring and aggregate-analysis scripts
├── CITATION.cff
├── LICENSE
└── DATA_LICENSE.md
```

## Key results

- Eight profile-specific models were assessed with ten administrations each of the 120-item IPIP-NEO-120.
- The retained aggregate score file contains 80 administration-level records.
- With thresholds E = 3.33, N = 2.75 and O = 2.83, the profile classification reproduces **71/80 = 88.75%** accuracy and the manuscript confusion matrix.
- The DPO run used 3,056 training and 764 evaluation examples (80/20), 3 epochs and 573 steps. The lowest supplied validation loss is 0.623164 at step 192.
- Main-task HPO trial 5 has validation loss 0.280343 and yields the reported final configuration (per-device batch 4, gradient accumulation 32, effective batch 128, learning rate approximately 1.22e-4, weight decay approximately 0.0054; warmup ratio 0.15).

## Reproduce the analysis

Python 3.10+ is sufficient for the scoring and CSV analysis scripts; they use the standard library only.

```bash
python scripts/reproduce_analysis.py
```

The default command reads `data/personality_assessment/trait_scores_long.csv` and writes profile summaries, the confusion matrix, profile metrics, trait metrics, and the 80 individual predictions to `derived/`.

To score a complete 120-response assessment, prepare a JSON file with a `responses` array of 120 integer Likert responses (1–5) in questionnaire order and run:

```bash
python scripts/score_ipip120.py my_responses.json --output scored.json
```

Regenerate the static supplementary figures from the supplied CSV and JSON records with `python scripts/reproduce_figures.py`. This requires Matplotlib and NumPy.

The implementation applies the Maples et al. (2014)-adapted item key specified in `data/personality_assessment/maples_adapted_scoring_key.csv`. Reverse-keyed responses are recoded as `6 - response`; scores are returned as means on the original 1–5 response metric.

## Data provenance and access

The underlying personality dialogue source is BIG5-CHAT (Li et al., 2025). The author-maintained copy referenced for this study is `shayanfirouzian/big5`: <https://huggingface.co/datasets/shayanfirouzian/big5>.

The DPO preference source is `ProlificAI/social-reasoning-rlhf`; an author-maintained backup is `shayanfirouzian/SocialReasoning_DPO`:

- <https://huggingface.co/datasets/ProlificAI/social-reasoning-rlhf>
- <https://huggingface.co/datasets/shayanfirouzian/SocialReasoning_DPO>

Third-party datasets and model weights are **not redistributed** in this repository. Obtain them from their source repositories and comply with their respective licences and access conditions. The HPO used `LLLLL`, the alphabetically last member of the initial 32 binary five-trait subsets, as a fixed convenience sample across both searches (ceteris paribus); it was not one of the final three-trait target profiles.

## Contents and reproducibility boundaries

- Eight final SFT JSON logs are provided. The `best_model_checkpoint` path in each JSON has been normalised to match its profile-specific filename and recorded best step. Checkpoint weights themselves are not included.
- DPO evaluation metrics supplied for the study are provided in CSV, alongside the DPO configuration.
- Surrogate-task and main-task HPO trial tables are provided in CSV, with the retained per-trial JSON logs supplied alongside them.
- Personality-assessment records contain ten aggregate trait-score observations for each profile. The baseline-versus-deliberation comparison file records the 70 questionnaire items whose numeric ratings changed; unchanged ratings are not repeated in that differential file.
- The repository scripts reproduce the aggregate scoring and classification analyses. The manuscript and `configs/sft_reported_configuration.json` document the reported final SFT settings; model checkpoint weights are referenced at their source rather than redistributed.

## Safety and intended use

The study concerns controlled research simulation. Models derived from refusal-modified checkpoints should not be assumed suitable for unrestricted public deployment. Researchers should maintain appropriate safeguards and comply with model-provider terms and applicable institutional requirements.

## Citation

Please cite the associated manuscript. A `CITATION.cff` file is included; update it with the final publication DOI and bibliographic details if the article is accepted.
