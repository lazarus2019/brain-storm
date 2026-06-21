## What is `git bisect`?

- Use binary search to find the commit that introduced a bug

> Docs: https://git-scm.com/docs/git-bisect

## Why `git bisect` exists? Dev pains before `git bisect`

```markdown
Commit 1 : Works
Commit 2 : Works
...
Commit 100 : Works
Commit 101 : Bug introduced
Commit 102 : Bug exists [today]
```

- Today you recognize the bug at commit 102, then asking:
  - Which first commit started the bug?
  - Was it commit 100?
  - Could it come from commit 90?
  - Commit 67?

- Without `git bisect`:

```bash
git checkout commit-67
# test

git checkout commit-90
# test

git checkout commit-99
# test
```

- Do it over and over again can take hours!!!

- Then `git bisect` come to safe the dev life

### How `git bisect` solve the problem

The binary search mechanics give git bisect mathematical efficiency:

| Number of Commits to Search | Maximum Steps Required to Find the Bug |
| --------------------------- | -------------------------------------- |
| 100 commits                 | ~7 steps                               |
| 1.000 commits               | ~10 steps                              |
| 10.000 commits              | ~14 steps                              |

- Think about real life situations:
  - Huge Commit Histories: When a codebase has thousands of commits, scrolling through logs to guess where a bug started is nearly impossible.
  - Hidden Regressions: Sometimes a feature breaks quietly, and nobody notices for weeks. git bisect bridges the gap between when the code last worked and when it broke.
  - Vague Bug Symptoms: When a stack trace doesn't explicitly reveal the root cause, finding the exact code change (the "diff") provides instant context on why the failure is happening.

## When to use `git bisect`?

- Use it whenever you have to find the first commit that broke the production in many commits already committed.
- A bug appeared recently (known which commit is bad and which commit is good)
- Performance regression (slowdown)
- Build suddenly fails
- Test started failing

## When NOT to use `git bisect`?

- Bug is not reproducible (bugs happen sometimes)
- Don't know which commit is good (can not start bisect)

## How to use `git bisect`?

### Step 1: Start bisect

```bash
git bisect start
```

Know where is the good commit

```bash
git bisect start HEAD commit_hash
```

Don't know which commit is bad

```bash
git bisect start
git bisect bad # same as git bisect bad HEAD
```

### Step 2: Mark good, bad commit

Test the version of current commit then tell `git bisect` is that bad/good commit

```bash
# bad commit
git bisect bad

# good commit
git bisect good
```

### Step 3: Find the first bad commit & exit bisect

Marking good/bad commit until git response message like

```plaintext
XXXXXX is the first bad commit
```

Then exit the bisect mode

```bash
git bisect reset
```

### Main commands in `git bisect`

- `git bisect start`: Enter the mode `git bisect`
- `git bisect good`: Mark the commit not have bugs
- `git bisect bad`: Mark the commit have bugs
- `git bisect reset`: Get out of mode `git bisect`

### Extend commands in `git bisect`

- `git bisect next`: Move to next commit (git automated this action)
- `git bisect skip`: Skip commit cannot test, force git choose another commit
- `git bisect visualize/view`: Show candidate commits (equal to `git log`)
- `git bisect log`: Show bisect history

## Best practice with `git bisect`?

### Use automated tests

Best scenario:

```bash
git bisect run npm test
```

No manual testing required, auto checkout to the next commit.

### Keep commit small changes

Good:

```plaintext
feat: implement authenticate
fix: validate auth payload
refactor: extract hook
```

Bad:

```plaintext
Update
Update everything
```

### Always reset after finished

Don't forget to run `git bisect reset` after finished

### Use tags/release as known good points

Must easier than finding hashes

```bash
git bisect good v1.2.0
```

## FAQ with `git bisect`

### Is `git bisect` changing my code?

No, only checkout difference commits, only change from HEAD to detached HEAD util run `git bisect reset`

### What if a commit cannot be tested?

Use `git bisect skip`

### Can I stop anytime?

Yes, use `git bisect reset`, this will move HEAD to the previous state

### Why there is `detached HEAD` during bisect?

Git just temporarily checkout into commit hash, don't panic.

```plaintext
HEAD detached at XXXXXX
```

### Can I use tags instead of commit hashes?

Yes, `git bisect good v1.0.0` `git bisect bad v2.0.0`

### Can `git bisect` find the commit that fixed the bugs?

Absolutely, reverse the logic.

```bash
git bisect start
git bisect new HEAD   # this state the fix exist
git bisect old XXXXXX # this state the bug exist
```

Mark `git bisect new` if commit state the fix exist
Mark `git bisect old` if commit state the bug exist

Util git response the first commit bug exist

## Conclusion

Mental model `git bisect` ~ `git log` + `binary search` + `testing`
Marking GOOD/BAD commit until got response `This is the first bad commit`
Fastest way to looking for the commit that introduced the bugs.
