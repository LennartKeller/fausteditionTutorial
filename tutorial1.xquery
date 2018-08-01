declare namespace f = "http://www.faustedition.net/ns";
declare namespace ge = "http://www.tei-c.org/ns/geneticEditions";
declare namespace TEI = "http://www.tei-c.org/ns/1.0";
declare namespace functx = "http://www.functx.com";

declare function functx:substring-before-match
( $arg as xs:string? ,
    $regex as xs:string )  as xs:string {

   tokenize($arg,$regex)[1]
 } ;
 
 declare function functx:substring-after-match
  ( $arg as xs:string? ,
    $regex as xs:string )  as xs:string? {

   replace($arg,concat('^.*?',$regex),'')
 } ;
 
 
<xhtml xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:TEI="http://www.tei-c.org/ns/1.0">
<head>
    <meta http-equiv="content-type" content="text/xhtml; char set=utf-8"/>
    <title>Writers and their writing materials</title>
</head>
    <h2>Writers and their writing materials</h2>
<p>{

let $path := "C:/Fausteditionen/transcript/agad_warszawa/test/0020.xml"    (: zu modifizierende Zeile für hardcode/softcode :)
let $file := for $file in doc(concat('file:///',$path,'?recurse=yes')) return if ($file//TEI:handNotes) then $file else error( QName('','ElementRequest'),  "Missing required element 'handNotes'")
(: Liste mit allen handNote Elementen wird in Liste gespeichert :)
let $handNotes := $file//TEI:handNote    (: zu modifizierende Zeile für hardcode/softcode :)
(: sammelt alle vorkommenden IDs der Schreiber aus den Elementen :)
let $wIDcollection := for $writerID in $handNotes/functx:substring-before-match(data(@xml:id), '_') return $writerID   

let $wIDs := for $wID in fn:distinct-values($wIDcollection) return $wID  (: eliminiert Dopplungen :) 
(: iteriert über Liste der Schreiber-IDs :)
for $currentWID in $wIDs     
order by $currentWID
return  

(: generiert einen <p/>-Block für jeden Schreiber mit Attributen Typ und Schreiber-ID :)
<p type="writer" wID="{$currentWID}">{
(: Liste mit allen Elementen, die sich auf den aktuellen Schreiber beziehen :)
let $stylesOfCurrentWriter := for $eachStyle in $handNotes where $file/functx:substring-before-match($eachStyle/data(@xml:id), '_') = $currentWID return $eachStyle   (: zu modifizierende Zeile für hardcode/softcode :)
(: Liste mit den Schreibernamen aus allen relevanten Elementen :)
let $currentWriterName := for $name in $stylesOfCurrentWriter/functx:substring-before-match(text(), '\s\(') return $name   
(: eliminiert Dopplungen :)
let $writer := fn:distinct-values($currentWriterName)      
return 
(<h4>{$writer}</h4>,
<ul>{
(: sammelt alle vorkommenden IDs der Styles aus den aktuell relevanten Elementen :) 
let $sIDcollection := for $style in $stylesOfCurrentWriter/functx:substring-after-match(data(@xml:id), '_') return $style 
 (: iteriert über Liste der Style-IDs :)
for $currentSID in $sIDcollection  
order by $currentSID
return
(: generiert einen Listeneintrag für jeden Style mit Attributen Typ und Style-ID :) 
<li type="style" sID="{$currentSID}">{
(: ordnet Elemente der aktuellen Style ID zu :)
let $styleList := for $eachStyle in $stylesOfCurrentWriter where $file/functx:substring-after-match($eachStyle/data(@xml:id), '_') = $currentSID return $eachStyle    (: zu modifizierende Zeile für hardcode/softcode :) 
(: liest die Stylebezeichnung aus Element aus :)
let $currentStyle := for $style in $styleList/functx:substring-before-match(functx:substring-after-match(text(), '\s+\('), '\)') return $style   
return 
$currentStyle
}
</li>
}
</ul>)
}
</p>
}
</p>
</xhtml>
