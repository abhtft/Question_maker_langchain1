a = {
    'HIGH': {
        'keywords': ['high', 'urgent', 'important', 'asap', 'quick', 'immediately',
                    'rush', 'priority', 'critical', 'essential', 'vital'],
        'display': 'High'  # Display format
    },
    'MEDIUM': {
        'keywords': ['medium', 'normal', 'regular', 'standard', 'moderate',
                    'average', 'ordinary', 'usual'],
        'display': 'Medium'  # Display format
    },
    'LOW': {
        'keywords': ['low', 'can wait', 'not urgent', 'whenever', 'flexible',
                    'casual', 'relaxed', 'later', 'eventually'],
        'display': 'Low'  # Display format
    }
}

# Fetching 'keywords' for all cases together
#all_keywords = {key: value['keywords'] for key, value in a.items()}
#print(all_keywords)
b=['low','happy','sad']

for k,v in a.items():
    for i in b:
        #var=sum(v['keywords'],[])

        if i in v['keywords']:
            print("Match found:", i)
            #print(a[i]) # Display the corresponding dictionary for the matched keyword
        else:
            print("No match found for:", i)


#print([value['display'] for value in a.values()])
#print([ value['keywords'] for value in a.values()])
# {'HIGH': ['high', 'urgent', 'important', 'asap', 'quick', 'immediately', 'rush', 'priority', 'critical', 'essential', 'vital'],

