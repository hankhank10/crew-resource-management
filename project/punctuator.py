from fastpunct import FastPunct
# The default language is 'english'

fastpunct = FastPunct()
output = fastpunct.punct(["john smiths dog is creating a ruccus"])

print (output)