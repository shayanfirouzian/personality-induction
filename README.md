# The Parametric Soul: Personality Induction in LLMs

## Scope

This repository accompanies the study of parametric personality induction in Llama-family language models. It contains the analysis-ready experimental records retained in the project archive, corrected profile checkpoint metadata, assessment prompts and scoring key, and scripts for reproducing the reported aggregate personality-score and classification analyses.

The final experiment covers eight binary profiles across three of the Five-Factor Model dimensions: Extraversion (E), Neuroticism (N), and Openness (O). Profile identifiers are ordered E-N-O; for example, `HLH` means high Extraversion, low Neuroticism, and high Openness. This is not a full five-domain profile induction.

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
└── LICENSE
```

## Data provenance and access

The underlying personality dialogue source is BIG5-CHAT (Li et al., 2025). The author-maintained copy referenced for this study is `shayanfirouzian/big5`: <https://huggingface.co/datasets/shayanfirouzian/big5>.

The DPO preference source is `ProlificAI/social-reasoning-rlhf`; an author-maintained backup is `shayanfirouzian/SocialReasoning_DPO`:

- <https://huggingface.co/datasets/ProlificAI/social-reasoning-rlhf>
- <https://huggingface.co/datasets/shayanfirouzian/SocialReasoning_DPO>

Third-party datasets and model weights are not redistributed in this repository. Obtain them from their source repositories and comply with their respective licenses and access conditions.
