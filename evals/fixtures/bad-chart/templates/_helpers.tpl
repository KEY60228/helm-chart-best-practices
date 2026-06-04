{{- define "fullname" -}}
{{- .Release.Name -}}-{{- .Chart.Name -}}
{{- end -}}

{{- define "labels" -}}
app: {{ .Chart.Name }}
version: {{ .Chart.AppVersion }}
{{- end -}}
