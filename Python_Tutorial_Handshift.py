#   Innerhalb der Transkripte sind die einzelnen handschriftlichen Abschnitte durch das TEI-Element handShift gekennzeichnet.
#   Dieses zeigt an,  dass ab hier der Text bis zum nächsten Auftreten eines handShift-Elements aus der Feder
#   des im @new-Attribut spezifizierten Schreibers ist. Der Wert dieses Attributes ist konform der xml:id aus den handNote-Elemente im Header,
#   so dass eine eindeutige Zuordnung der Abschnitte zu Schreiber und Schreibvariante möglich ist.
  
#   Nicht nur aus philologischer Sicht ist ein Auslesen dieser Daten interessant, sondern auch da die Datenstruktur eine 
#   kleine Herausforderung darstellt  - die handShift-Elemente sind leer, enthalten also keine Kindelemente. 
#   Die eigentlichen Daten der handShift-Einheit bilden also keinen Teilbaum des handShifts-Elements, 
#   den man einfach per XPath adressieren und auslesen könnte.
#   Im folgenden Beispiel werden diese Daten ausgelesen und in einer sehr einfachen Art verarbeitet und mit bereits bestehenden Daten aggregiert.

#   Das folgende Skript kann grob in 3 Abschnitte gegliedert werden, die eigene Teilaufgaben darstellen:

#   1. Definition von einfachen Hilfsklassen, in denen die Daten später gespeichert werden.
#   => Dies hat den Vorteil, dass im weiteren Programmablauf nicht mehr mit Listen hantiert werden muss, bei denen man auf die Daten nur
#   über einen "nicht sprechenden" Index zugreifen kann.

#   2. Auslesen der gesuchten Daten aus mehreren XML-Dateien mithilfe der beiden Bibliotheken glob und lxml. 
#   ACHTUNG: lxml gehört nicht zum Standardumfang einer Python-Installation, kann aber einfach mit : 'pip install lxml' nachinstalliert werden.
   
#   3. Im letzten Schritt werden die Daten dann in die Ergebnis-Datei aus dem XQuery-Beispiel integriert.
#   => Dies führt jedoch dazu, dass diese Datei relativ groß und unübersichtlich wird. Jedoch kann damit gut zeigen,
#   wie einfach sich mithilfe von lxml XML-Dateien modifizieren lassen.

from lxml import etree
import glob

# Datenklassen

class Namespace:
    """
        Klasse um alle den Namen eines Namensraum zu kapseln
    """
    def __init__(self, name, uri):  
        """
        Konstruktor
            :param name: Bezeichnung des Namesraum (wird später im namespace-dict von lxml als key verwendet)
            :param uri: URI des Namenraum
        """   
        self.name = name
        self.uri = uri
    
    def __str__(self):
        """
            Stringausgabe nach der Konvention für Namensraumprefixe von lxml.Element-Strings
        """
        return '{' + self.uri + '}'

class Handshift:
    """
        Klasse um alle Daten einer handShift-Einheit zu kapseln und zu verarbeiten.
    """
    def __init__(self, source_doc, element_list):
        """
        Konstruktor
            :param source_doc: Name des Quelldokuments in dem die handShift-Einheit gefunden wurde
            :param element_list: Liste aller Elemente der handShift-Einheit, das erste Element der Liste muss das handShift-Element sein, mit dem gestart wird
        """
        # Namensräume der transcript/** Dokumente
        self.tei_ns = Namespace('tei', 'http://www.tei-c.org/ns/1.0')
        self.genetic_edition_ns = Namespace('geneticEdition', 'http://www.tei-c.org/ns/geneticEditions')
        self.faustedition_ns = Namespace('faustedition', 'http://www.faustedition.net/ns')
        
        # Falls das erste Element der übergebenen Elementenliste kein handShift-Element ist wird ein Fehler geworfen
        if element_list[0].tag != str(self.tei_ns) + 'handShift':
            raise Exception('First element has to be tei:handShift')
        
        self.source_doc = source_doc
        self.handShift = element_list[0]
        self.new_attrib = self.handShift.attrib['new'][1:]
        if "_" in self.new_attrib:
            ids = self.new_attrib.split('_', 1)
            self.writer_id = ids[0]
            self.variant_id = ids[1] 
        else:
            self.writer_id = self.new_attrib
            self.variant_id = ''        
        self.content = element_list[1:]
        

    def get_text(self, text_elements=[]):
        """
        Gibt den Text, des handShifts Abschnitts zurück, dafür werden die ge:line Elemente ausgewertet
            :param text_elements=[]: optional, zusätliche Elemente, deren Text auch ausgewertet werden soll
        """   
        string = ''
        # Sonderfall:
        # Falls  sich das handShift-Element in einem Element befindet, das Text enhält muss dieses auch noch ausgelesen werden,
        # da das lxml-Datenmodel keine Textknoten kennt, sondern den Text als Attribut interpretiert
        try:
            handShift_parent = next(self.handShift.iterancestors())
            if handShift_parent:
                text = handShift_parent.xpath('text()')
                if len(text) > 0:
                    string += text[0]
        except StopIteration:
            pass
        text_elements.append(str(self.genetic_edition_ns) + 'line')

        # Iteration über alle Element des handShifts-Abschnitts
        for i in self.content:
            # falls das Element für den Text berücksichtigt wird und auch tatsächlich Text enthält, wird dieser an den Ergebnisstring angehängt
            if i.tag in text_elements and i.text:              
                string += i.text + '\n'
        return string
    
    def __repr__(self):
        """
        Eindeutige Stringrepräsentation der Objektinstanz
        """   
        return super().__repr__() + '\n' + self.source_doc + '\n' + self.writer_id + '\n' + str(self.content)

