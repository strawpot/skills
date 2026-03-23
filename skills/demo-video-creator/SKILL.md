---
name: demo-video-creator
description: Automate end-to-end demo video creation from a YAML scene script. Produces MP4 videos by orchestrating terminal recordings (VHS), browser recordings (Playwright), title cards (ffmpeg), and final stitching. Use this skill whenever the user wants to create a demo video, product walkthrough, marketing video, release video, changelog video, terminal recording, screencast, or any scripted video that combines terminal, browser, and title-card scenes. Also trigger when the user mentions VHS tape files, automated video production, asks to turn a CLI workflow into a video, or needs a video for a landing page, README, or documentation site.
metadata:
  strawpot:
    tools:
      vhs:
        description: Terminal session recorder (charmbracelet/vhs)
        install:
          macos: brew tap charmbracelet/tap && brew install vhs
          linux: go install github.com/charmbracelet/vhs@latest
      ffmpeg:
        description: Video processing and stitching
        install:
          macos: brew install ffmpeg
          linux: apt install ffmpeg
          windows: winget install Gyan.FFmpeg
      node:
        description: Node.js runtime (for Playwright)
        install:
          macos: brew install node
          linux: apt install nodejs npm
          windows: winget install OpenJS.NodeJS
      playwright:
        description: Browser automation and recording
        install:
          macos: npm install -g playwright && npx playwright install chromium
          linux: npm install -g playwright && npx playwright install --with-deps chromium
    env:
      DEMO_VIDEO_OUTPUT_DIR:
        required: false
        description: Directory for final video output (defaults to ./output)
---

# Demo Video Creator

Create polished demo videos from a declarative YAML scene script. Each scene is recorded independently using the best tool for its type, then all scenes are stitched into a single MP4 with transitions.

## Quick Start

1. Write a scene script in YAML (see format below)
2. Run each scene through its recorder (VHS, Playwright, or ffmpeg)
3. Stitch all scene outputs into one final MP4

## Scene Script Format

The scene script is a YAML file that defines an ordered list of scenes and global output settings.

```yaml
scenes:
  - type: title-card
    text: "StrawPot Demo"
    subtitle: "AI agents that ship code"
    duration: 3s
    background: "#1a1a2e"
    text_color: "#ffffff"
    font_size: 72

  - type: terminal
    commands:
      - "strawpot run 'Build me a landing page'"
    typing_speed: 50ms
    wait_after: 2s
    duration: 8s
    viewport: 1920x1080
    font_size: 22
    theme: Catppuccin Mocha

  - type: browser
    url: "http://localhost:3000"
    actions:
      - click: ".agent-dashboard"
      - wait: ".task-complete"
      - scroll: "bottom"
      - screenshot_pause: 2s
    viewport: 1920x1080
    duration: 10s

  - type: terminal
    commands:
      - "git log --oneline -3"
      - "echo 'Done!'"
    typing_speed: 40ms
    duration: 4s

  - type: title-card
    text: "Try it: strawpot.com"
    duration: 3s

output:
  file: demo.mp4
  resolution: 1920x1080
  fps: 30
  transition: crossfade       # crossfade | cut | fade-black
  transition_duration: 0.5s
  background_music: null       # path to audio file, or null
  music_volume: 0.15           # 0.0-1.0, relative to scene audio
  codec: libx264
  crf: 23                      # quality (lower = better, 18-28 typical)
  pixel_format: yuv420p        # web-compatible
```

### Scene Types

#### `title-card`

Static frame with centered text overlay. Generated purely with ffmpeg — no external recording needed.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | required | Main title text |
| `subtitle` | string | `""` | Smaller text below title |
| `duration` | duration | `3s` | How long the card displays |
| `background` | hex color | `"#1a1a2e"` | Background color |
| `text_color` | hex color | `"#ffffff"` | Text color |
| `font_size` | int | `72` | Title font size in points |
| `subtitle_font_size` | int | `36` | Subtitle font size |

#### `terminal`

