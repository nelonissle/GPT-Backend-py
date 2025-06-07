{{- define "kong.fullname" -}}
{{ include "kong.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "kong.name" -}}
{{ .Chart.Name }}
{{- end }}