"""python -m app from the backend directory."""

from .main import app
import uvicorn


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
