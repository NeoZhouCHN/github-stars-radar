# Release Notes For Maintainers

This document is for project maintainers. It is intentionally separate from the main README so regular users only see installation and usage instructions.

## Windows Packaging

This repository includes a manually triggered GitHub Actions workflow:

```text
.github/workflows/windows-release.yml
```

After updating the project, open **Actions -> Build Windows Package -> Run workflow**, enter a version, and choose whether to publish a GitHub Release.

Use SemVer-style versions:

```text
0.1.1
0.2.0
0.2.0-alpha.1
```

The workflow automatically prefixes release tags with `v`, so version `0.1.1` creates or updates tag/release `v0.1.1`.

The workflow:

1. Runs unit tests, MCP smoke test, and manifest checks.
2. Builds `github-stars-radar.exe` with PyInstaller.
3. Builds `GitHubStarsRadarConfig.exe` for Windows packages.
4. Creates Windows, macOS, and Linux portable packages.
5. Builds `GitHubStarsRadarSetup-<version>.exe` with Inno Setup on Windows.
6. Creates `SHA256SUMS.txt`.
7. Uploads packages, installer, and checksums as workflow artifacts.

## Output Destinations

- By default, outputs are uploaded only to the workflow run's **Artifacts** section.
- If `publish_release` is set to `true`, the workflow creates a GitHub **Release** with automatically generated release notes and uploads packages, installer, and checksums as Release assets.
- If the release tag already exists, the workflow does not rewrite the release notes. It only re-uploads assets with `--clobber`.
- This project does not use GitHub **Packages**. Windows installers, zips, and exes are release downloads, so Releases fit better than Packages.

## Release Notes

GitHub generates release notes when a new release is created. The changelog categories are configured in:

```text
.github/release.yml
```

Release notes are best when changes arrive through pull requests with labels such as:

- `feature`
- `bug`
- `documentation`
- `ci`
- `packaging`
- `release`

Direct pushes still work, but the generated notes may be less detailed than PR-based release notes.

## Recommended Release Flow

1. Finish code and docs changes.
2. Run local verification:

```powershell
py -m unittest discover -s tests -v
py scripts\smoke_mcp.py
py scripts\check_manifests.py
```

3. Push to `main`.
4. Open **Actions -> Build Windows Package -> Run workflow**.
5. For test builds, set `publish_release=false`.
6. For public releases, set `publish_release=true`.
7. After the workflow completes, open **Releases** and confirm the installer, zip, checksums, and generated notes are present.

## Current Package Outputs

The workflow currently produces:

- `GitHubStarsRadar-<version>-windows-x64.zip`
- `GitHubStarsRadarSetup-<version>.exe`
- `GitHubStarsRadar-<version>-macos-x64.tar.gz`
- `GitHubStarsRadar-<version>-linux-x64.tar.gz`
- per-platform SHA256 checksum files

## Future Distribution Work

- Medium effort: add native macOS `.dmg`/`.pkg` and Linux `.deb`/`.rpm`/AppImage packages.
- High effort: add code signing, notarization, auto-update, and package manager publishing such as Homebrew, winget, Scoop, Chocolatey, or apt/yum repositories.

The current workflow provides portable packages for common desktop platforms and a Windows installer. Matching mature projects with fully signed installers across platforms requires additional release infrastructure.
