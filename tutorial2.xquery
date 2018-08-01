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
 
 
<xhtml xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:TEI="http://www.tei-c.org/ns/1.0">
<head>
    <meta http-equiv="content-type" content="text/xhtml; char set=utf-8"/>
    <title>Writing materials - statistics</title>
</head>
    <h2>Writers and their writing materials</h2>
<p>{

let $path := "C:/Fausteditionen/transcript/agad_warszawa"    (: zu modifizierende Zeile für hardcode/softcode :)
let $fileCollection := for $file in collection(concat('file:///',$path,'?recurse=yes')) where $file//TEI:handNotes return $file
(: Liste mit allen handNote Elementen wird in Liste gespeichert :)
let $handNotes := $fileCollection[1]//TEI:handNote    (: zu modifizierende Zeile für hardcode/softcode :)
(: sammelt alle vorkommenden IDs der Schreiber aus den Elementen :)
let $wIDcollection := for $writerID in $handNotes/functx:substring-before-match(data(@xml:id), '_') return $writerID   

let $wIDs := for $wID in fn:distinct-values($wIDcollection) return $wID  (: eliminiert Dopplungen :) 
(: iteriert über Liste der Schreiber-IDs :)
for $currentWID in $wIDs     
order by $currentWID
return  

(: generiert einen <p/>-Block für jeden Schreiber mit Attributen Typ und Schreiber-ID :)
<p type="writer" wID="{$currentWID}">{
(: Liste mit allen Elementen, die sich auf den aktuellen Schreiber beziehen 
Lis:)
let $stylesOfCurrentWriter := for $eachStyle in $handNotes where $fileCollection[1]/functx:substring-before-match($eachStyle/data(@xml:id), '_') = $currentWID return $eachStyle   (: zu modifizierende Zeile für hardcode/softcode :)

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
let $styleList := for $eachStyle in $stylesOfCurrentWriter where $fileCollection/functx:substring-after-match($eachStyle/data(@xml:id), '_') = $currentSID return $eachStyle    (: zu modifizierende Zeile für hardcode/softcode :) 
(: liest die Stylebezeichnung aus Element aus :)
let $currentStyle := for $style in $styleList/functx:substring-before-match(functx:substring-after-match(text(), '\s+\('), '\)') return $style   
return 
($currentStyle,

(: sammelt Dateien, in denen auf die aktuelle Writer-Style Kombination gewechselt wird :)
let $fileList := for $file in $fileCollection where exists($file//*[@new|@hand = concat("#",$currentWID,"_",$currentSID)]) return $file

(: Dateipfade werden so weit abgeschnitten, wie das Quellverzeichnis zu Beginn angegeben wurde :)
let $fileNames := for $fileName in $fileList return functx:substring-after-last($fileName//fn:document-uri(), $path)
return
if (count($fileList)>0) (:prüft ob dieser style in einem file des repos gefunden wurde :)
then (<details><summary><div><i>Found in {count($fileList)} file{if (count($fileList)>1) then "s" else ""}</i></div></summary>
<ol>{for $file in fn:distinct-values($fileNames) order by $file return <li type="file">{$file}</li>}</ol></details>,
<div>{ 

let $relevantNodes := for $anyNode in $fileList//* order by $anyNode return 
    if ($anyNode[@new]) then (name($anyNode), concat("handShift in ", name($anyNode/ancestor::*[1])))
    else if ($anyNode[@hand]) then name($anyNode)
    else ""
let $relevantNames := distinct-values($relevantNodes)
for $name in $relevantNames return if ($name>"") then <ul>{<li>{$name}: {count(for $node in $relevantNodes where $node=$name return $node)}</li>}</ul> else ""
    
        }</div>   )
      else "" )       




}
</li>
}
</ul>)
}
</p>
}
</p>
</xhtml>
