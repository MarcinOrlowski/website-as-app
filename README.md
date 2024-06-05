![WebApp](docs/logo.png)

# WebApp

Run any website as standalone desktop application

---

Small Python script opening any web page in dedicated window, using embedded QT WebEngine. There are
no visible browser's UI etc., so the that can be useful to turn any website into standalone desktop
application. This is useful if you, as me, would like to have a website run as standalone app,
independently of your main browser which can be beneficial as it gives you separate entry in
window manager or task switcher etc.

> **IMPORTANT:** This tool is **NOT** turning websites into OFFLINE apps! It's about separating
> each of your key websites i.e. from each other, or gazzilions of your browser's tabs. But you
> still MUST be connected to the Internet for the apps (websites) to work as previously.

## Installation

I recommend you use `pipx` to install this tool in isolated environment:

```bash
$ pipx install website-as-app
```

You can also use plain `pip`:

```bash
$ pip install website-as-app
```

But that might be a problem on some distributions no longer allowing such installations, therefore
use of `pipx` is strongly recommended as the all-in-one solution.

Once app is running, please use `--help` to see all available options, as i.e. custom icon,
window title etc.

## Usage

When app is installed system-wide, you can run it from anywhere:

```bash
$ webapp "https://github.com"
```

If you are using virtual environment, there's handy Bash script in [extras/](extras/) directory 
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
--profile PROFILE     Profile name (for cookies isolation etc). Default: "default"
--name NAME, -n NAME  Application name (shown as window title)
--geometry GEOMETRY   Initial window geometry (in format "WIDTHxHEIGHT+X+Y")
--icon ICON, -i ICON  Full path to image file to be used as app icon
--zoom ZOOM, -z ZOOM  Initial WebBrowserView zoom factor. Default: 1.0
--no-tray             Disables system tray support (closing window terminates app)
```

The most important option is `--profile` which allows you to isolate cookies and app settings
per instance. Any instance using the same profile will have access to the same cookies and
settings. This is useful if you want to run multiple instances of the same app, but with
different accounts. By default `default` profile is used and it's recommended to use different
profile per each app instance.

## Current limitations

* Due to security based limitations of embedded `QWebBrowerView` you will not be able
  to save any file to your local storage nor filesystem.
* Website's Javascript code cannot write to system clipboard so you might need to manually
  select given portion of the site and copy using function from context menu as any buttons
  on the page that is using JS to write to the host's clipboard will not currently work.

## License ##

* Written and copyrighted &copy;2023-2024 by Marcin Orlowski <mail (#) marcinorlowski (.) com>
* ResponseBuilder is open-sourced software licensed under
  the [MIT license](http://opensource.org/licenses/MIT)
