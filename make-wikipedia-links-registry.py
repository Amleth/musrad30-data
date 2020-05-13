import json
import pandas

registry = {}

for id, row in pandas.read_excel("2020-04-18 musiciens_séparés virgules et complétés wiki par cb.xlsx", sheet_name="musiciens_complété par cb", encoding='utf-8').iterrows():
    if not pandas.isna(row['URL page wikipedia']):
        registry[row['IDmusiciens']] = row['URL page wikipedia']

with open('wikipedia-links-registry.json', 'w') as outfile:
    json.dump(registry, outfile)
