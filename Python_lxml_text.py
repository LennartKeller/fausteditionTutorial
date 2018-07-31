from lxml import etree

doc = etree.fromstring("""
<dokument>
    <zeile>Ich <verwischt/>einen Satz.</zeile>
</dokument>
""")

elem = doc.find("zeile")
elem2 = elem.find("verwischt")

print(elem.text)
print(elem2.tail)

def get_text(node):
    if node.text:
        yield node.text
    for child in node.iterchildren():
        yield from get_text(child)
    if node.tail:
        yield node.tail

print(list(get_text(doc)))