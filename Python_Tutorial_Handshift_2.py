from lxml import etree
import glob

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
    
    def __add__(self, other):
        """
        Verkettet den Namensraumprefix mit einem beliebigen String
            :param other: String der mit dem Namesraumprefix verkettet werden soll.
        """
        if not isinstance(other, str):
            raise TypeError("Other has to be of type str")
        return self.__str__() + other

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
        # Namensräume der XML-Dokumente
        self.tei_ns = Namespace('tei', 'http://www.tei-c.org/ns/1.0')
        self.genetic_edition_ns = Namespace('geneticEdition', 'http://www.tei-c.org/ns/geneticEditions')
        self.faustedition_ns = Namespace('faustedition', 'http://www.faustedition.net/ns')
        
        # Falls das erste Element der übergebenen Elementenliste kein handShift-Element ist wird ein Fehler geworfen
        if element_list[0].tag != str(self.tei_ns) + 'handShift':
            raise Exception('First element has to be tei:handShift')
        
        self.source_doc = source_doc
        self.handShift = element_list[0]

        # der Wert des new-Attributs hat die Form '#<writerid>_<styleid>' oder '#<writerid>_<styleid>_<stylesuffix>'
        # weshalb hier die Raute weggesch_<styleid>nitten wird und der String beim ersten Unterstrich geteilt wird
        self.new_attrib = self.handShift.attrib['new'][1:]
        if "_" in self.new_attrib:
            ids = self.new_attrib.split('_', 1)
            self.writer_id = ids[0]
            self.style_id = ids[1] 
        else:
            self.writer_id = self.new_attrib
            self.style_id = ''        
        self.content = element_list[1:]

    def recursive_dfs(self, node: etree.Element, exclude):

        """
        Generator-Funktion, durchläuft alle Nachkommen des (->Unterbaum) übergebenenen Elements und gibt den gefunden Text zurück.
            :param node: Knoten der der ausgewertet werden soll
            :param exclude: Liste mit tag Strings von Elementen deren Text nicht zurückgegeben werden soll    
        """

        if node.tag in exclude:
            return

        # Überprüfe, ob das betrachtete Element text enthält (vgl. Exkurs lxml-Textmodel)
        if node.text:
            yield node.text

        # Überprüfe, ob das betrachtete Element Kindeelemente hat
        children = list(node.iterchildren())
        for child in children:
            if child.tag == self.tei_ns + 'handShift':
                return
            yield from self.recursive_dfs(child, exclude)

        # Überprüfe, ob der Node text im Tail Attribut enthält (s.o.)
        if node.tail:
            yield node.tail

    def get_text(self, exclude=[])->str:
        """
        Gibt den Text, des handShifts Abschnitts zurück gibt. Dafür werden die ge:line Elemente ausgewertet
            :param exclude=[]: optional, zusätzliche Elemente, deren Text und der Text deren Kinder nicht ausgewertet werden soll
        """
        string = ''
        if self.handShift.tail:
            string += self.handShift.tail
        siblings = list(self.handShift.itersiblings())
        for i in siblings:
            text = self.recursive_dfs(i, exclude)
            string += ''.join(text)
        for i in self.content:
            if i.tag == self.genetic_edition_ns + 'line':
                text = self.recursive_dfs(i, exclude)
                string += ''.join(text)
        return string         

    
    def __repr__(self):
        """
        Eindeutige Stringrepräsentation der Objektinstanz
        """   
        return super().__repr__() + '\n' + self.source_doc + '\n' + self.writer_id + '\n' + str(self.content)

class HandshiftFactory:

    def __init__(self):
        # Definition der Namensräume
        self.tei_ns = Namespace('tei', 'http://www.tei-c.org/ns/1.0')
        self.genetic_edition_ns = Namespace('geneticEdition', 'http://www.tei-c.org/ns/geneticEditions')
        self.faustedition_ns = Namespace('faustedition', 'http://www.faustedition.net/ns')
        self.namespaces = {
            self.tei_ns.name: self.tei_ns.uri,
            self.genetic_edition_ns.name: self.genetic_edition_ns.uri,
            self.faustedition_ns.name: self.faustedition_ns.uri
        }
    
    def _search_xml_files(self, path:str)-> list:
        import glob
        
        if path.endswith('/'):
            path = path[:-1]

        files = glob.glob(path + '/**/*.xml', recursive=True)
        if not files:
            raise Warning('No XML Files were found.')
        return files

    def run(self, path:str)->list:

        if path.endswith('.xml'):
            files = [path]
        else:
            files = self._search_xml_files(path)

        result = []
        for f in files:

            # Im Falle von Fehlern bei Parsen der Dokumente wird eine Fehlermeldung ausgegeben und diese Datei wird übersprungen.
            try:
                doc = etree.parse(f)
            except etree.XMLSyntaxError as e:
                print('WARNING: Could not parse file {}.\n{}\n'.format(f, str(e)))
                continue
            
            # überspringe den aktuellen Schleifendurchlauf, falls das Dokument kein handShift Element enthält
            if not doc.xpath('//tei:handShift', namespaces=self.namespaces):
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
                if elem.tag == self.tei_ns + 'handShift':
                    # initialisiert eine die Liste content mit diesem Element
                    content = [elem]
                    elem = next(doc_iterator, done)
                    # diese Schleife wird solange durchlaufen, wie das aktuelle Element kein handShift-Element ist
                    # dabei wird das aktuelle Element an die content-Liste angehängt
                    while elem is not done and elem.tag != self.tei_ns + 'handShift':
                        content.append(elem)
                        elem = next(doc_iterator, done)
                    # handShift-Abschnitt wird dem Gesamtergebnis angehängt
                    total.append(content) 
                else:
                    elem = next(doc_iterator, done)

            for sublist in total:
                result.append(Handshift(f, sublist))

        return result
    
class HandshiftWriter:

    @staticmethod
    def write_txt(handshifts:list, destination:str, exclude=[]):
        import os
        import re
        if not os.path.isdir(destination):
            os.mkdir(destination)
        # dieser regulärer Ausdruck ermöglicht es Pfadangaben zu Datein in den Pfad, dem Dateinamen und die Dateiendung zu zerlegen.
        # eine genaue Erklärung kann unter https://techtavern.wordpress.com/2009/04/06/regex-that-matches-path-filename-and-extension/ gefunden werden
        regex = re.compile(r'^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))')
        for handshift in handshifts:
            source_doc_splitted = re.match(regex, handshift.source_doc)
            source_doc_filename = source_doc_splitted.group(2)
            filename = destination + '/' + '_'.join((source_doc_filename, handshift.writer_id, handshift.style_id)) + '.txt'
            with open(filename, 'w', encoding='UTF-8') as f:
                f.write(handshift.get_text(exclude))
            
            

# Begin des eigentlichen Programmablaufs
if __name__ == '__main__':

    factory = HandshiftFactory()
    result = factory.run('xml')
    HandshiftWriter.write_txt(result, 'firstTest')