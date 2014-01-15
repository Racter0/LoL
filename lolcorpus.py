import os
import nltk
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk import FreqDist, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
import random
from nltk.cluster import KMeansClusterer, euclidean_distance
import numpy
#make a corpus from the lore
lorecorpus= PlaintextCorpusReader('/Users/ruskinr/Desktop/nlp/loltxts/paras', '.*')


#annotate txts with gender and affiliation of champion
#ambiguities from my interpretation of lore vs official affiliation on webpage:
#riot/me
#amumu= bandlecity*/shurima
#annie=independent/noxus*
#cass=shurima/noxus*
#heim=bandlecity/piltover*
#janna=independent/(zaun* or piltover)
#jinx=zaun*/piltover
#kayle=demacia/independent*
#lucian=demacia/shadowisles* or independent
#morgana=noxus/independent*
#tf=bilgewater*/zaun
annotated=(['aatrox.txt', 'male', 'independent'],['ahri.txt','female','ionia'],['akali.txt','female','ionia'],
           ['alistar.txt','male','independent'],['amumu.txt','male','bandlecity'],['anivia.txt','female','freljord'],
           ['annie.txt','female','noxus'],['ashe.txt','female','freljord'],['blitzcrank.txt','male','zaun'],
           ['brand.txt','male','independent'],['caitlyn.txt','female','piltover'],['cassiopeia.txt','female','noxus'],
           ['chogath.txt','male','void'],['corki.txt','male','bandlecity'],['darius.txt','male','noxus'],
           ['diana.txt','female','targon'],['drmundo.txt','male','zaun'],['draven.txt','male','noxus'],
           ['elise.txt','female','shadowisles'],['evelynn.txt','female','shadowisles'],['ezreal.txt','male','piltover'],
           ['fiddlesticks.txt','male','independent'],['fiora.txt','female','demacia'],['fizz.txt','male','bilgewater'],
           ['galio.txt','male','demacia'],['gangplank.txt','male','bilgewater'],['garen.txt','male','demacia'],
           ['gragas.txt','male','freljord'],['graves.txt','male','bilgewater'],['hecarim.txt','male','shadowisles'],
           ['heimerdinger.txt','male','piltover'],['irelia.txt','female','ionia'],['janna.txt','female','zaun'],
           ['jarvaniv.txt','male','demacia'],['jax.txt','male','independent'],['jayce.txt','male','piltover'],
           ['jinx.txt','female','zaun'],['karma.txt','female','ionia'],['karthus.txt','male','shadowisles'],
           ['kassadin.txt','male','void'],['katarina.txt','female','noxus'],['kayle.txt','female','independent'],
           ['kennen.txt','male','ionia'],['khazix.txt','male','void'],
           ['kogmaw.txt','male','void'],['leblanc.txt','female','noxus'],['leesin.txt','male','ionia'],['leona.txt','female','targon'],
           ['lissandra.txt','female','freljord'],['lucian.txt','male','shadowisles'],['lulu.txt','female','bandlecity'],
           ['lux.txt','female','demacia'],['malphite.txt','male','independent'],['malzahar.txt','male','void'],
           ['maokai.txt','male','independent'],['masteryi.txt','male','ionia'],['missfortune.txt','female','bilgewater'],
           ['mordekaiser.txt','male','shadowisles'],['morgana.txt','female','independent'],['nami.txt','female','independent'],
           ['nasus.txt','male','shurima'],['nautilus.txt','male','bilgewater'],['nidalee.txt','female','independent'],
           ['nocturne.txt','male','independent'],['nunu.txt','male','freljord'],['olaf.txt','male','freljord'],
           ['orianna.txt','female','piltover'],['pantheon.txt','male','targon'],['poppy.txt','female','bandlecity'],
           ['quinn.txt','female','demacia'],['rammus.txt','male','shurima'],['renekton.txt','male','shurima'],
           ['rengar.txt','male','independent'],['riven.txt','female','noxus'],['rumble.txt','male','bandlecity'],
           ['ryze.txt','male','independent'],['sejuani.txt','female','freljord'],['shaco.txt','male','independent'],
           ['shen.txt','male','ionia'],['shyvana.txt','female','demacia'],['singed.txt','male','zaun'],
           ['sion.txt','male','noxus'],['sivir.txt','female','shurima'],['skarner.txt','male','independent'],
           ['sona.txt','female','demacia'],['soraka.txt','female','ionia'],['swain.txt','male','noxus'],
           ['syndra.txt','female','ionia'],['talon.txt','male','noxus'],['taric.txt','male','independent'],
           ['teemo.txt','male','bandlecity'],['thresh.txt','male','shadowisles'],['tristana.txt','female','bandlecity'],
           ['trundle.txt','male','freljord'],['tryndamere.txt','male','freljord'],['twistedfate.txt','male','bilgewater'],
           ['twitch.txt','male','zaun'],['udyr.txt','male','freljord'],['urgot.txt','male','noxus'],
           ['varus.txt','male','ionia'],['vayne.txt','female','demacia'],['veigar.txt','male','bandlecity'],
           ['vi.txt','female','piltover'],['viktor.txt','male','zaun'],['vladimir.txt','male','noxus'],
           ['volibear.txt','male','freljord'],['warwick.txt','male','zaun'],['wukong.txt','male','ionia'],
           ['xerath.txt','male','shurima'],['xinzhao.txt','male','demacia'],['yasuo.txt','male','ionia'],
           ['yorick.txt','male','shadowisles'],['zac.txt','male','zaun'],['zed.txt','male','ionia'],
           ['ziggs.txt','male','bandlecity'],['zilean.txt','male','independent'],['zyra.txt','female','independent'])

