{{- define "chat-service.fullname" -}}
{{ include "chat-service.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "chat-service.name" -}}
{{ .Chart.Name }}
{{- end }}