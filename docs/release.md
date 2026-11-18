# Release process
Using `invoke` tasks to help with the build/release workflow:

For a list of tasks:
```
inv --list build
```

## Manually / Locally
The individual steps are described here in case something needs to be done with adjustments in the
steps.

### Build
1. Bump version
   ```
   inv build.version
   ```
   Then select which portion to bump (major, minor or patch).
2. Create / merge a PR

### Publish / Release
#### GitHub
##### Package
1. Publish package to Pypi.
   ```
   inv build.publish
   ```
   Gets published to [https://pypi.org/project/hd_active/](https://pypi.org/project/hd_active/)

#### Pypi
**TODO: Finish**

## GitHub Actions
The GitHub action [Release](https://github.com/joaonc/hd_active/actions/workflows/release.yml)
follows the same steps described above, but in an automatic way, making it easier and with less
room for error.

**TODO: Finish**
