![WebApp](docs/logo.png)

# WebApp

Run any website as standalone desktop application

---

## Installation

This is regular Python package and is also hosted
on [PyPi](https://pypi.org/project/website-as-app/) so
you can install it as usual. But because this one is supposed to rather act as the application, I
strongly recommend to use [pipx](https://pipx.pypa.io/) to install this tool in isolated
environment:

```bash
$ pipx install website-as-app
```

You can also use plain `pip`:

```bash
$ pip install website-as-app
```

But that might be a problem on some distributions no longer allowing such installations, therefore
use of `pipx` is strongly recommended as the all-in-one solution.

Once installed `webapp` executable (and its alias `runasapp`) should be available in your system.
Please use `--help` to see all available options, as i.e. custom icons, window title etc.

## Usage

When app is installed system-wide, you can run it from anywhere:

```bash
$ webapp "https://github.com"
```

If you are using virtual environment, there's handy Bash script in `extras/` directory
which takes care of initializing virtual environment and running the app using that environment.
You simply use `extras/webapp.sh` script instead of `webapp` directly:

```bash
$ extras/webapp.sh "https://github.com"
```

### Configuration

Available options:

```bash
webapp -h
usage: webapp [--profile PROFILE] [--name NAME] [--icon ICON] [--zoom ZOOM] [--no-tray] url

usage: webapp [--profile PROFILE] [--name NAME] [--icon ICON] [--geometry GEOMETRY]
              [--zoom ZOOM] [--no-tray] [--minimized] [--allow-multiple]
              [--no-custom-webengine] [--search-top] [--version] [--debug] url

Open any website in standalone window (like it's an app)

positional arguments:
url                   The URL to open

options:
--profile PROFILE, -p PROFILE     Profile name (for cookies isolation etc). Default: "default"
--name NAME, -n NAME              Application name (shown as window title)
--icon ICON, -i ICON              Full path to PNG image file to be used as app icon
--geometry GEOMETRY, -g GEOMETRY  Initial window ("WIDTHxHEIGHT+X+Y"). Default: "450x600+0+0"
--zoom ZOOM, -z ZOOM              WebView scale. Default: 1.0 (no scale change).
--no-tray, -t                     Disables docking app in system tray (closing window quits app)
--minimized, -m                   Starts app minimized to system tray.
--allow-multiple, -a              Allows multiple instances of the app to run on the same profile
--no-custom-webengine             Uses built-in QWebEngineView instead of the custom one we use.
--search-top                      Puts search bar on top of window when activated
--debug, -d                       Makes app print more debug messages during execution
```

The most important option is `--profile` which allows you to isolate cookies and app settings
per instance. Any instance using the same profile will have access to the same cookies and
settings. This is useful if you want to run multiple instances of the same app, but with
different accounts. By default `default` profile is used and it's recommended to use different
profile per each app instance.

By default only one instance per profile is allowed to run (attempt to run second instance
will bring the first one to the front). If you want to allow multiple instances of the app
to run on the same profile, use `--allow-multiple` switch.

NOTE: `--zoom` accepts fractional values, so you can use i.e. `--zoom 1.25` to scale content up by
25% or `--zoom 0.75` to scale down to 75% of the original size.

## Keyboard shortcuts

* `CTRL` + `F` - opens search bar (close with `ESC` or toolbar's button).

## Notes

This tool doesn't really transforms websites into offline applications. Rather, it focuses
on separating your key websites from each other and from the multitude of browser tabs you might
typically have open. While this approach offers improved organization and workflow, it's crucial
to understand that an internet connection is still required for these "apps" (websites) to function
as they normally would in a traditional browser environment.

## License

* Written and copyrighted &copy;2023-2025 by Marcin Orlowski <mail (#) marcinorlowski (.) com>
* ResponseBuilder is open-sourced software licensed under
  the [MIT license](http://opensource.org/licenses/MIT)
