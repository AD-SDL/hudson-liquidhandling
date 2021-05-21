import sys

sys.path.append("../utils")

from manifest import generateFileManifest

text = generateFileManifest(
    sys.argv[1], purpose=sys.argv[2], manifest_filename=sys.argv[3]
)
print(text)
