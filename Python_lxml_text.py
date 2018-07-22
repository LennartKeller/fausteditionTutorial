from lxml import etree

doc = etree.fromstring("""
<dokument>
    <zeile>Hallo <unklar>daf<vielleicht>s</vielleicht></unklar> ist ein Satz.</zeile>
</dokument>
""")
elem = doc.find("zeile")
print(elem.text)