#in order to try to classify these short texts, we're going to take the most common (interesting) words.
#First create word bank, then use words as features.


#split text into words, pos tag, remove some boring words based on tags
def parse_and_tag(corpus):
    boring_tags=['CC','DT',',','IN','PRP','PRP$','VBZ','TO','POS',':','(',')','AT','.',"''"]
    if isinstance(corpus,basestring):
        with lorecorpus.open(corpus) as fin:
            sents=nltk.sent_tokenize(fin.read().strip())
    else:
        sents=nltk.sent_tokenize(corpus.raw().strip())
    tagged_text_unmerged=([nltk.pos_tag(nltk.word_tokenize(sent)) for sent in sents])
    #make a list of tuples, not a list of lists of tuples
    tagged_text=[item for sublist in tagged_text_unmerged for item in sublist]
    all_word_tuples=[(word[0].lower(), word[1]) for word in tagged_text if word[1] not in boring_tags]
    #turn the tuples into lists
    all_word_lists=[list(word) for word in all_word_tuples]
    all_words=[a for (a,b) in all_word_tuples]
    return all_word_lists
###
###
#convert nltk pos tags to wordnet pos tags
def convert_pos(postag):

    if postag.startswith('J'):
        return 'a'
    elif postag.startswith('V'):
        return 'v'
    elif postag.startswith('N'):
        return 'n'
    elif postag.startswith('R'):
        return 'r'
    else:
        return 'u'
###
###
#lemmatize tagged wordset
def lemmatize(word_list):

    wordnet_tagged=[[word, convert_pos(pos)] for [word,pos] in word_list]
    wnl=nltk.WordNetLemmatizer()
    lemmas=[wnl.lemmatize(word[0],word[1]) for word in wordnet_tagged if word[1] != 'u']
    #the lemmatizer doesn't know words not in its dictionary, so do some manual lemmatizing
    #also remove more boring words
    excluded_words=["n't",'be','have','do']
    for index,word in enumerate(lemmas):
        if word == 'demacian' or word == 'demacians':
            lemmas[index] = 'demacia'
        elif word == 'noxian' or word == 'noxians':
            lemmas[index] = 'noxus'
        elif word == 'ionian' or word == 'ionians':
            lemmas[index] = 'ionia'
        elif word in excluded_words:
            lemmas.remove(word)
    
    return lemmas
