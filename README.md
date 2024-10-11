![WebApp](docs/logo.png)

# WebApp

Run any website as standalone desktop application

---

This Python script offers a unique approach to web browsing by opening any webpage in a dedicated
window using the embedded QT WebEngine. By removing the typical browser UI elements, it effectively
turns websites into standalone desktop applications. This can be particularly useful if you've ever
wished to run a frequently used website as a separate app, independent from your main browser.

The tool provides a practical solution for those who find themselves juggling numerous browser tabs
or wanting a clearer separation between work and personal web applications. With each website
running as its own "app", you gain the benefit of individual entries in your window manager or task
switcher, potentially improving your workflow organization and efficiency.

Whether you're looking to streamline your digital workspace or simply curious about alternative
ways to interact with web content, this script presents an interesting concept that might just
solve a problem you didn't know you had.

**IMPORTANT:** It's worth pointing out however, that this tool doesn't transform websites into
offline applications. Rather, it focuses on separating your key websites from each other and from
the multitude of browser tabs you might typically have open. While this approach offers improved
organization and workflow, it's crucial to understand that an internet connection is still required
for these "apps" (websites) to function as they normally would in a traditional browser environment.

## Installation

I recommend you use [pipx](https://pipx.pypa.io/) to install this tool in isolated environment:

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

## Current limitations

* Website's Javascript code cannot write to system clipboard so you might need to manually
  select given portion of the site and copy using function from context menu as any buttons
  on the page that is using JS to write to the host's clipboard will not currently work.

## License

* Written and copyrighted &copy;2023-2024 by Marcin Orlowski <mail (#) marcinorlowski (.) com>
* ResponseBuilder is open-sourced software licensed under
  the [MIT license](http://opensource.org/licenses/MIT)
