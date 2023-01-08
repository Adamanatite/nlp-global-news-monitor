from elasticsearch_database import GetActiveSources, EnableSource

disabled_sources = GetActiveSources(False)
if not disabled_sources:
    print("No disabled sources")
    exit(0)
for source in disabled_sources:
    EnableSource(source["_id"])

print("Enabled all disabled sources.")