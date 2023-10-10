apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: operations-engineering-landing-page-poc
type: Opaque
data:
  APP_SECRET_KEY: ${FLASK_APP_SECRET}
