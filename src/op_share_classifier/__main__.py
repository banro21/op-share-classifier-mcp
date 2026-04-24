import os

import uvicorn

from .server import create_app


def main():
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(create_app(), host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
