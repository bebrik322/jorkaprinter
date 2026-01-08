# JorkaPrinter 🖨️

**JorkaPrinter** is a lightweight, automated maintenance bot for inkjet printers on Linux (CUPS). 

It prevents ink clogging by monitoring printer usage logs. If the printer hasn't been used for a set period (default: 7 days), it automatically prints a minimal CMYK test pattern with the current date.

## Features

*   **Smart Monitoring:** Checks CUPS logs (`/var/log/cups/page_log`) to avoid unnecessary prints if you've used the printer recently.
*   **Eco-Friendly:** 
    *   Prints a small CMYK strip instead of a full page.
    *   **Random Positioning:** Places the test pattern at a random location on the A4 page, allowing you to re-use the same sheet of paper multiple times.
*   **Dynamic Generation:** Generates the test image on-the-fly with a timestamp.
*   **Systemd Integration:** Runs automatically in the background as a user timer.

## Requirements

*   **OS:** Linux
*   **Printing System:** CUPS (`lp` command)
*   **Dependencies:** 
    *   `python3`
    *   `imagemagick` (for `convert`)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/gleckson/jorkaprinter.git
    cd jorkaprinter
    ```

2.  Run the installer:
    ```bash
    ./install.sh
    ```
    *   The installer will detect your default printer and set up a daily systemd timer.

3.  (Optional) Test immediately:
    ```bash
    ~/.local/bin/jorka-maintenance --force
    ```

## Manual Usage / Configuration

The script is installed to `~/.local/bin/jorka-maintenance`.

```bash
usage: jorka-maintenance [-h] [--force] [--printer PRINTER] [--days DAYS]

Printer maintenance script.

options:
  -h, --help         show this help message and exit
  --force            Force print test page ignoring history.
  --printer PRINTER  CUPS Printer Name (Auto-detects default if omitted)
  --days DAYS        Days threshold (Default: 7)
```

## Uninstallation

To remove the service and timer:

```bash
systemctl --user disable --now jorka-maintenance.timer
rm ~/.config/systemd/user/jorka-maintenance.*
rm ~/.local/bin/jorka-maintenance
systemctl --user daemon-reload
```

## License

MIT
