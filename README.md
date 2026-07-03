# Claw

Personal Codex skills, automations, and intelligence workflows.

## Skills

- [DCID - Daily CNBC Intelligence Digest](skills/dcid/README.md): Fetches CNBC-first financial news, classifies and ranks articles, and generates a Chinese-friendly market intelligence digest.

## Codex Invocation

This repo includes a Codex skill wrapper at `.agents/skills/dcid/SKILL.md`.
From a Codex session launched inside this repo, invoke it with `/skills` and pick `dcid`, or mention:

```text
$dcid generate today's CNBC intelligence digest
```

## Layout

```text
.agents/
  skills/
    dcid/
skills/
  dcid/
    src/
    tests/
    README.md
```

Each skill should be self-contained, with its own README, tests, and runtime configuration.
