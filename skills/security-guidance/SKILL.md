---
name: security-guidance
description: "Security guidance for common vulnerability patterns — command injection, XSS, unsafe code execution, and insecure deserialization. Use this skill when writing or reviewing code that involves shell commands, user input handling, HTML rendering, serialization, or GitHub Actions workflows. Triggers include: editing workflow files, using exec/eval/innerHTML, handling untrusted input, or any request to check code for security issues."
---

# Security Guidance

When writing or editing code, watch for these common security vulnerability patterns and follow the safe alternatives.

## Command Injection

### Shell execution (Node.js)

`child_process.exec()` passes input through a shell, enabling injection.

```javascript
// UNSAFE — shell injection via user input
exec(`command ${userInput}`)

// SAFE — use execFile which does not invoke a shell
execFile('command', [userInput])
```

Only use `exec()` if you absolutely need shell features and the input is guaranteed to be safe.

### Shell execution (Python)

`os.system()` passes arguments through a shell.

```python
# UNSAFE — shell injection
os.system(f"command {user_input}")

# SAFE — use subprocess with list arguments
subprocess.run(["command", user_input])
```

Only use `os.system()` with static arguments, never with user-controlled input.

## Code Injection

### eval()

`eval()` executes arbitrary code and is a major security risk.

```javascript
// UNSAFE
eval(userInput)

// SAFE — use JSON.parse() for data parsing
JSON.parse(userInput)
```

Only use `eval()` if you truly need to evaluate arbitrary dynamic code.

### new Function()

`new Function()` with dynamic strings can lead to code injection.

```javascript
// UNSAFE
new Function(userInput)()
```

Consider alternative approaches that don't evaluate arbitrary code.

## Cross-Site Scripting (XSS)

### dangerouslySetInnerHTML (React)

Can lead to XSS if used with untrusted content. Ensure all content is properly sanitized using a library like DOMPurify, or use safe alternatives.

### innerHTML

```javascript
// UNSAFE — XSS via untrusted content
element.innerHTML = userInput

// SAFE — use textContent for plain text
element.textContent = userInput
```

If you need HTML, use a sanitizer library like DOMPurify.

### document.write()

Can be exploited for XSS attacks. Use DOM manipulation methods like `createElement()` and `appendChild()` instead.

## Insecure Deserialization

### pickle (Python)

Using `pickle` with untrusted content can lead to arbitrary code execution.

```python
# UNSAFE — arbitrary code execution
pickle.loads(untrusted_data)

# SAFE — use JSON for untrusted data
json.loads(untrusted_data)
```

Only use `pickle` if it is explicitly needed and the data source is trusted.

## GitHub Actions Workflows

When editing `.github/workflows/*.yml` files, never use untrusted input directly in `run:` commands.

```yaml
# UNSAFE — command injection via issue title
run: echo "${{ github.event.issue.title }}"

# SAFE — use environment variables
env:
  TITLE: ${{ github.event.issue.title }}
run: echo "$TITLE"
```

Risky inputs that must be handled via environment variables:

- `github.event.issue.title` / `.body`
- `github.event.pull_request.title` / `.body` / `.head.ref` / `.head.label`
- `github.event.comment.body`
- `github.event.review.body` / `review_comment.body`
- `github.event.commits.*.message` / `.author.email` / `.author.name`
- `github.event.head_commit.message` / `.author.email` / `.author.name`
- `github.event.pages.*.page_name`
- `github.head_ref`

Reference: https://github.blog/security/vulnerability-research/how-to-catch-github-actions-workflow-injections-before-attackers-do/
