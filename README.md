# Mouse Gaze

A small Pygame window with a girl whose eyes and head follow the mouse. The pointer is tracked across the whole screen on Windows, including when it is outside the window. Eyes move first; the head follows with a softer spring, so the motion eases instead of snapping.

## Run

```powershell
cd C:\Users\shukl\mouse-gaze
run.bat
```

`run.bat` checks Python, creates `.venv` if needed, installs dependencies, and opens version 2. `run.bat v1` opens the original drawn character instead.

Esc or the window close button quits. The window can be resized; she stays inside it.

The corner readout is the cursor position in screen pixels and the direction from her eyes to the pointer (`toward you` when the cursor is on her face).

## Replace the character

The drawn girl is the default. To use your own art, copy `assets/character.example.json` to `assets/character.json` and add the images it names next to that file.

| Field | Meaning |
| --- | --- |
| `reference_size` | Window size the coordinates below were chosen for. The sprite scales uniformly when the window changes. |
| `anchor` | Eye/face point the gaze direction is measured from, in reference-window pixels. |
| `body`, `body_pos` | Optional body image and its top-left position. |
| `head` | Head image, including the face. Leave the pupils out so they can move. |
| `head_pivot` | Pixel on the head image that stays planted (usually the base of the neck). |
| `head_pos` | Where that pivot sits in the reference window. |
| `eyes` | Pupil centers on the head image, one `[x, y]` pair per eye. |
| `pupil` | Optional pupil image. A dark circle is drawn if this is omitted. |
| `pupil_range` | How far a pupil may travel, in head-image pixels: `[x, y]`. |
| `max_head_degrees` | Subtle head turn at a full look. |
| `head_shift` | Subtle head slide toward the cursor, in reference pixels: `[x, y]`. |

Remove `assets/character.json` to go back to the drawn girl.

To supply a different character in code, implement `mouse_gaze.character.Character` and return it from `create_character` in `mouse_gaze/factory.py`. `GazeMotion` in `mouse_gaze/motion.py` is the shared eye/head spring.

## Deploy

The image runs the window on a virtual display, so a server does not need a monitor. Global mouse tracking stays on Windows; inside Linux the character follows the pointer in its own display.

```powershell
docker build -t mouse-gaze:latest .
docker run --rm -e SDL_VIDEODRIVER=dummy mouse-gaze:latest python scripts/smoke_test.py
docker compose up -d --build
```

Jenkins pipeline job `mouse-gaze` builds that image, runs `scripts/smoke_test.py`, and restarts the container only when the build is started with **DEPLOY** checked. The job definition is `Jenkinsfile`. Register it on http://143.244.128.22:8081/ after this repo is pushed somewhere Jenkins can clone:

```powershell
$env:JENKINS_USER = "your-username"
$env:JENKINS_API_TOKEN = "your-api-token"
.\jenkins\create-pipeline.ps1 -GitUrl "https://example.com/you/mouse-gaze.git" -GitBranch "*/master"
```

Use an API token from Jenkins (**User → Security → Add new token**). The agent that runs the job needs Docker.
