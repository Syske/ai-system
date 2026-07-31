# AI System — Migration Package

## What's Here

ai-system/ — the full AI Runtime Engine (workflows, skills, governance, CLI)

## Post-Migration Steps

1. Edit ai-system/config/environments/local.yaml.template:
   - workspace.root — absolute path to the new workspace root
   - workspace.repository_root — path to cloned code repositories (can be a junction)
   - build.java_home / build.maven_home / build.maven_settings — local tool paths
   - Rename to local.yaml

2. Create or rebuild the projects/ junction:
     mklink /J projects D:\path\to\code-repositories

3. Run python ai-system/tools/path-audit.py to verify all paths resolve

4. Install Python dependencies and register the CLI:
     cd ai-system
     pip install -e .    # editable install; `aic` command available after

5. Verify:
     aic --help          # positional: aic <workflow>
     aic                 # interactive wizard (no arguments)
     python tools/path-audit.py

## Packed On

2026-07-31

## Included Directories

  aic.egg-info/
  archived/
  cli/
  config/
  frameworks/
  governance/
  loaders/
  logs/
  maintainers/
  metrics/
  reports/
  rfc/
  routing/
  skills/
  templates/
  tools/
  workflows/

## Excluded

- logs/, metrics/, .egg-info, __pycache__, *.pyc
- node_modules/, package*.json, link.txt
- archived/ai-runtime/opencode/node_modules/
- local.yaml (saved as .template — contains absolute paths)

Run tools/pack.py on the new machine after the first migration to create
subsequent migration packages.