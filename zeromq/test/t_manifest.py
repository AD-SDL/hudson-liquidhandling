import sys

sys.path.append(".")

from manifest import generateFileManifest

text = generateFileManifest(
    "manifest.py", purpose="build_dataframe", manifest_filename="manifest.txt"
)
print(text)
