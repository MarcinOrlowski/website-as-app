![WebApp](docs/logo.png)

# CHANGES

---

* 1.4.0 (2024-11-12)
  * Added screenshot and simplified landing page.
  * Added custom context menu for the embedded browser.
  * Added `Copy URL` item to the context menu.
  * Added `Open URL from Clipboard` item to the context menu.
  * Added option to disable custom WebEngine used by the app (if needed).

* 1.3.1 (2024-10-28)
  * Artificial release to fix isses with PyPy release.

* 1.3.0 (2024-10-28)
  * Enabled clipboard access for the embedded browser (so all the "Copy" buttons now work).
  * If both '--no-tray' and `--minimized` options are given `--minimized` is being ignored.

* 1.2.0 (2024-10-09)
  * Added support for downloading files.
  * Added `--version` switch.

* 1.1.1 (2024-10-06)
  * Fixed setup script missing runtime dependency.

* 1.1.0 (2024-10-06)
  * Now allows only single instance per each profile to be run.
  * Added `--minimized` option to start app minimized.
  * Added `-t` as short form for `--no-tray` switch.

* 1.0.0 (2024-01-28)
  * Initial release.
