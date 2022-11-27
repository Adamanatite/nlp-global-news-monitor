# From https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from elasticsearch_database import GetActiveSources, EnableSource

disabled_sources = GetActiveSources(False)
if not disabled_sources:
    print("No disabled sources")
    exit(0)
for source in disabled_sources:
    EnableSource(source["_id"])

print("Enabled all disabled sources.")