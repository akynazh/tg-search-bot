import re

msg = 'ipx--369 ipx123 sfe_213 213-21313 _fdsag-123_ _dfaf_ad n1235 npx1231'

# ids = re.compile(r'[A-Za-z0-9]+[-_][A-Za-z0-9]+').findall(msg)
ids = re.compile(r'n\d+').findall(msg)
ids = set(ids)
for id in ids:
    print(id)