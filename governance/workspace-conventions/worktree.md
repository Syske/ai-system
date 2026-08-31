# Worktree Convention

## Location

| Scenario | Path |
|---|---|
| Project dev branch | `workspaces/<project-id>/worktrees/{service}-{branch}` |
| Non-project (code review / exploration) | `worktrees/{service}-{branch}` |

## Naming

Template: `{service}-{branch}`

- service = service name (matches `projects/` directory name)
- branch = branch name (main chain: P26 template `cc{date}_ipd_{desc}_{service}`; bugfix: `cc{date}_{type}{desc}_{service}`)

## Lifecycle

| Phase | Condition | Owner |
|---|---|---|
| Create | dev-setup stage, user decides to use worktree | AI provides steps, ops executes |
| Maintain | during development | ops/developer |
| Cleanup | branch merged or abandon | ops runs `git worktree remove` |
| GC | `git worktree prune` (periodic) | ops |

## Relationship with projects/

- `projects/{service}` always stays on master (authoritative source, clean)
- Dev branches exist only in worktree, never switch branches in `projects/`
- Same branch cannot be checked out in two worktrees simultaneously
