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