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

def get_text_without_comments(node):

    if node.text and not isinstance(node, etree._Comment):
            yield node.text
    for child in node.iterchildren():
            yield from get_text_without_comments(child)
    if node.tail:
        yield node.tail

doc = etree.fromstring("""
<dokument>
    <zeile>Ich <verwischt/><!-- TODO: Überprüfen -->einen Satz.</zeile>
</dokument>
""")

print(list(get_text(doc)))
print(list(get_text_without_comments(doc)))