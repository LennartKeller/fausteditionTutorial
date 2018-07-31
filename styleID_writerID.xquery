declare namespace functx = "http://www.functx.com";
declare function functx:substring-before-match
( $arg as xs:string? ,
    $regex as xs:string )  as xs:string {
    (:test:)
   tokenize($arg,$regex)[1]
 } ;
 declare function functx:substring-after-match
  ( $arg as xs:string? ,
    $regex as xs:string )  as xs:string? {

   replace($arg,concat('^.*?',$regex),'')
 } ;

<html xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:TEI="http://www.tei-c.org/ns/1.0">
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Variant - Writer</title>
</head>
<p>
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $data := doc('file:///C:/Fausteditionen/transcript/agad_warszawa/PL_1_354_13-16-24/0012.xml')
(: zu modifizierende Zeile für hardcode/softcode :)
let $list := $data//TEI:handNote   (: Liste mit allen handNote Elementen wird in $list gespeichert :)
let $sIDcollection := for $i in $list/functx:substring-after-match(data(@xml:id), '_') return $i (: sammelt alle vorkommenden IDs der Varianten aus den Elementen :)
let $sIDlist := for $i in fn:distinct-values($sIDcollection) return $i  (: eliminiert Dopplungen :) 
for $currentSID in $sIDlist     (: iteriert über Liste der Varianten-IDs :)
order by $currentSID
return  
(: generiert einen <p/>-Block für jeden Schreiber mit Attributen Typ und Varianten-ID :)
<p type="variant" vID="{$currentSID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $styleList := for $i in $list where $data/functx:substring-after-match($i/data(@xml:id), '_')=$currentSID return $i    (: Liste mit allen Elementen, die sich auf die aktuelle Variante beziehen :)
let $style := for $i in $styleList/functx:substring-before-match(functx:substring-after-match(text(), '\s+\('), '\)') return $i     (: Liste mit den Varianten aus allen relevanten Elementen :)
let $currentStyle := for $i in fn:distinct-values($style) return $i      (: eliminiert Dopplungen :)
return 
(<h4>{$currentStyle[1]}</h4>,
<ul>{
let $wIDcollection := for $i in $styleList/functx:substring-before-match(data(@xml:id), '_') return $i (: sammelt alle vorkommenden IDs der Schreiber aus den aktuell relevanten Elementen :) 
for $currentWID in $wIDcollection   (: iteriert über Liste der Varianten-IDs :)
order by $currentWID
return
(: generiert einen Listeneintrag für jede Variante mit Attributen Typ und Varianten-ID :) 
<li type="writer" wID="{$currentWID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $writerList := for $i in $list where $data/functx:substring-before-match($i/data(@xml:id), '_')=$currentWID return $i   (: ordnet Elemente der aktuellen Schreiber ID zu :)
let $currentWriter := for $i in $writerList/functx:substring-before-match(text(), '\s\(') return $i   (: liest den Schreiber aus Element aus :)
return $currentWriter[1] (: eliminiert Dopplungen und schreibt Schreibernamen in den Listeneintrag :)
}    
</li>}
</ul>)
}</p>
}
</p>
</html>
