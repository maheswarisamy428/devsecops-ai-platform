# AI Usage Disclosure

This repository was prepared with AI assistance for boilerplate generation, documentation structure, policy examples and review of the challenge requirements.

## Areas where AI assistance was used

- Drafting and improving README, architecture, decisions and evaluation documentation.
- Suggesting GitHub Actions workflow structure and stage ordering.
- Suggesting Terraform/Checkov/Kyverno evaluation fixtures.
- Reviewing the repository for missing challenge deliverables and inconsistent paths.
- Improving wording for security rationale and simulated evaluation scenarios.

## Human responsibility

The candidate is responsible for reviewing, understanding and being able to explain every artifact. In particular, the candidate should be prepared to explain:

- why each CI stage runs where it does;
- why a given Checkov rule/policy is relevant;
- what each Kubernetes policy blocks;
- how the SRE agent avoids unsupported conclusions;
- why each monitoring threshold is only a starting point;
- which evidence is simulated and which was actually executed.

## No claim of autonomous production implementation

AI assistance was not used as evidence that the system is production-ready. The repository intentionally labels live-infrastructure assumptions and simulated behavior separately.

## Final submission note

Before submitting, update this file with any additional AI tools actually used after this document was generated, including the tool name and the type of assistance received. Do not claim that a tool was used if it was not.
