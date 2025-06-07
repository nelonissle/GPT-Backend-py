{{- define "admin-service.fullname" -}}
{{ include "admin-service.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "admin-service.name" -}}
{{ .Chart.Name }}
{{- end }}