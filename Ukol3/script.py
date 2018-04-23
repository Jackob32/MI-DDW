import wikipedia
import nltk
from pprint import pprint


def extractEntities(ne_chunked):
    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join(word for word, tag in entity.leaves())
            label = entity.label()
            if text not in data:
                data[text] = [label, 1]
            else:
                data[text][1] += 1
    return data



def getByWiki(entity: str):

    page = wikipedia.page(entity)

    tagged_tokens = nltk.pos_tag(nltk.word_tokenize(page.summary))
    # for sentence in
    cp = nltk.RegexpParser("NP: {<DT>?<JJ>*<NN>}")
    chunked = cp.parse(tagged_tokens)

    for entity in chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            # ent = entity.label()
            return text

def getCustom(tagged):
    #Noun    NN
    #Proper   Noun    PNP
    #Adjective JJ
    #Pronoun PRP
    #Verb     VB
    #Adverb     RB
    #Proposition  IN
    #Conjunction CC


    result = {}
    entity = []
    for tagged_entry in tagged:
        for tagged_word in tagged_entry:
            if not entity: #if empty find first start
                    if tagged_word[1]=="NN" or tagged_word[1]=="NNP" or tagged_word[0]=="The":
                        entity.append(tagged_word)
            else: #found first start
                if entity[-1][1] == "NN" or entity[-1][1] == "NNP" or entity[-1][0] == "The":
                    if tagged_word[1]=="NNP":
                        entity.append(tagged_word)
                    elif tagged_word[1]=="IN":
                        entity.append(tagged_word)
                    elif tagged_word[1] == "CC":
                        id = " ".join([word[0] for word in entity])
                        if id not in result:
                            result[id] = [entity, 1]
                        else:
                            result[id][1] += 1
                        entity = []
                    else:
                        if entity[-1][0] != "The" and entity[-1][0] != "’" and entity[-1][0] != "”" :
                            id = " ".join([word[0] for word in entity])
                            if id not in result:
                                result[id] = [entity, 1]
                            else:
                                result[id][1] += 1
                        entity = []
                elif entity[-1][1] == "JJ":
                    if tagged_word[1] == "NNP" or tagged_word[1]=="NN":
                        entity.append(tagged_word)
                        entity = []
        entity=[]
    return result


# get the text information
text = None
with open('hp.txt', 'r') as f:
    text = f.read()

# the POS tagging
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    POS_tagged = [nltk.pos_tag(item) for item in tokens]

    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    ne_chunked = nltk.ne_chunk(tagged)


    #ne_chunked = nltk.ne_chunk(tagged, binary=True)

   # NER with entity classification (using nltk.ne_chunk)


# print POS tagged
    print("=" * 80)
    print("tagged_tokens")
pprint(POS_tagged[:20], indent=2)
print("=" * 80)

print("tokens")
print(tokens[:20])
print("=" * 80)

print("tokens")
print(tagged[:20])
print("=" * 80)

extentities=extractEntities(ne_chunked)
print("=" * 80)
print("Top recognized entities:")

print(sorted(extentities.items(), key=lambda entity: entity[1][1], reverse=True)[:20])


custom_parsed_entities = getCustom(POS_tagged)
print("=" * 80)
print("Top custom tagged entities:")
# Sort by value (entity[1]), using its second field (i.e. count)
sorted_entities = sorted(custom_parsed_entities.items(), key=lambda entity: entity[1][1], reverse=True)
for entity in sorted_entities[:20]:
    print(entity)

i=0
print("=" * 80)
print("Tagged NLTK entities through Wikipedia:")

for entity in extentities:
    try:
        category = getByWiki(entity)
        print(" {0} is  {1}".format(entity, category))
        i += 1;
        if(i>10):
            break
    except:
        pass

# using custom pattern
print("=" * 80)
print("Tagged custom entities through Wikipedia:")
i=0
for entity in sorted_entities:
    try:
        category = getByWiki(entity[0])
        print(" {0} is  {1}".format(entity[0], category))
        i+=1;
        if(i>10):
            break
    except:
        pass

#print(page.summary)