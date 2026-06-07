import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command):
    subprocess.run(command, cwd=ROOT, check=True)


def clean_path(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def exe_name(name, system):
    return f"{name}.exe" if system == "windows" else name


def build_exe(name, entry, onefile=False):
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        name,
    ]
    command.append("--onefile" if onefile else "--onedir")
    command.append(entry)
    run(command)


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def make_archive(source_dir, artifact, system):
    if system == "windows":
        with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in source_dir.rglob("*"):
                archive.write(path, path.relative_to(source_dir.parent))
    else:
        with tarfile.open(artifact, "w:gz") as archive:
            archive.add(source_dir, arcname=source_dir.name)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--platform", default=platform.system().lower())
    args = parser.parse_args()

    system = args.platform.lower()
    if system.startswith("win"):
        system = "windows"
    elif system.startswith("darwin") or system.startswith("mac"):
        system = "macos"
    elif system.startswith("linux"):
        system = "linux"

    package_name = f"GitHubStarsRadar-{args.version}-{system}-x64"
    dist = ROOT / "dist"
    package_root = dist / "portable" / package_name

    clean_path(ROOT / "build")
    clean_path(dist / "github-stars-radar")
    clean_path(dist / "GitHubStarsRadarConfig")
    clean_path(package_root)
    dist.mkdir(exist_ok=True)

    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    build_exe("github-stars-radar", str(ROOT / "mcp-server" / "server.py"))
    build_exe("GitHubStarsRadarConfig", str(ROOT / "config-helper" / "config.py"), onefile=True)

    package_root.mkdir(parents=True, exist_ok=True)
    copy_tree(dist / "github-stars-radar", package_root)

    helper_binary = dist / exe_name("GitHubStarsRadarConfig", system)
    if helper_binary.exists():
        shutil.copy2(helper_binary, package_root / helper_binary.name)

    for file_name in [".env.example", "LICENSE", "README.md", "README.en.md"]:
        shutil.copy2(ROOT / file_name, package_root / file_name)
    for dir_name in ["prompts", "skills", "adapters"]:
        copy_tree(ROOT / dir_name, package_root / dir_name)
    (package_root / "data").mkdir(exist_ok=True)
    (package_root / "generated").mkdir(exist_ok=True)

    artifact = dist / (f"{package_name}.zip" if system == "windows" else f"{package_name}.tar.gz")
    clean_path(artifact)
    make_archive(package_root, artifact, system)
    print(artifact)

    sums = dist / f"SHA256SUMS-{system}.txt"
    sums.write_text(f"{sha256(artifact)}  {artifact.name}\n", encoding="ascii")
    print(sums)


if __name__ == "__main__":
    main()
