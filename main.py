"""Run the mouse-gaze character window."""

def main() -> None:
    try:
        import pygame  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "pygame is required. From this folder run: pip install -r requirements.txt"
        ) from exc

    from mouse_gaze.app import run

    run()


if __name__ == "__main__":
    main()
