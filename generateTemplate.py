import argparse
import os

parser = argparse.ArgumentParser(description='File Inputs')
parser.add_argument('-g', action='store', dest='tf_file',
                    help='the tf-docs file that gets merged with the template')
parser.add_argument('-t', action='store', dest='template_file',
                    help='the template file to base the output file on when merging with the generated tf-docs file')
parser.add_argument('-o', action='store', dest='output_file',
                    help='the destination file to output to. THIS WILL OVERWRITE THE FILE!!')

args = parser.parse_args()


class Section:
    def __init__(self, heading, body):
        self.heading = heading
        self.body = body


order = ['Requirements', 'Providers',
         'Modules', 'Inputs', 'Outputs', 'Resources']


def swapSection(sec1, sec2):
    sec1, sec2 = sec2, sec1


tfdoc_sections = []
readme_sections = []

# search arr for a section with the provided heading, return index if found, -1 if not


def contains(arr, heading):
    for i in range(0, len(arr), 1):
        if(arr[i].heading.strip(' ') in heading.strip(' ') or heading.strip(' ') in arr[i].heading.strip(' ')):
            return i
    return -1


def reorderSections(arr, offset):
    orderedSections = []
    print('Reordering')
    for i in range(0, len(arr), 1):
        print('Reordering {}'.format(arr[i].heading))
        if arr[i].heading.strip(' ')[3:] in order:
            print('{} is in order'.format(arr[i].heading))
            index = contains(arr, order[i - offset])
            print('Current Item: {}, Index: {}, Index Item: {}'.format(
                arr[i].heading, index, arr[index].heading))
            orderedSections.append(arr[index])
        else:
            orderedSections.append(arr[i])
            print('{} is not in order'.format(arr[i].heading))
            if i > offset:
                offset += 1
    return orderedSections

# check to make sure that arr1 has all elements of arr2 and any additions that need made will be added at the offset


def reconcileDifferences(arr1, arr2, offset):
    for section in arr2:
        index = contains(arr1, section.heading)
        if not index == -1:
            if not section.body == arr1[index].body:
                arr1[index].body = section.body
        else:
            arr1.insert(offset, section)


def chunk(arr):
    begArr = []
    endArr = []
    chunkArr = []
    for i in range(0, len(arr), 1):
        if arr[i].heading.strip('#').strip(' ') in order:
            chunkArr.append(arr[i])
        else:
            if (i + 1) <= len(arr)/2:
                begArr.append(arr[i])
            else:
                endArr.append(arr[i])

    return begArr + chunkArr + endArr


# init
def readTemplate():
    global tfdoc_sections
    currentHeading = ''
    bodyLines = []
    stripNewLineOnly = False
    try:
        with open(args.tf_file) as f:
            line = f.readline()
            while line != '':
                if '```' in line:
                    stripNewLineOnly = not stripNewLineOnly
                if stripNewLineOnly:
                    line = line.rstrip(' \n')
                    line = line.strip('\n')
                else:
                    line = line.strip(' \n')
                if line == '':
                    line = f.readline()
                    continue
                if line[:3] == '## ':
                    if currentHeading == '':
                        currentHeading = line
                    else:
                        tfdoc_sections.append(
                            Section(currentHeading, bodyLines))
                        currentHeading = line
                        bodyLines = []
                elif line[:3] == '<!-' or line == '\n' or line == '\r\n':
                    line = f.readline()
                    continue
                else:
                    bodyLines.append(line)
                line = f.readline()
            tfdoc_sections.append(Section(currentHeading, bodyLines))
    except IOError as e:
        # if we dont have the file then we need to
        print(e)

# base read off of the template we read in


def readREADME():
    global readme_sections
    currentHeading = ''
    bodyLines = []
    stripNewLineOnly = False
    try:
        with open(args.template_file) as f:
            if os.stat(args.template_file).st_size == 0:
                return
            line = f.readline()
            while line != '':
                if '```' in line:
                    stripNewLineOnly = not stripNewLineOnly
                if stripNewLineOnly:
                    line = line.rstrip(' \n \r')
                else:
                    line = line.strip(' \n \r')
                if line[:2] == '# ':
                    if currentHeading == '':
                        currentHeading = line
                    else:
                        readme_sections.append(
                            Section(currentHeading, bodyLines))
                        currentHeading = line
                        bodyLines = []
                elif line[:3] == '## ':
                    if currentHeading == '':
                        currentHeading = line
                    else:
                        if not currentHeading[:2] == '# ' or line[3:].strip('# ') in order:
                            readme_sections.append(
                                Section(currentHeading, bodyLines))
                            currentHeading = line
                            bodyLines = []
                        else:
                            bodyLines.append(line)
                elif line[:3] == '<!-' or line == '\n' or line == '\r\n':
                    line = f.readline()
                    continue
                else:
                    bodyLines.append(line)
                line = f.readline()
            readme_sections.append(Section(currentHeading, bodyLines))
    except IOError as e:
        pass


# read in the files
readTemplate()
readREADME()

print('After Read in')
for section in readme_sections:
    print(section.heading)
print('\n')

readme_sections = chunk(readme_sections)

print('After Chunking')
for section in readme_sections:
    print(section.heading)
print('\n')

outputSections = []
offset = 0

for section in readme_sections:
    if section.heading.strip(' ')[:3] == '## ' and section.heading.strip(' ')[3:] in order:
        break
    offset += 1

reconcileDifferences(readme_sections, tfdoc_sections, offset)

print('After Reconciling differences')
for section in readme_sections:
    print(section.heading)
print('\n')

test = reorderSections(readme_sections, offset)

print('After Reorder')
for section in test:
    print(section.heading)
print('\n')

try:
    with open(args.output_file, 'w') as f:
        for section in test:
            f.write(section.heading)
            f.write('\n\n')
            for line in section.body:
                if line:
                    # print("Writing \"{}\" to file".format(len(line)))
                    if '#' in line[0]:
                        f.write("\n")
                    f.write(line)
                    if '#' in line[0]:
                        f.write("\n")
                    f.write('\n')
            f.write("\n")

except IOError as e:
    print(e)
