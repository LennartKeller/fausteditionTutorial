from lxml import etree
from Python_Tutorial_Handshift import Namespace

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
        
    def get_text(self, exclude=[]):
        """
        Gibt den Text, des handShifts Abschnitts zurück, dafür werden die ge:line Elemente ausgewertet
            :param exclude=[]: optional, zusätzliche Elemente, deren Text nicht ausgewertet werden soll
        """   
        handshift_parent = next(self.handShift.iterancestor())
        if handshift_parent:
            if handshift_parent.tag = self.genetic_edition_ns +  line

    def __repr__(self):
        """
        Eindeutige Stringrepräsentation der Objektinstanz
        """   
        return super().__repr__() + '\n' + self.source_doc + '\n' + self.writer_id + '\n' + str(self.content)


class HandshiftWriter:
    
    def write(self, handshifts, path: str):

        if isinstance(handshifts, list):
    
    def _get_text(self, handshift)



    