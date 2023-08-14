
from textblob_FR import TextBlob
text = "bonjour"
blob = unicode( text , "utf-8")
print "Unicode text" + blob

eng_blob = TextBlob(blob)
print eng_blob.translate(from_lang="fr", to='en')

try:
	eng_blob = TextBlob(blob)
	sentenceRecognized = eng_blob.translate(from_lang="fr", to='en')
	print sentenceRecognized
	print type(sentenceRecognized)
	print str(sentenceRecognized)
	type(sentenceRecognized)
except:
	print "No translation"