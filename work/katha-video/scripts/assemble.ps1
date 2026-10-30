$episode = Join-Path $PSScriptRoot "..\01-bhilni-fruit"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..\.."))
.\.venv\Scripts\python.exe -m katha_video.cli assemble $episode
.\.venv\Scripts\python.exe -m katha_video.cli qc $episode