Records a terminal session using [VHS](https://github.com/charmbracelet/vhs). Commands are typed and executed in sequence.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `commands` | list[string] | required | Commands to type and execute |
| `typing_speed` | duration | `50ms` | Delay between keystrokes |
| `wait_after` | duration | `1s` | Pause after last command |
| `duration` | duration | auto | Max scene duration (VHS trims) |
| `viewport` | `WxH` | `1920x1080` | Terminal window size |
| `font_size` | int | `22` | Terminal font size |
| `theme` | string | `"Catppuccin Mocha"` | VHS theme name |
| `env` | map | `{}` | Environment variables to set |
| `shell` | string | `"bash"` | Shell to use |
| `cwd` | string | `.` | Working directory |

#### `browser`

Records browser interactions using [Playwright](https://playwright.dev/) video recording.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | required | URL to navigate to |
| `actions` | list | `[]` | Sequence of browser actions |
| `viewport` | `WxH` | `1920x1080` | Browser viewport size |
| `duration` | duration | auto | Max recording duration |
| `wait_for_load` | duration | `2s` | Wait after page load |
| `device` | string | null | Playwright device preset |

**Supported browser actions:**

- `click: "<selector>"` — click an element
- `type: {selector: "<sel>", text: "<text>"}` — type into an input
- `wait: "<selector>"` — wait for element to appear
- `wait_timeout: "<duration>"` — wait a fixed time
- `scroll: "bottom" | "top" | "<selector>"` — scroll to position
- `screenshot_pause: "<duration>"` — hold the current frame
- `hover: "<selector>"` — hover over an element
- `navigate: "<url>"` — go to a different URL

## Orchestration Workflow

Follow these steps in order for each video production run.

### Step 1: Parse and Validate the Script

Read the YAML scene script and validate:
- Every scene has a `type` field with a supported value
- Required fields are present for each scene type
- Duration values parse correctly (e.g., `3s`, `500ms`)
- Resolution is in `WxH` format
- Referenced files (background_music) exist

Report all validation errors before proceeding. Do not partially record.

### Step 2: Create a Working Directory

```bash
mkdir -p .demo-video-work/{scenes,normalized}
```

Each scene gets a numbered output file: `scene-001.mp4`, `scene-002.mp4`, etc. The numbering preserves scene order for stitching.

### Step 3: Record Each Scene

Process scenes sequentially in script order.

#### Title Cards

Generate with ffmpeg drawtext:

```bash
ffmpeg -f lavfi -i color=c=0x1a1a2e:s=1920x1080:d=3 \
  -vf "drawtext=text='StrawPot Demo':fontcolor=white:fontsize=72:\
x=(w-text_w)/2:y=(h-text_h)/2-40,\
drawtext=text='AI agents that ship code':fontcolor=0xcccccc:fontsize=36:\
x=(w-text_w)/2:y=(h-text_h)/2+50" \
  -c:v libx264 -pix_fmt yuv420p \
  .demo-video-work/scenes/scene-001.mp4
```

For custom fonts, add `fontfile=/path/to/font.ttf` to the drawtext filter. Escape special characters in text with backslashes.

#### Terminal Scenes

Generate a `.tape` file from the scene config, then run VHS:

```tape
# Auto-generated .tape file
Set Shell "bash"
Set FontSize 22
Set Width 1920
Set Height 1080
Set Theme "Catppuccin Mocha"
Set TypingSpeed 50ms

Output .demo-video-work/scenes/scene-002.mp4

Type "strawpot run 'Build me a landing page'"
Enter
Sleep 2s
```

**Tape generation rules:**
- `typing_speed` maps to `Set TypingSpeed` (VHS handles per-character delay)
- Each command becomes `Type "<command>"` followed by `Enter`
- `wait_after` becomes a final `Sleep` at the end
- `env` entries become `Set Env "<KEY>" "<VALUE>"`
- `cwd` becomes an initial `cd` command (hidden)

Run VHS:

```bash
vhs .demo-video-work/scene-002.tape
```

If the VHS output is a GIF (some versions default to GIF), convert to MP4:

```bash
ffmpeg -i scene.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" scene.mp4
```

#### Browser Scenes

Write and execute a Playwright script:

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: '.demo-video-work/scenes/',
      size: { width: 1920, height: 1080 }
    }
  });
  const page = await context.newPage();

  await page.goto('http://localhost:3000');
  await page.waitForTimeout(2000); // wait_for_load

  // Actions from script
  await page.click('.agent-dashboard');
  await page.waitForSelector('.task-complete');
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(2000); // screenshot_pause

  await context.close();
  await browser.close();
})();
```

Run it:

```bash
npx playwright install chromium  # first time only
node .demo-video-work/browser-scene-003.js
```

Rename the Playwright output (random UUID filename) to the expected `scene-NNN.mp4`.

### Step 4: Normalize All Scenes

Before stitching, normalize every scene to consistent parameters:

```bash
ffmpeg -i scene-001.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -crf 23 -pix_fmt yuv420p \
  .demo-video-work/normalized/scene-001.mp4
