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

<html xmlns="http://www.tei-c.org/ns/1.0" 
  xmlns:TEI="http://www.tei-c.org/ns/1.0">
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Writer - Variant</title>
</head>
<p>
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $data := doc('file:///C:/Fausteditionen/transcript/agad_warszawa/PL_1_354_13-16-24/0012.xml') 
(: zu modifizierende Zeile für hardcode/softcode :)
let $list := $data//handNote     (: Liste mit allen handNote Elementen wird in $list gespeichert :)
let $wIDcollection := for $i in $list/functx:substring-before-match(data(@xml:id), '_') return $i   (: sammelt alle vorkommenden IDs der Schreiber aus den Elementen :)
let $wIDlist := for $i in fn:distinct-values($wIDcollection) return $i  (: eliminiert Dopplungen :) 
for $currentWID in $wIDlist     (: iteriert über Liste der Schreiber-IDs :)
order by $currentWID
return  
(: generiert einen <p/>-Block für jeden Schreiber mit Attributen Typ und Schreiber-ID :)
<p type="writer" wID="{$currentWID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $writerList := for $i in $list where $data/functx:substring-before-match($i/data(@xml:id), '_')=$currentWID return $i    (: Liste mit allen Elementen, die sich auf den aktuellen Schreiber beziehen :)
let $currentWriter := for $i in $writerList/functx:substring-before-match(text(), '\s\(') return $i     (: Liste mit den Schreibernamen aus allen relevanten Elementen :)
let $writer := for $i in fn:distinct-values($currentWriter) return $i      (: eliminiert Dopplungen :)
return 
(<h4>{$writer}</h4>,
<ul>{
let $vIDcollection := for $i in $writerList/functx:substring-after-match(data(@xml:id), '_') return $i (: (: sammelt alle vorkommenden IDs der Varianten aus den aktuell relevanten Elementen :) :)
for $currentVID in $vIDcollection   (: iteriert über Liste der Varianten-IDs :)
order by $currentVID
return
(: generiert einen Listeneintrag für jede Variante mit Attributen Typ und Varianten-ID :) 
<li type="variant" vID="{$currentVID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $variantList := for $i in $list where $data/functx:substring-after-match($i/data(@xml:id), '_')=$currentVID return $i    (: ordnet Elemente der aktuellen Varianten ID zu :)
let $currentVariant := for $i in $variantList/functx:substring-before-match(functx:substring-after-match(text(), '\s+\('), '\)') return $i   (: liest die Variantenbezeichnung aus Element aus :)
return $currentVariant[1] (: eliminiert Dopplungen und schreibt Variante in den Listeneintrag :)
}    
</li>}
</ul>)
}</p>
}
</p>
</html>
