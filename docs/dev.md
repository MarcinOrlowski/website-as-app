![WebApp](img/banner.webp)

# Dev corner

[&laquo; Back to main menu](README.md)

1. [Profiles](#profiles)
2. [Building the package](#building-the-package)

---

## Profiles

Each instance can be separated from others by using dedicated "profile". Any
instance using the same profile, will have access to the same shared data like
cookies or app settings.

### Location

If for any reason you would like to reset the profile, you can do it by removing the profile
directory:

Windows

```ascii
%USERPROFILE%\AppData\Local\MarcinOrlowski\WebsiteAsApp\<APP_PROFILE_NAME>\
```

Linux

```ascii
~/.local/share/MarcinOrlowski/WebsiteAsApp/<APP_PROFILE_NAME>/
```

MacOS

```ascii
??? (PLEASE ASSIST)
```

---

## Building the package

Checkout the source code:

```bash
$ cd <DIR>
$ git clone ....
$ cd website-as-app
```

Setup its runtime environment (NOTE: if you are using different shell than `bash` (i.e. `fish`),
please use correct `activate` script from `venv/bin/` directory):

```bash
$ python -m venv venv
$ source venv/bin/activate  # User right one for your shell
```

Install all the dependencies:

```bash
(venv) $ pip install -r requirements-dev.txt
```

Build the package:

```bash
(venv) $ python -m build
```

Install package locally for testing.

We intentionally ignore `install --upgrade` while planting new build, as we need to ensure no
cached bytecode from previous version remains (which could be the case as we do not increment the
version each build).

```bash
(venv) $ pip uninstall --yes dist/website_as_app-1.0.0-py3-none-any.whl
(venv) $ pip install dist/website_as_app-1.0.0-py3-none-any.whl
```

Test the app

```bash
(venv) $ webapp -h
usage: webapp [-h] [--name TITLE] [--icon ICON] [--profile PROFILE] [--zoom ZOOM] url
...
```
