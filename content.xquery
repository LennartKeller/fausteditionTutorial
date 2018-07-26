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
declare function functx:escape-for-regex
  ( $arg as xs:string? )  as xs:string {

   replace($arg,
           '(\.|\[|\]|\\|\||\-|\^|\$|\?|\*|\+|\{|\}|\(|\))','\\$1')
 } ; 
declare function functx:substring-after-last
  ( $arg as xs:string? ,
    $delim as xs:string )  as xs:string {

   replace ($arg,concat('^.*',functx:escape-for-regex($delim)),'')
 } ;
 declare function functx:is-value-in-sequence
  ( $value as xs:anyAtomicType? ,
    $seq as xs:anyAtomicType* )  as xs:boolean {

   $value = $seq
 } ;

<html xmlns="http://www.tei-c.org/ns/1.0" 
  xmlns:TEI="http://www.tei-c.org/ns/1.0">
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Writer/Styles</title></head>
    <h2>Writer: Styles</h2>
<p>
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $repository := "C:/Fausteditionen/transcript/agad_warszawa"
let $data := collection(concat('file:///',$repository,'?recurse=yes')) 
(: zu modifizierende Zeile für hardcode/softcode :)
let $list := $data[1]//handNote     (: Liste mit allen handNote Elementen wird in $list gespeichert :)
let $wIDcollection := for $i in $list/functx:substring-before-match(data(@xml:id), '_') return $i   (: sammelt alle vorkommenden IDs der Schreiber aus den Elementen :)
let $wIDlist := for $i in fn:distinct-values($wIDcollection) return $i  (: eliminiert Dopplungen :) 
for $currentWID in $wIDlist     (: iteriert über Liste der Schreiber-IDs :)
order by $currentWID
return  
(: generiert einen <p/>-Block für jeden Schreiber mit Attributen Typ und Schreiber-ID :)
<p type="writer" wID="{$currentWID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $writerList := for $i in $list where $data[1]/functx:substring-before-match($i/data(@xml:id), '_')=$currentWID return $i    (: Liste mit allen Elementen, die sich auf den aktuellen Schreiber beziehen :)
let $currentWriter := for $i in $writerList/functx:substring-before-match(text(), '\s\(') return $i     (: Liste mit den Schreibernamen aus allen relevanten Elementen :)
let $writer := for $i in fn:distinct-values($currentWriter) return $i      (: eliminiert Dopplungen :)
return 
(<h4>{$writer}</h4>,
<ul>{
let $sIDcollection := for $i in $writerList/functx:substring-after-match(data(@xml:id), '_') return $i (: (: sammelt alle vorkommenden IDs der Styles aus den aktuell relevanten Elementen :) :)
for $currentSID in $sIDcollection   (: iteriert über Liste der Style-IDs :)
order by $currentSID
return
(: generiert einen Listeneintrag für jeden Style mit Attributen Typ und Style-ID :) 
<li type="style" vID="{$currentSID}">  
{
(: zu modifizierende Zeile für hardcode/softcode :)
let $styleList := for $i in $list where $data[1]/functx:substring-after-match($i/data(@xml:id), '_')=$currentSID return $i    (: ordnet Elemente der aktuellen Style ID zu :)
let $currentStyle := for $i in $styleList/functx:substring-before-match(functx:substring-after-match(text(), '\s+\('), '\)') return $i   (: liest die Stylebezeichnung aus Element aus :)
(: sammelt Dateien, in denen auf die aktuelle Writer-Style Kombination gewechselt wird :)
let $dataList := for $i in $data where exists($i//element()[@new=concat("#",$currentWID,"_",$currentSID)]) return $i
(: Dateipfade werden so weit abgeschnitten, wie das Quellverzeichnis zu Beginn angegeben wurde :)
let $fileList := for $i in $dataList return functx:substring-after-last($i//fn:document-uri(), $repository)
let $contentList := for $i in $dataList return $i//handShift/following::*/text()
return 
($currentStyle[1],
    if (count($dataList)>0) 
    then <ul>{for $i in fn:distinct-values($fileList) return <li type="file">{$i}
    <ul>{
    for $i in $contentList
    return <li>{$i}</li>}</ul>
    </li>}</ul>
    else "" )

    


}
</li>
}
</ul>)
}
</p>
}
</p>
</html>
(:
let $fileList := $data[//element()[@new=concat("#",$currentWID,"_",$currentVID)]]
let $output := "not found"
for $i in $fileList
where exists($i//fn:document-uri()) let $output := functx:substring-after-last($i//fn:document-uri(), $repository)
return <li>{$output}</li> :)
