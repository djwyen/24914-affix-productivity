import json
import numpy as np
import matplotlib.pyplot as plt

with open('year_wc_data.json', 'r') as f1:
    year_to_wc = json.load(f1)
with open('year_ness_neologism_data.json', 'r') as f2, open('year_ity_neologism_data.json', 'r') as f3:
    ness_year_to_neologisms = json.load(f2)
    ity_year_to_neologisms = json.load(f3)
years = list(year_to_wc.keys())

wordcounts = np.array([year_to_wc[year] for year in years])
ness_neologisms = np.array([ness_year_to_neologisms[year] for year in years])
ity_neologisms = np.array([ity_year_to_neologisms[year] for year in years])
ness_percent_neologisms = np.divide(ness_neologisms, wordcounts)
ity_percent_neologisms = np.divide(ity_neologisms, wordcounts)
years = np.array(years, dtype=np.dtype('float64'))
print(year_to_wc)
print(ness_year_to_neologisms)
print(ity_year_to_neologisms)
# TODO should I take the log and plot that instead?

# calculate best fit line and plot
slope1, b1 = np.polyfit(years, ness_percent_neologisms, 1)
slope2, b2 = np.polyfit(years, ity_percent_neologisms, 1)
# convert to np arrays

plt.plot(years, ness_percent_neologisms, 'C0o')
plt.plot(years, ity_percent_neologisms, 'C1o')
plt.plot(years, (years*slope1 + b1), 'C0')
plt.plot(years, (years*slope2 + b2), 'C1')
plt.legend(['-ness', '-ity'])
plt.title('% neologisms per year')
plt.xlabel('Year')
plt.ylabel('Neologism % of total word count')
plt.show()

# we can also plot the actual # of neologisms per year. Of course, be wary that each year has a different number of documents, and therefore words, in it.
width = .4
plt.bar(years - (width / 2), ness_neologisms, width=width, label='-ness', color='C0')
plt.bar(years + (width / 2), ity_neologisms, width=width, label='-ity', color='C1')
max_neologisms = max(max(ness_neologisms), max(ity_neologisms))
plt.yticks(range(0, max_neologisms + 1, 2))
# plt.xticks(years + width / 2)
plt.legend(loc='best')
plt.title('Number of neologisms per year')
plt.xlabel('Year')
plt.ylabel('Neologisms')
plt.show()