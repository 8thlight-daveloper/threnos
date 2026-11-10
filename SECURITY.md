# Security policy

## Report a problem privately

Do not open a public issue for a security problem. Use the **Report a vulnerability** button on this repository's
Security tab, or [open a private report](https://github.com/8thlight-daveloper/threnos/security/advisories/new)
directly. Only the maintainers can read it. Include what you found, the steps to reproduce it, and the version or commit
you tested.

We reply in the report, so you do not need to share an email address. We will confirm that we received it and keep you
informed as we look into it.

## Supported versions

Threnos has no tagged release yet. We fix problems on `main`. Once releases exist, this section will name the supported
ones.

## What counts as a security problem

Threnos is mostly documents, but three parts act on a project's files or tell an agent to act:

- `nix run .#sync` writes the shared rules and skills into a project, removes skills the project turned off, and seeds
  starting files such as CI workflows where the project has nothing at that path. It never overwrites an existing seed,
  and records each seeded path in `.threnos/seeded`.
- The shared rules and the skills are instructions that agents follow with the permissions the project gave them.
- `gomurun` and the mutation scripts run a project's tests and write a cache and reports under that project.

These are in scope:

- Sync writing, replacing, or deleting a file outside `.agents/` and `.claude/skills/`, or one the project did not
  install through sync.
- A rule or skill that tells an agent to read a secret, send data off the machine, or run a command from untrusted
  content.
- The mutation tools running a command or reading a path the project did not name.
- Credentials, personal data, or client details committed to this repository.

These are out of scope:

- A local user who can already write to the project's directory.
- A hostile process running as the same user.
- Weaknesses in Nix, Go, gomu, or another tool Threnos calls. Report those to the tool's maintainers.
