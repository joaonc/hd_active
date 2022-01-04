# Development

!!! TODO

    Add content

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
