import sys

sys.path.append(".")

from manifest import generateFileManifest

text = generateFileManifest("manifest.py", manifest_filename="manifest.txt")
print(text)
