import nltk
import csv
import os
import json

affixes = ['ity', 'ness']
years = list(range(1975, 2006))
year_to_wc = {}

# filter_command
# grep -aE 'ity\>' *_1980_*.txt > ity_1980w.txt

# wc_command
# grep -ae '[a-z]' *_1989_*.txt | wc -l
# TODO check -e vs -E meaning ? doesn't seem to affect wc_command but could affect filter_command

# deprecated, because we don't actually need to move all of these files around
# def compile_coha():
#     '''Process the COHA data for convenience. Assumes all unzipped COHA folders are in data/COHA_zips'''
#     os.system('mkdir data/COHA_collated')
#     # collate the word-lemma-pair (wlp) files from all 3 decades. Can't just use mv alone because the output is too large.
#     os.system('for f in data/COHA_zips/*/*; do mv \"$f\" data/COHA_collated; done')
#     os.system('mkdir data/compiled_wlp')
# compile_coha()

def calculate_wc():
    '''Populates year_to_wc with the word count for each year'''
    # grep all the relevant words to put them into single files per affix; calculate the word counts for each year
    for affix in affixes:
        for year in years:
            # not using word boundary like \b or \> since that can pick up hyphenated words (security-minded) and trailing periods, among others. The columns are tab-separated so \t works well to detect actual end-of-word.
            # the double alphabetical character is to filter out four letter words like 'city' and 'pity', because apparently each letter of the alphabet is in the nltk vocabulary. I think it's fine to assume the smallest affixable word is two letters (could probably even go higher honestly)
            regex = '[a-zA-Z][a-z]' + affix + '\\t'
            search_file = 'data/COHA_zips/*/*_' + str(year) + '_*.txt'
            output_file = 'data/compiled_wlp/' + affix + '_' + str(year) + '.txt'
            filter_command = f'grep -aE \'{regex}\' {search_file} > {output_file}'
            wc_command = f'grep -ae \'[a-z]\' {search_file} | wc -l'
            # print(filter_command)
            # print(wc_command)
            os.system(filter_command)
            count = os.popen(wc_command).read().replace('\n', '')
            year_to_wc[year] = int(count)

def calculate_neologisms(affix: str):
    # not the best method of doing this, but we identify neologisms by checking membership in nltk's dictionary.
    english_vocab = set(w.lower() for w in nltk.corpus.words.words())

    year_to_neologisms = {}
    all_neologisms = set() # record all seen neologisms so we can tell the first instance of a neologism

    def base_plausible(word: str):
        # checks I want to implement:
        # if base is a word
        # if affix is ity; if base + e is a word
        # if affix is ity and base also ends with -bil (ie was -bility) if substituting to base + ble is a word
        base = word[:-len(affix)]
        if base in english_vocab:
            return True
        if affix == 'ity':
            # this will return a few false positives, eg 'university -> universe' or 'gravity -> grave' or 'community -> commune' but there's not much to be done about that. Some of these false positives are also etymologically correct, even if modern speakers won't see it that way.
            # this will also return a couple other false positives because the nltk dictionary has some weird words. Apparently 'c' and 'ce' are both in the dictionary so 'city' counts as a word ending in -ity.
            if base + 'e' in english_vocab:
                return True
            if len(base) >= 3:
                potential_bil = base[-3:]
                if potential_bil == 'bil':
                    if base[:-3] + 'ble' in english_vocab:
                        return True
        return False

    def count_neologisms(file: str):
        neologism_count = 0
        neologisms = set() # neologisms that first appear in this year
        with open(file, 'r') as f:
            # replace null characters, which mess up the analysis. In COHA, a truly novel form has the null character listed as its lemma.
            # also remove periods, which could end word boundaries but sometimes got absorbed by the OCR
            f1 = [x.replace('\0', '').replace('.','') for x in f]
            reader = csv.reader(f1, delimiter='\t')
            
            for line in reader:
                # the column that used to be the word now has a colon in it due to using grep, so we filter out the file origin so we extract just the word:
                word = line[0].split(':', 1)[1]
                lemma = line[1]
                # You can add the clause and lemma != '' to filter out some words that were deemed OCR errors (and not given a lemma) but this judgment seems slightly overzealous and removes words like 'kittenishness (1977)' that I think are valid  
                if lemma not in english_vocab:
                    # we check to see if this is truly a neologism and not just an OCR error by checking if its base (plus minor modifications) is a real word
                    if base_plausible(word) and word not in all_neologisms:
                        neologism_count += 1
                        all_neologisms.add(word)
                        neologisms.add(word)
        print('found %d neologisms' % neologism_count)
        print(list(x for x in neologisms))

        # save the neologisms for future inspection
        filename = 'data/recorded_neologisms/' + file.split('/', 2)[2].split('.', 1)[0] + '_neologisms.json'
        with open(filename, 'w+') as f:
            json.dump(list(neologisms), f) # sets aren't json serializable

        return neologism_count

    for year in years:
        file_name = 'data/compiled_wlp/' + affix + '_' + str(year) + '.txt'
        count = count_neologisms(file_name)
        year_to_neologisms[year] = count
    return year_to_neologisms

# will take only the relevant affixed words and put them into files by year. This folder will contain those processed files.
os.system('mkdir data/compiled_wlp')
os.system('mkdir data/recorded_neologisms')

calculate_wc()
# serialize for later
with open('year_wc_data.json', 'w+') as f:
    json.dump(year_to_wc, f)
print(year_to_wc)

for affix in affixes:
    year_to_neologisms = calculate_neologisms(affix)
    filename = 'year_' + affix + '_neologism_data.json'
    with open(filename, 'w+') as f:
        json.dump(year_to_neologisms, f)
    print(year_to_neologisms)

