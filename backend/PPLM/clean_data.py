# -*- coding: utf-8 -*-
import csv
import tqdm
from collections import defaultdict

c2c = {'Grampa Simpson': 'abraham_grampa_simpson',
 'Manjula Nahasapeemapetilon': 'apu_nahasapeemapetilon',
 'Bart Simpson':'bart_simpson',
 'C. Montgomery Burns': 'charles_montgomery_burns',
 'Chief Wiggum': 'chief_wiggum',
 'Comic Book Guy': 'comic_book_guy',
 'Edna Krabappel-Flanders': 'edna_krabappel',
 'Homer Simpson': 'homer_simpson',
 'Kent Brockman': 'kent_brockman',
 'Krusty the Clown': 'krusty_the_clown',
 'Lisa Simpson': 'lisa_simpson',
 'Marge Simpson': 'marge_simpson',
 'Milhouse Van Houten': 'milhouse_van_houten',
 'Moe Szyslak': 'moe_szyslak',
 'Ned Flanders': 'ned_flanders',
 'Nelson Muntz': 'nelson_muntz',
 'Seymour Skinner': 'principal_skinner',
 'Sideshow Bob': 'sideshow_bob'}

dataset_fp = 'simpsons_dataset.csv'
c2s = defaultdict(list)

with open(dataset_fp) as f:
    csv_reader = csv.DictReader(f)
    for i, row in enumerate(tqdm.tqdm(csv_reader, ascii=True)):
        if row:
            label = row['raw_character_text']
            text = row['spoken_words']
            c2s[label].append(text)

print(max([len(x) for _, x in c2s.items()]))
print(min([len(x) for _, x in c2s.items()]))

clean_c2s = dict()
for k, v in c2s.items():
    if k not in c2c:
        continue
    clean_c2s[c2c[k]] = v
    assert len(v) > 100

print(len(clean_c2s.keys()))
print(clean_c2s.keys())

# dr.fieldnames contains values from first row of `f`.
with open('new' + dataset_fp,'w') as fou:
    dw = csv.DictWriter(fou, delimiter='\t', fieldnames=csv_reader.fieldnames)
    headers = dict()
    for n in dw.fieldnames:
        headers[n] = n
    dw.writerow(headers)
    for k,v in clean_c2s.items():
        for samples in v:
            row = {'raw_character_text': k, 'spoken_words': samples}
        dw.writerow(row)
