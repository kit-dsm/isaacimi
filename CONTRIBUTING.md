# Contributing

Contributions are always appreciated!

## Setup
Install Isaac Sim and Isaac IMI. Ensure that Isaac IMI is installed with additional test dependencies by running the install script with the `--test` flag.
```bash
./scripts/install.sh --test
```

## Development
1. Create a new branch
2. Make your desired changes to Isaac IMI
3. Ensure that your tests (and existing tests) pass
```bash
cd tests/
isaacimi test
```
4. If you made changes to the documentation, serve the docs locally and ensure it looks good at `http://localhost:8000`
```bash
cd docs/
./serve.sh
```

## Pushing
Push your changes to your branch and submit a pull request!