###
###

all_word_lists=parse_and_tag(lorecorpus)
lemmas=lemmatize(all_word_lists)

#make a frequency distribution of words; take only ones over 2
freq_words=FreqDist(lemmas)
common_words=[word for word in freq_words.keys() if freq_words[word]>2]
#print common_words

#define features for classification
###
def freq_features(loretext):
    lore_words_long= parse_and_tag(loretext)
    lore_words=lemmatize(lore_words_long)
    features={}
    for word in common_words:
        features['contains(%s)' % word] = (word in lore_words)
    return features



########Used this segment to find feminine words.
###list of tuples of genders
genders=[(a,b) for [a,b,c] in annotated]


accuracies=[]
top_ten=[]
for i in range(10):
    #try a test set and a training set:
    random.shuffle(genders)
    featuresets=[(freq_features(d),a) for (d,a) in genders]
    test_lore, train_lore=genders[:10], genders[10:]
    test_set, train_set= featuresets[:10], featuresets[10:]

    classifier=nltk.NaiveBayesClassifier.train(train_set)

    for (word,fval) in classifier.most_informative_features(50):
        atuple=(word,fval)
        top_ten.append(atuple)

    accuracy=nltk.classify.accuracy(classifier, test_set)
    print accuracy
    accuracies.append(accuracy)


####################This segment is for finding words that
#characterize affiliations    
#list of tuples of affiliations
affiliation=[(a,c) for [a,b,c] in annotated]
demacia=[]
for (a,b) in affiliation:
    if b=='demacia':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    demacia.append(atuple)

noxus=[]
for (a,b) in affiliation:
    if b=='noxus':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    noxus.append(atuple)

bandle=[]
for (a,b) in affiliation:
    if b=='bandlecity':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    bandle.append(atuple)

shadow=[]
for (a,b) in affiliation:
    if b=='shadowisles':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    shadow.append(atuple)

void=[]
for (a,b) in affiliation:
    if b=='void':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    void.append(atuple)
    
ionia=[]
for (a,b) in affiliation:
    if b=='ionia':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    ionia.append(atuple)

freljord=[]
for (a,b) in affiliation:
    if b=='freljord':
        atuple=(a,b)
    else:
        atuple=(a,'elsewhere')
    freljord.append(atuple)    
featuresets=[(freq_features(d),a) for (d,a) in freljord]
classifier=nltk.NaiveBayesClassifier.train(featuresets)

classifier.show_most_informative_features(20)


###################This is for K-means clustering.
# our vectors are going to have dimensions equal to a number of features.
# each direction can only have magnitude one or zero
def get_word_freq(loretext):
    lore_words_long=parse_and_tag(loretext)
    lore_words=lemmatize(lore_words_long)
    freq_lore=FreqDist(lore_words)
    return freq_lore.items()

    
num_clusters=20
vec_len=len(common_words)
vector_words=common_words[:vec_len]
word_freqs=[get_word_freq(text) for [text,a,b] in annotated]
tmp_vector=[]
for champ_freq in word_freqs:
    for word in vector_words:
        appendable=None
        for (aword, afreq) in champ_freq:
            if word == aword:
                appendable=afreq
        if appendable==None:
            tmp_vector.append(0)
        else:
            tmp_vector.append(appendable)
            
vector_list=[tmp_vector[i:i+vec_len] for i in range(0, len(tmp_vector), vec_len)]
word_array=numpy.array(vector_list)
clusterer= KMeansClusterer(num_clusters, euclidean_distance, repeats=10)
clusters = clusterer.cluster(word_array, True)
enum_clusters=list(enumerate(clusters))
enum_clusters.sort(key=lambda x: x[1])
clustered_champs= [(annotated[index][0], clus_num) for (index , clus_num) in enum_clusters]


print('clustered_champs',clustered_champs)

