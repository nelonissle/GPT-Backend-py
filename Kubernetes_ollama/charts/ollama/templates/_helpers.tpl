{{/* Chart “name” (used for labels & selectors) */}}
{{- define "ollama.name" -}}
{{- default .Chart.Name .Values.nameOverride -}}
{{- end -}}

{{/* Chart “fullname” (used for resource names) */}}
{{- define "ollama.fullname" -}}
{{- if .Values.fullnameOverride }}
  {{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
  {{- printf "%s-%s" .Release.Name (include "ollama.name" .) 
       | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end -}}

{{/* Standard set of labels for every resource */}}
{{- define "ollama.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "ollama.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
