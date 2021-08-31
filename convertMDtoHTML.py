import markdown

with open('README.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text, extensions=['extra'])

with open('output.html', 'w') as f:
    f.write(html)