```

This ensures all scenes share the same resolution, frame rate, and pixel format — required for clean concatenation.

### Step 5: Stitch Scenes

#### Simple cut (no transitions)

Create a concat file:

```
file 'normalized/scene-001.mp4'
file 'normalized/scene-002.mp4'
file 'normalized/scene-003.mp4'
```

```bash
ffmpeg -f concat -safe 0 -i concat.txt -c copy .demo-video-work/stitched.mp4
```

#### Crossfade transitions

For crossfade, use the xfade filter between each pair of scenes. With N scenes and transition duration T:

```bash
ffmpeg \
  -i scene-001.mp4 -i scene-002.mp4 -i scene-003.mp4 \
  -filter_complex "\
    [0][1]xfade=transition=fade:duration=0.5:offset=2.5[v01];\
    [v01][2]xfade=transition=fade:duration=0.5:offset=10.0[vout]" \
  -map "[vout]" -c:v libx264 -crf 23 -pix_fmt yuv420p \
  .demo-video-work/stitched.mp4
```

The `offset` for each xfade = cumulative duration of previous scenes minus cumulative transition overlaps. Calculate offsets programmatically:

```
offset[0] = duration[0] - transition_duration
offset[i] = offset[i-1] + duration[i] - transition_duration
```

#### Fade-black transitions

Apply fade-out to the end of each scene and fade-in to the start of the next, with a black gap between them:

```bash
# For each scene, add fade-out at the end and fade-in at the start
ffmpeg -i scene-001.mp4 \
  -vf "fade=t=out:st=2.5:d=0.5" \
  -c:v libx264 -crf 23 -pix_fmt yuv420p \
  .demo-video-work/faded/scene-001.mp4

ffmpeg -i scene-002.mp4 \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=9.5:d=0.5" \
  -c:v libx264 -crf 23 -pix_fmt yuv420p \
  .demo-video-work/faded/scene-002.mp4
```

Then concatenate the faded scenes with simple cut (the fades create the visual transition).

### Step 6: Add Background Music (Optional)

If `background_music` is specified:

```bash
ffmpeg -i .demo-video-work/stitched.mp4 -i background.mp3 \
  -filter_complex "[1:a]volume=0.15[bg];[bg]apad[bgpad]" \
  -map 0:v -map "[bgpad]" \
  -shortest -c:v copy -c:a aac \
  .demo-video-work/final.mp4
```

If no music, copy stitched.mp4 as final.mp4.

### Step 7: Output

Move the final video to the output path:

```bash
mv .demo-video-work/final.mp4 demo.mp4
```

Report:
- Total duration
- File size
- Number of scenes recorded
- Any warnings (e.g., scene ran shorter than specified duration)

Clean up the working directory if the user confirms, or leave it for debugging:

```bash
rm -rf .demo-video-work  # only after user confirms
```

## Troubleshooting

**VHS not found**: Install via `brew tap charmbracelet/tap && brew install vhs` (macOS) or `go install github.com/charmbracelet/vhs@latest` (Linux). Requires `ttyd` and `ffmpeg` as VHS dependencies.

**Playwright browser not installed**: Run `npx playwright install chromium` to download the browser binary. For CI environments, use `npx playwright install --with-deps chromium`.

**ffmpeg xfade not working**: The xfade filter requires ffmpeg 4.3+. Check with `ffmpeg -version`. On older systems, fall back to simple cut transitions.

**Browser scene shows blank page**: Ensure the target URL is running and accessible. Add `wait_for_load` to give the page time to render. For SPAs, use `wait: "<selector>"` to wait for content.

**Terminal scene too fast/slow**: Adjust `typing_speed` (per-keystroke delay) and `wait_after` (post-command pause). For commands with long output, increase `duration` to capture all output.

**Resolution mismatch artifacts**: The normalization step (Step 4) handles this. If you still see black bars or stretching, check that the source viewport matches the output resolution.

## Example: Full StrawPot Demo Script

```yaml
scenes:
  - type: title-card
    text: "StrawPot"
    subtitle: "AI agents that ship code"
    duration: 3s
    background: "#0f0f23"

  - type: terminal
    commands:
      - "strawpot run 'Build me a landing page with a hero section and pricing table'"
    typing_speed: 40ms
    wait_after: 5s
    duration: 12s
    theme: "Catppuccin Mocha"

  - type: browser
    url: "http://localhost:3000"
    actions:
      - wait: ".hero-section"
      - screenshot_pause: 3s
      - scroll: ".pricing-table"
      - screenshot_pause: 3s
    viewport: 1920x1080
    duration: 10s

  - type: terminal
    commands:
      - "git log --oneline -5"
      - "wc -l src/**/*.tsx"
    typing_speed: 40ms
    duration: 6s

  - type: title-card
    text: "Ship faster with AI agents"
    subtitle: "strawpot.com"
    duration: 3s
    background: "#0f0f23"

output:
  file: strawpot-demo.mp4
  resolution: 1920x1080
  fps: 30
  transition: crossfade
  transition_duration: 0.5s
  codec: libx264
  crf: 23
  pixel_format: yuv420p
```
