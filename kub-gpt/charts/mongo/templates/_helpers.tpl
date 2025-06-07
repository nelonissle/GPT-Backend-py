{{- define "mongo.fullname" -}}
{{ include "mongo.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "mongo.name" -}}
{{ .Chart.Name }}
{{- end }}