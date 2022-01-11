# Development

!!! TODO

    Add content

## UI
This project uses [Qt 6](https://www.qt.io) for its UI components.

`Qt Designer` is used to create the UI, which outputs a `.ui` file (XML content that describes the UI). This file is
then transformed into a `.py` file.

All the required tools are available by installing `pyside6`:

* `Qt Designer`: `pyside6-designer`
* `.ui > .py` Converter: `pyside6-uic`
  At the project root:
  ```
  pyside6-uic assets/ui/settings.ui > hd_active/ui/settings_ui.py
  ```

!!! Note

    Qt is not necessarily required, something like Tkinter could have been used (more open and included in Python), and
    the latest version of Qt (6) isn't necessary, something more established like Qt 5 could have been used, but I
    wanted to dip my toes into the Qt world and figured using the latest version would give me more lasting knowledge.

## Documentation
Install documentation requirements with:
```
pip install -r docs-requirements.txt
```

You can then edit the `.md` files under the `docs` directory and, if more need to be added, update `mkdocs.yml`.

### View locally

* Web server (recommended)
  ```
  mkdocs serve
  ```
* Static files
  ```
  mkdocs build
  ```
  This generates a static web site under `/site`, which is in `.gitignore`.

### Update in GitHub

Simply run the command below to push the documentation to GitHub pages.

```
mkdocs gh-deploy
```

More instructions [here](https://www.mkdocs.org/user-guide/deploying-your-docs/#github-pages).

The first time `gh-deploy` is used, authorization needs to be granted to publish to GitHub Pages. A _GitHubCredentials_
widget appears and follow the prompts.

Documentation available here: [https://joaonc.github.io/hd_active](https://joaonc.github.io/hd_active)

When running this command, it's this website that needs to be updated (unless working in a forked project). Until a
process is established for other people to update this GitHub Page location, please contact me and I'll push the
documentation changes as needed.
