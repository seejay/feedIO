"""PyInstaller entry point, deliberately using the same CLI as python -m feedio."""
from feedio.feedIO import main

if __name__ == '__main__':
    raise SystemExit(main())
