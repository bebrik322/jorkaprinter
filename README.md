# JorkaPrinter

**JorkaPrinter** is a maintenance bot for inkjet printers on Linux (CUPS). 

Inkjet printers have a fatal flaw: if left idle for too long, the print heads dry out and clog, leading to streaky prints and expensive cartridge replacements. Script solves this by automating a minimal maintenance cycle. It monitors your printing habits and only activates when necessary. The maintenance print consists of four small blocks (Cyan, Magenta, Yellow, Black) and a timestamp, consuming approximately 0.46% of an A4 page. This ensures all nozzles remain clear and functional with negligible ink cost. Random positioning allows you to reuse the same sheet of paper for months.

If the printer hasn't been used for a set period (default: 7 days), it automatically prints this minimal CMYK test pattern. The script checks CUPS logs (`/var/log/cups/page_log`) to avoid unnecessary prints if you've already used the printer recently.

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
