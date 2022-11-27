from elasticsearch_database import GetActiveSources, EnableSource

disabled_sources = GetActiveSources(False)
for source in disabled_sources:
    EnableSource(source["_id"])