# Begin des eigentlichen Programmablaufs
if __name__ == '__main__':
    
    # Definition der Namensräume
    tei_ns = Namespace('tei', 'http://www.tei-c.org/ns/1.0')
    genetic_edition_ns = Namespace('geneticEdition', 'http://www.tei-c.org/ns/geneticEditions')
    faustedition_ns = Namespace('faustedition', 'http://www.faustedition.net/ns')

    # lxml-methoden benötigen die Namensräume als dictionary
    namespaces = {
        # falls der TEI-Namespace, der default-namespace sein soll:
        # None: tei_ns.uri,
        tei_ns.name: tei_ns.uri,
        genetic_edition_ns.name: genetic_edition_ns.uri,
        faustedition_ns.name: faustedition_ns.uri
    }
    
    # rekurisves Durchsuchen aller Unterordner des transcripts Verzeichnisses nach xml-Dateien
    files = glob.glob('../Referat/xml/transcript/**/*.xml', recursive=True)

    result = []

    for f in files:

        # einige Dokumente enthalten fehlerhafte xml:id Attribute und können nicht geparst werden
        # in diesem Fall wird eine Fehlermeldung ausgegeben
        try:
            doc = etree.parse(f)
        except etree.XMLSyntaxError as e:
            print('WARNING: Could not parse file {}.\n{}\n'.format(f, str(e)))
            continue
        
        # überspringe den aktuellen Schleifendurchlauf, falls das Dokument kein handShift Element enthält
        if not doc.xpath('//tei:handShift', namespaces=namespaces):
            continue

        # der doc_iterator enthält alle Elemente des Dokuments in der Textreihenfolge
        doc_iterator = doc.iter()
        
        # das Done-Objekt wird der next-Funktion übergeben, damit diese keinen StopIteration Fehler wirft, wenn der Iterator "leer" ist
        # dies hat den Vorteil, dass man keine Fehlerbehandlung implementieren muss
        done = object()
        
        # das erste Element des Iteratorsa
        elem = next(doc_iterator, done)
        
        # leere Liste wird später die handShift-Abschnitte als sublists enhalten
        total = []

        # in dieser Schleife wird durch das Element iteriert
        while elem is not done:
            # falls das aktuelle Element ein handShift-Element ist
            if elem.tag == str(tei_ns) + 'handShift':
                # initialisiere eine die Liste content mit diesem Element
                content = [elem]
                elem = next(doc_iterator, done)
                # diese Schleife wird solange durchlaufen, wie das aktuelle Element kein handShift-Element ist
                # dabei wird das aktuelle Element an die content-Liste angehängt
                while elem is not done and elem.tag != str(tei_ns) + 'handShift':
                    content.append(elem)
                    elem = next(doc_iterator, done)
                # handShift-Abschnitt wird dem Gesamtergebniss angehänt
                total.append(content) 
            else:
                elem = next(doc_iterator, done)

        for sublist in total:
            result.append(Handshift(f, sublist))

# Verknüpfen der mit den Daten der Schreibvarianten nach Autor

# Einlesen der Ergebnisses aus Tutorial 1
writer_doc = etree.parse('writerid_variantid_attributes.xml')

# Vorverarbeitungsschritt, jedes li-Element wird ein leeres ul-Element anghängt,
# in das später die Dateinamen geschrieben werden
for li in writer_doc.xpath('//tei:li', namespaces=namespaces):
    li.append(etree.Element(etree.QName(tei_ns.uri, 'ul'), type='file_list'))

# Iteration über alle handShift Objekte aus dem ersten Programmteil
for handshift in result:
    # Suchen des p-Elements im html das writer_id Attribut des aktuellen Handshift Objekt ist
    p_elem = writer_doc.find('//tei:p[@wID="{}"]'.format(handshift.writer_id), namespaces=namespaces)
    
    # falls ein solches gefunden wurde
    if p_elem is not None:
        
        # Suchen des Listenelement mit der akutellen varianten_id
        if handshift.variant_id:
            list_elem = p_elem.find('.//tei:li[@vID="{}"]'.format(handshift.variant_id), namespaces=namespaces)
        
        else:
            # wenn keine variant_id exisitert, wurde die writer_id verwendet
            list_elem = p_elem.find('.//tei:li[@vID="{}"]'.format(handshift.writer_id), namespaces=namespaces)
        # Test ob ein Listenelement gefunden wurde
        if list_elem is not None:
            # Anhängen des Listeneintrags mit dem Dateipfad, falls ein solcher noch nicht existiert
            if not list_elem.xpath('.//tei:li[text()="{}"]'.format(handshift.source_doc), namespaces=namespaces):
                new_li = etree.Element(etree.QName(tei_ns.uri, 'li'), type='file')
                new_li.text = handshift.source_doc
                list_elem.find('.//tei:ul', namespaces=namespaces).append(new_li)


    else:
        print('No entry with wID = {} was found.'.format(handshift.writer_id))

# für xhtml das vom Broswer verarbeitet werden kann muss die Ausgabe Datei als kanonisches XML geschrieben werden.
writer_doc.write_c14n('Python_Tutorial_Result.html')