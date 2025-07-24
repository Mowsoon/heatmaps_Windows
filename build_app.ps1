# build_app.ps1
# Compile l'application FastAPI en exécutable standalone avec Nuitka

# Nom du fichier principal Python
$mainScript = "main.py"

# Dossier de sortie
$outputDir = "build"

# Compilation avec Nuitka
nuitka `
  --standalone `
  --include-module=main `
  --include-package=cv2 `
  --include-package=numpy `
  --include-package=pdf2image `
  --include-package=uvicorn `
  --include-package=pywifi `
  --include-data-dir=templates=templates `
  --include-data-dir=static=static `
  --include-data-dir=languages=languages `
  --output-dir=$outputDir `
  $mainScript
