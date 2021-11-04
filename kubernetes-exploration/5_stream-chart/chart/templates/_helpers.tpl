{{- define "chart.namePrefix" -}}
{{- default "trainingk8s" -}}
{{- end -}}

{{- define "chart.labels" -}}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end -}}
