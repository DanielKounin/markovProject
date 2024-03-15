from bs4 import BeautifulSoup
import sys

def isStartTag(txt):
    return len(txt) >= 3 and txt.startswith('<') and txt.endswith('>') and txt[1] != '/' and txt[1] != '!'
    # StartTags have a length greater than 3, are marked w/carrots on each side, and do not contain a '/'

def isEndTag(txt):
    return len(txt) >= 3 and txt.startswith('<') and txt.endswith('>') and txt[1] == '/'
    # EndTags are are characterized by a '/' after the carrot

def isComment(txt):
    return len(txt) >= 3 and txt.startswith('<') and txt.endswith('>') and txt[1] == '!'
    # Comments are distinguished by the '!'

def isXMLDeclaration(txt):
    return txt.startswith("<?") and txt.endswith("?>")
    # Declaration is marked with '<?' and '?>' on each side


def extractAttributes(txt):
    # Returns Key-Value pair dictionary of attributes of current Start Tag
    if isStartTag(txt):
        tag_name = extractTagName(txt)
        spoofed_tag = txt + '</' + tag_name + '>'
        soup = BeautifulSoup(spoofed_tag, 'xml')
        tag = soup.find(tag_name)
        attrs = tag.attrs
    else:
        raise Exception("TRYING TO EXTRACT ATTRIBUTES FROM NON-START TAG")
    return attrs

#clean the tag names
def extractTagName(txt):
    if isStartTag(txt):
        txt = txt[1: len(txt)-1] # Remove start and end <>
    elif isEndTag(txt):
        txt = txt[2: len(txt)-1] # Remove start <\ and end >
    else:
        raise Exception("THIS IS NOT A TAG")

    return txt.split(' ')[0]

#Remove beginning and end characters around the comments
def extractComment(txt):

    if isComment(txt):
        return txt[5:-4]
    else:
        raise Exception("TRYING TO EXTRACT COMMENT ON NON-COMMENT")



def extractTagPaths(docpath):

    def _tagList2Path(tagList):
        return '/' + '/'.join(tagList)

    # Read the file
    infile = open(docpath, encoding="utf8", mode="r")
    contents = infile.read()

    # Use Soup to Prettify and Create a List Containing Each Line In the Pretty XML
    soup = BeautifulSoup(contents, 'xml')
    pretty = soup.prettify()
    #print(pretty)
    docList = [txt.strip() for txt in pretty.split('\n')]
    #print(docList)

    tagList = [] # List of current tag structure we are inside
    outputList = [] # List that will be used to build output file

    for line in docList:
        #print(tagList)
        #for each line in the list figure out which kind of line it is
        if isXMLDeclaration(line):
            pass

        # If we get a Start Tag, then add that tag to our tagList
        elif isStartTag(line):
            tag_name = extractTagName(line)
            attrs = extractAttributes(line)
            tagList.append(tag_name) # add each tag name to the tagList as we iterate
            tag_path = _tagList2Path(tagList) # call the _tagList2Path function to join tagList values with a '/'
            for attr_k in attrs.keys():
                outputList.append(tag_path + '@' + attr_k + '=' + attrs[attr_k])
                # if a line has an attribute/value pair then we will add that to another line and use the '@' identifier
            outputList.append(tag_path)
            # add the appended tagList to the outputList

        # If we get an End Tag, we know that we are leaving the current tag and we can remove it from our tagList
        elif isEndTag(line):
            tag_name = extractTagName(line)
            if tag_name == tagList[-1]:  # if the tag name is equal to the last item in the tagList
                tag_path = _tagList2Path(tagList) # tagList without the attribute
                outputList.append(tag_path)
                tagList.pop()
            else:
                raise Exception("GOT UNMATCHED SET OF TAGS: " + tagList[-1] + " AND " + tag_name)


        elif isComment(line):
            outputList.append("/#comment= " + extractComment(line))


        else: # We found the actual text of the XML Document
            if len(outputList) != 0:
                outputList.append(outputList[-1] + "/#text=" + line)
            else:
                raise Exception("TEXT: " + line + " IS OUTSIDE OF XML TAGS")


    # Replace any HTML Entities
    outputList = [line.replace('&amp;', '&') for line in outputList]
    outputList = [line.replace('&gt;', '>') for line in outputList]
    outputList = [line.replace('&lt;', '<') for line in outputList]

    return outputList



def list2txtfile(l, path):
    textfile = open(path, encoding="utf8", mode="w")
    for element in l:
        textfile.write(element + "\n")
    textfile.close()




def main():

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    tagsOutput = extractTagPaths(input_path)
    list2txtfile(tagsOutput, output_path)

    return


if __name__ == '__main__':
    main()

