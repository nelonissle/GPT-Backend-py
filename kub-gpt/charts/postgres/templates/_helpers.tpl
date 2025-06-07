{{- define "postgres.fullname" -}}
{{ include "postgres.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "postgres.name" -}}
{{ .Chart.Name }}
{{- end }}