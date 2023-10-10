apiVersion: apps/v1
kind: Deployment
metadata:
  name: operations-engineering-landing-page-poc
  namespace: operations-engineering-landing-page-poc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: operations-engineering-landing-page-poc-app
  template:
    metadata:
      labels:
        app: operations-engineering-landing-page-poc-app
    spec:
      containers:
        - name: operations-engineering-landing-page-poc
          image: ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG}
          env:
            - name: FLASK_DEBUG
              value: "true"   
          envFrom:
            - secretRef:
                name: app-secrets       
          ports:
          - containerPort: 4567