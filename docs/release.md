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

##### Binary
1. Build app
   ```
   inv build.app
   ```
   Check that the executable looks good after building (run tests).
2. Upload to 

#### Pypi
**TODO: Finish**

## GitHub Actions
The GitHub actions [Release](https://github.com/joaonc/hd_active/actions/workflows/release.yml) and
[Build app](https://github.com/joaonc/hd_active/actions/workflows/build-app.yml) follow the same
steps described above, but in an automatic way, making it easier and with less room for error.

**TODO: Finish**
