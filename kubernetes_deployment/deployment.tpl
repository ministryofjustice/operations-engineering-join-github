apiVersion: apps/v1
kind: Deployment
metadata:
  name: operations-engineering-landing-pages-poc
  namespace: operations-engineering-landing-pages-poc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: operations-engineering-landing-pages-poc-app
  template:
    metadata:
      labels:
        app: operations-engineering-landing-pages-poc-app
    spec:
      containers:
        - name: operations-engineering-landing-pages-poc
          image: 754256621582.dkr.ecr.eu-west-2.amazonaws.com/${ECR_NAME}:${IMAGE_TAG}
          env:
            - name: FLASK_DEBUG
              value: "true"   
          envFrom:
            - secretRef:
                name: app-secrets       
          ports:
          - containerPort: 4567